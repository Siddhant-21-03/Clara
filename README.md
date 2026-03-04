# Clara Answers — Onboarding Automation Pipeline

Takes messy demo and onboarding call transcripts and turns them into configured Retell AI voice agents. Zero cost — no paid APIs, no LLM calls, just regex extraction and templating.

## How it works

There are two phases:

1. **Pipeline A** — Feed in a demo call transcript, get a v1 agent config. These are intentionally incomplete since demo calls are exploratory and don't cover everything. Missing info gets flagged, not made up.

2. **Pipeline B** — Feed in the onboarding call for the same account, and the pipeline diffs it against v1, merges the new data, and produces a v2 with a full changelog.

Both phases run on all 10 transcripts (5 demo + 5 onboarding) in about a second.

```
Transcript → Regex extraction → Account Memo (JSON) → Prompt generator → Retell Agent Spec + System Prompt
                                                                              ↓
                                                         Stored as v1/ or v2/ with changelog
```

The extraction is rule-based — about 50 regex patterns in `extractor.py` that pull out company names, business hours, phone numbers, emergency definitions, routing chains, etc. No GPT, no Claude, no API costs. The tradeoff is that weird phrasing can trip it up, but for well-structured transcripts it gets ~80-90% accuracy, and the onboarding phase fills in whatever the demo missed.

## Quick start

**Easiest way:** double-click `run_demo.bat` (Windows) or `./run_demo.sh` (Mac/Linux). It installs deps, runs the pipeline, and opens the dashboard.

**Manual:**

```bash
pip install -r requirements.txt
cd scripts
python pipeline.py --mode all --clean
cd ../dashboard
python app.py
# open http://localhost:5000
```

You need Python 3.10+ and pip. That's it.

## What to look at

Once it's run, the interesting stuff:

- **`outputs/accounts/ACC-001/v2/system_prompt.md`** — open this first. It's a complete voice agent prompt with business-hours flow, after-hours flow, emergency routing chain, transfer protocol, the works.

- **`outputs/accounts/ACC-005/changes.md`** — Summit Facility Maintenance, the most complex account. Multi-trade routing (separate on-call numbers for plumbing, HVAC, electrical, elevator), 15 field-level changes from v1 to v2.

- **The dashboard** at `http://localhost:5000` — click any account to see the diff between v1 and v2. The v1 memos have `null` for phone numbers and greetings; v2 fills them in from onboarding.

- **`/try` page** on the dashboard — paste in any transcript and watch it extract data + generate an agent spec in real time.

## Architecture

```
scripts/
  config.py              — keywords, patterns, timezone mappings
  extractor.py           — the regex extraction engine (~900 lines, this is where the work is)
  prompt_generator.py    — takes a memo and builds a Retell agent spec + system prompt
  version_manager.py     — diffs v1 vs v2, generates changelogs
  pipeline.py            — orchestrates everything, CLI interface
```

The pipeline reads transcripts from `data/`, extracts structured data, generates agent configs, and writes everything to `outputs/accounts/ACC-XXX/v1/` and `v2/`. Each account also gets `changes.json` (machine-readable) and `changes.md` (human-readable).

The dashboard is a small Flask app that reads the output JSON files and renders them. Nothing fancy — just a way to browse results without opening JSON files manually.

## File structure

```
├── data/
│   ├── demo_transcripts/          # 5 demo call transcripts
│   └── onboarding_transcripts/    # 5 matching onboarding transcripts
├── scripts/                       # core pipeline code (5 modules)
├── outputs/
│   └── accounts/
│       ├── ACC-001/ through ACC-005/
│       │   ├── v1/                # account_memo.json, agent_spec.json, system_prompt.md
│       │   ├── v2/                # same files, updated from onboarding
│       │   ├── changes.json
│       │   └── changes.md
│       └── pipeline_summary.json
├── changelog/
│   └── global_changelog.md
├── tasks/
│   └── task_log.json
├── workflows/
│   └── clara_pipeline_n8n.json    # n8n workflow export
├── dashboard/
│   ├── app.py
│   └── templates/                 # index, account detail, try-your-own page
├── schemas/                       # JSON schemas for memo + agent spec
├── docker-compose.yml             # n8n + dashboard containers
├── run_demo.bat / run_demo.sh     # one-click demo scripts
└── README.md
```

## Output format

**Account Memo** — structured JSON per account with: `account_id`, `company_name`, `business_hours`, `office_address`, `services_supported`, `emergency_definition`, `emergency_routing_rules`, `non_emergency_routing_rules`, `call_transfer_rules`, `integration_constraints`, `after_hours_flow_summary`, `office_hours_flow_summary`, `questions_or_unknowns`, `notes`. If something isn't in the transcript, it's `null` or flagged as unknown — never fabricated.

**Agent Spec** — JSON with: `agent_name`, `voice_style`, `system_prompt` (the big one — full conversation flow), `key_variables`, `tool_invocations` (backend only, never mentioned to caller), `call_transfer_protocol`, `fallback_protocol`, `version`.

**Changelog** — per-account `changes.json` and `changes.md` showing field-level diffs between v1 and v2, with old/new values and reasons.

## Running the pipeline

```bash
# full run — processes all 10 transcripts
python scripts/pipeline.py --mode all --clean

# just demo transcripts
python scripts/pipeline.py --mode demo

# just onboarding (needs v1 to exist already)
python scripts/pipeline.py --mode onboarding

# single file
python scripts/pipeline.py --mode single --file data/demo_transcripts/demo_001_fireshield.txt --type demo
```

The `--clean` flag wipes outputs before running. Without it, existing accounts are skipped (idempotent).

## n8n setup

```bash
docker-compose up -d n8n
# → http://localhost:5678 (login: clara / clara2026)
```

Import `workflows/clara_pipeline_n8n.json`, configure env vars, hit Execute. The workflow calls the same Python pipeline under the hood.

## Retell setup

Retell's free tier doesn't support programmatic agent creation, so the pipeline outputs JSON specs that you'd paste into Retell manually:

1. Create a Retell account at [retell.ai](https://www.retell.ai/)
2. Create an agent, name it per the spec (e.g. "Clara - FireShield Protection Services")
3. Copy the system prompt from `outputs/accounts/ACC-XXX/v2/system_prompt.md`
4. Set up transfer numbers from `call_transfer_protocol.transfer_targets` in the agent spec

If Retell opens up free API access, there's a code snippet in the agent spec showing how you'd create agents programmatically.

## Plugging in your own data

Name your files like this:

```
data/demo_transcripts/demo_001_yourcompany.txt
data/onboarding_transcripts/onboarding_001_yourcompany.txt
```

The `001` number links demo and onboarding to the same account. Then `python scripts/pipeline.py --mode all --clean`.

For audio files, transcribe locally with Whisper first:

```bash
pip install openai-whisper
whisper recording.wav --output_format txt --output_dir data/demo_transcripts/
```

## Known limitations

- **Regex isn't perfect.** Unusual phrasing or ambiguous sentence structure can cause missed extractions. The onboarding phase usually catches what demo missed, but edge cases exist.

- **Phone number attribution** gets tricky when multiple numbers appear in the same paragraph. The extractor uses proximity heuristics — works most of the time, but can misattribute in dense sections.

- **ACC-005 (Summit)** has trade-specific routing (different on-call numbers for plumbing, HVAC, electrical). The pipeline handles it, but it took specific pattern matching for "For [trade]: call..." constructions. Other multi-trade formats might need tuning.

- **No live Retell integration.** Zero-cost constraint means we output specs for manual import. The code is structured so you'd just need to drop in an API key.

- **Dashboard is read-only.** Shows results after the pipeline runs, doesn't stream progress.

## What I'd do with production access

Swap the regex extractor for LLM-powered extraction (probably Claude or GPT-4) — that alone would take accuracy from ~85% to 99%+. Add Deepgram or Whisper API for automatic transcription so the pipeline can ingest audio directly. Use the Retell API to create and update agents programmatically instead of manual copy-paste. Move storage from local JSON to Postgres or Supabase. Hook up Asana for real task tracking instead of the JSON log. Add Sentry for error monitoring and a CI pipeline.

The architecture already supports this — the extractor is a single swappable module, storage is abstracted through the version manager, and the prompt generator doesn't care where its input comes from.
