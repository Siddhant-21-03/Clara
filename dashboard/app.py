"""
Clara Answers - Web Dashboard
==============================
Simple Flask web dashboard to view accounts, diffs, agent specs, and pipeline status.
"""

import json
import os
import sys
from datetime import datetime

# Add parent dir for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import tempfile
import time
from flask import Flask, render_template, jsonify, send_from_directory, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs", "accounts")
CHANGELOG_DIR = os.path.join(BASE_DIR, "changelog")
TASKS_DIR = os.path.join(BASE_DIR, "tasks")
DATA_DIR = os.path.join(BASE_DIR, "data")
DEMO_DIR = os.path.join(DATA_DIR, "demo_transcripts")
ONBOARDING_DIR = os.path.join(DATA_DIR, "onboarding_transcripts")

# Pipeline is imported lazily in the /api/process route
# to avoid issues with Flask's debug reloader


def load_json_file(path):
    """Safely load a JSON file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def load_text_file(path):
    """Safely load a text file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return None


def get_accounts():
    """Get all account data."""
    accounts = []
    if not os.path.exists(OUTPUTS_DIR):
        return accounts

    for account_id in sorted(os.listdir(OUTPUTS_DIR)):
        account_dir = os.path.join(OUTPUTS_DIR, account_id)
        if not os.path.isdir(account_dir) or account_id.startswith('.'):
            continue

        account = {"account_id": account_id, "versions": {}}

        for version in ["v1", "v2"]:
            version_dir = os.path.join(account_dir, version)
            if os.path.exists(version_dir):
                memo = load_json_file(os.path.join(version_dir, "account_memo.json"))
                spec = load_json_file(os.path.join(version_dir, "agent_spec.json"))
                prompt = load_text_file(os.path.join(version_dir, "system_prompt.md"))

                account["versions"][version] = {
                    "memo": memo,
                    "spec": spec,
                    "prompt": prompt
                }

                if memo:
                    account["company_name"] = memo.get("company_name", "Unknown")
                    account["services"] = memo.get("services_supported", [])

        # Load changelog
        changes = load_json_file(os.path.join(account_dir, "changes.json"))
        account["changes"] = changes
        changes_md = load_text_file(os.path.join(account_dir, "changes.md"))
        account["changes_md"] = changes_md

        accounts.append(account)

    return accounts


@app.route('/')
def index():
    """Dashboard home page."""
    accounts = get_accounts()
    summary = load_json_file(os.path.join(OUTPUTS_DIR, "pipeline_summary.json"))
    tasks = load_json_file(os.path.join(TASKS_DIR, "task_log.json")) or []
    return render_template('index.html', accounts=accounts, summary=summary, tasks=tasks)


@app.route('/account/<account_id>')
def account_detail(account_id):
    """Account detail page with v1/v2 comparison."""
    accounts = get_accounts()
    account = next((a for a in accounts if a["account_id"] == account_id), None)
    if not account:
        return "Account not found", 404
    return render_template('account.html', account=account)


@app.route('/api/accounts')
def api_accounts():
    """API endpoint for accounts."""
    accounts = get_accounts()
    return jsonify(accounts)


@app.route('/api/account/<account_id>')
def api_account(account_id):
    """API endpoint for single account."""
    accounts = get_accounts()
    account = next((a for a in accounts if a["account_id"] == account_id), None)
    if not account:
        return jsonify({"error": "Not found"}), 404
    return jsonify(account)


@app.route('/api/summary')
def api_summary():
    """API endpoint for pipeline summary."""
    summary = load_json_file(os.path.join(OUTPUTS_DIR, "pipeline_summary.json"))
    return jsonify(summary or {})


@app.route('/try')
def try_transcript():
    """Try your own transcript page."""
    samples = []
    # Load available sample transcripts
    if os.path.exists(DEMO_DIR):
        for f in sorted(os.listdir(DEMO_DIR)):
            if f.endswith('.txt'):
                name = f.replace('demo_', '').replace('.txt', '').replace('_', ' ').title()
                samples.append({"file": f, "type": "demo", "label": f"Demo: {name}"})
    if os.path.exists(ONBOARDING_DIR):
        for f in sorted(os.listdir(ONBOARDING_DIR)):
            if f.endswith('.txt'):
                name = f.replace('onboarding_', '').replace('.txt', '').replace('_', ' ').title()
                samples.append({"file": f, "type": "onboarding", "label": f"Onboarding: {name}"})
    return render_template('try.html', samples=samples)


@app.route('/api/sample/<filename>')
def api_sample(filename):
    """Return the content of a sample transcript."""
    # Security: only allow loading from known directories
    for d in [DEMO_DIR, ONBOARDING_DIR]:
        path = os.path.join(d, filename)
        if os.path.exists(path):
            return jsonify({"content": load_text_file(path)})
    return jsonify({"error": "Sample not found"}), 404


@app.route('/api/process', methods=['POST'])
def api_process():
    """Process a user-submitted transcript through the pipeline."""
    data = request.get_json()
    if not data or 'transcript' not in data:
        return jsonify({"error": "Missing 'transcript' in request body"}), 400

    transcript_text = data['transcript'].strip()
    transcript_type = data.get('type', 'demo')  # 'demo' or 'onboarding'

    if len(transcript_text) < 50:
        return jsonify({"error": "Transcript too short — need at least a few exchanges"}), 400

    if transcript_type not in ('demo', 'onboarding'):
        return jsonify({"error": "Type must be 'demo' or 'onboarding'"}), 400

    try:
        start = time.time()
        from pipeline import ClaraPipeline
        pipeline = ClaraPipeline()

        # Write transcript to a temp file (pipeline expects file paths)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False,
                                          dir=os.path.join(BASE_DIR, "data"),
                                          encoding='utf-8') as tmp:
            tmp.write(transcript_text)
            tmp_path = tmp.name

        try:
            if transcript_type == 'demo':
                result = pipeline.process_demo_transcript(tmp_path)
            else:
                result = pipeline.process_onboarding_transcript(tmp_path)
        finally:
            # Clean up temp file
            os.unlink(tmp_path)

        duration = round(time.time() - start, 2)

        # Load the generated artifacts to return them
        account_id = result['account_id']
        version = result['version']
        version_dir = os.path.join(OUTPUTS_DIR, account_id, version)

        memo = load_json_file(os.path.join(version_dir, "account_memo.json"))
        spec = load_json_file(os.path.join(version_dir, "agent_spec.json"))
        prompt = load_text_file(os.path.join(version_dir, "system_prompt.md"))

        response = {
            "account_id": account_id,
            "company_name": result.get("company_name"),
            "version": version,
            "confidence": result.get("confidence"),
            "unknowns": result.get("unknowns", []),
            "duration": duration,
            "memo": memo,
            "agent_spec": spec,
            "system_prompt": prompt,
        }

        # If this was an onboarding run, include changes
        if version == "v2":
            changes = load_json_file(os.path.join(OUTPUTS_DIR, account_id, "changes.json"))
            response["changes"] = changes
            response["changes_count"] = result.get("changes_count", 0)

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
