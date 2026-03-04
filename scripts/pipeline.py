"""
Clara Answers - Main Orchestration Pipeline
=============================================
End-to-end automation pipeline that:
1. Ingests transcripts (demo or onboarding)
2. Extracts structured data
3. Generates Retell agent specs
4. Manages versioning (v1 -> v2)
5. Produces changelogs
6. Stores all artifacts

Usage:
    python pipeline.py --mode all          # Run full pipeline on all data
    python pipeline.py --mode demo         # Process only demo transcripts
    python pipeline.py --mode onboarding   # Process only onboarding transcripts
    python pipeline.py --mode single --file <path>  # Process single file
"""

import argparse
import json
import os
import sys
import re
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from config import (
    BASE_DIR, DATA_DIR, DEMO_TRANSCRIPTS_DIR, ONBOARDING_TRANSCRIPTS_DIR,
    OUTPUTS_DIR, CHANGELOG_DIR, LOGS_DIR, LOG_FORMAT, LOG_LEVEL,
    ACCOUNT_ID_PREFIX
)
from extractor import TranscriptExtractor
from prompt_generator import PromptGenerator
from version_manager import VersionManager

# Setup logging
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ClaraPipeline:
    """Main orchestration pipeline for Clara Answers onboarding automation."""

    def __init__(self):
        self.extractor = TranscriptExtractor()
        self.prompt_generator = PromptGenerator()
        self.version_manager = VersionManager(OUTPUTS_DIR)
        self.account_registry = self._load_registry()

    def _load_registry(self) -> Dict:
        """Load or create account registry mapping filenames to account IDs."""
        registry_path = os.path.join(OUTPUTS_DIR, "account_registry.json")
        if os.path.exists(registry_path):
            with open(registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"accounts": {}, "next_id": 1}

    def _save_registry(self):
        """Persist account registry."""
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        registry_path = os.path.join(OUTPUTS_DIR, "account_registry.json")
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.account_registry, f, indent=2)

    def _get_or_create_account_id(self, filename: str, company_name: Optional[str] = None) -> str:
        """Get existing account ID or create new one. Links demo/onboarding files by number."""
        # Extract the numeric part from filename (e.g., "001" from "demo_001_fireshield.txt")
        num_match = re.search(r'(\d{3})', filename)
        file_num = num_match.group(1) if num_match else None

        # Check if we have an existing account with this number
        if file_num:
            for key, info in self.account_registry["accounts"].items():
                key_num = re.search(r'(\d{3})', key)
                if key_num and key_num.group(1) == file_num:
                    return info["account_id"]

        # Check by company name
        if company_name:
            for key, info in self.account_registry["accounts"].items():
                if info.get("company_name", "").lower() == company_name.lower():
                    return info["account_id"]

        # Create new account ID
        account_id = f"{ACCOUNT_ID_PREFIX}-{self.account_registry['next_id']:03d}"
        self.account_registry["accounts"][filename] = {
            "account_id": account_id,
            "company_name": company_name,
            "created_at": datetime.now(timezone.utc).isoformat() + "Z"
        }
        self.account_registry["next_id"] += 1
        self._save_registry()

        return account_id

    def read_transcript(self, filepath: str) -> str:
        """Read a transcript file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def process_demo_transcript(self, filepath: str) -> Dict:
        """
        Pipeline A: Demo Call -> Preliminary Agent (v1)

        Steps:
        1. Read transcript
        2. Extract structured data
        3. Assign account ID
        4. Generate agent spec
        5. Save v1 artifacts
        """
        filename = os.path.basename(filepath)
        logger.info(f"{'='*60}")
        logger.info(f"PIPELINE A: Processing demo transcript: {filename}")
        logger.info(f"{'='*60}")

        # Step 1: Read
        transcript = self.read_transcript(filepath)
        logger.info(f"Read transcript: {len(transcript)} characters")

        # Step 2: Extract
        logger.info("Extracting structured data...")
        memo = self.extractor.extract_all(transcript, source="demo_call")
        memo["_source_file"] = filename
        logger.info(f"Extracted company: {memo.get('company_name')}")
        logger.info(f"Services found: {memo.get('services_supported')}")
        logger.info(f"Emergencies found: {len(memo.get('emergency_definition', []))}")
        logger.info(f"Unknowns: {len(memo.get('questions_or_unknowns', []))}")

        # Step 3: Assign account ID
        account_id = self._get_or_create_account_id(filename, memo.get("company_name"))
        memo["account_id"] = account_id
        logger.info(f"Account ID: {account_id}")

        # Step 4: Generate agent spec
        logger.info("Generating Retell agent spec...")
        agent_spec = self.prompt_generator.generate_agent_spec(memo)
        logger.info(f"Agent spec generated: {agent_spec['agent_name']}")
        logger.info(f"Confidence score: {agent_spec['metadata']['confidence_score']}")

        # Step 5: Save v1
        v1_dir = self.version_manager.save_v1(account_id, memo, agent_spec)
        logger.info(f"v1 saved at: {v1_dir}")

        # Create task tracking entry
        self._create_task_entry(account_id, memo, "v1")

        result = {
            "account_id": account_id,
            "company_name": memo.get("company_name"),
            "version": "v1",
            "output_dir": v1_dir,
            "confidence": agent_spec["metadata"]["confidence_score"],
            "unknowns": memo.get("questions_or_unknowns", []),
            "status": "success"
        }

        logger.info(f"Pipeline A complete for {account_id}")
        return result

    def process_onboarding_transcript(self, filepath: str) -> Dict:
        """
        Pipeline B: Onboarding -> Agent Modification (v1 -> v2)

        Steps:
        1. Read transcript
        2. Extract structured data
        3. Match to existing account
        4. Apply updates (diff/patch)
        5. Regenerate agent spec
        6. Save v2 with changelog
        """
        filename = os.path.basename(filepath)
        logger.info(f"{'='*60}")
        logger.info(f"PIPELINE B: Processing onboarding transcript: {filename}")
        logger.info(f"{'='*60}")

        # Step 1: Read
        transcript = self.read_transcript(filepath)
        logger.info(f"Read transcript: {len(transcript)} characters")

        # Step 2: Extract
        logger.info("Extracting structured data from onboarding...")
        onboarding_memo = self.extractor.extract_all(transcript, source="onboarding_call")
        onboarding_memo["_source_file"] = filename
        logger.info(f"Extracted company: {onboarding_memo.get('company_name')}")

        # Step 3: Match to existing account
        account_id = self._get_or_create_account_id(filename, onboarding_memo.get("company_name"))
        onboarding_memo["account_id"] = account_id
        logger.info(f"Matched to account: {account_id}")

        # Step 4: Apply updates
        logger.info("Applying onboarding updates to v1...")
        v2_memo, changes = self.version_manager.apply_update(account_id, onboarding_memo)
        logger.info(f"Changes detected: {len(changes)}")
        for change in changes:
            logger.info(f"  - {change['field']}: {change['action']} — {change['reason']}")

        # Step 5: Regenerate agent spec
        logger.info("Regenerating Retell agent spec for v2...")
        v2_agent_spec = self.prompt_generator.generate_agent_spec(v2_memo)
        logger.info(f"v2 agent spec generated: {v2_agent_spec['agent_name']}")

        # Step 6: Save v2 with changelog
        v2_dir = self.version_manager.save_v2(account_id, v2_memo, v2_agent_spec, changes)
        logger.info(f"v2 saved at: {v2_dir}")

        # Update task tracking
        self._create_task_entry(account_id, v2_memo, "v2")

        result = {
            "account_id": account_id,
            "company_name": v2_memo.get("company_name"),
            "version": "v2",
            "output_dir": v2_dir,
            "confidence": v2_agent_spec["metadata"]["confidence_score"],
            "changes_count": len(changes),
            "unknowns": v2_memo.get("questions_or_unknowns", []),
            "status": "success"
        }

        logger.info(f"Pipeline B complete for {account_id}")
        return result

    def _create_task_entry(self, account_id: str, memo: Dict, version: str):
        """Create a task tracking entry (local JSON-based task tracker)."""
        tasks_dir = os.path.join(BASE_DIR, "tasks")
        os.makedirs(tasks_dir, exist_ok=True)

        task = {
            "task_id": f"TASK-{account_id}-{version}",
            "account_id": account_id,
            "company_name": memo.get("company_name"),
            "version": version,
            "status": "completed",
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "description": f"{'Demo' if version == 'v1' else 'Onboarding'} processing complete for {memo.get('company_name')}",
            "unknowns_count": len(memo.get("questions_or_unknowns", [])),
            "unknowns": memo.get("questions_or_unknowns", [])
        }

        tasks_file = os.path.join(tasks_dir, "task_log.json")
        tasks = []
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)

        # Remove duplicate task entries (idempotent)
        tasks = [t for t in tasks if t["task_id"] != task["task_id"]]
        tasks.append(task)

        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)

    def run_all_demos(self) -> List[Dict]:
        """Process all demo transcripts (Pipeline A)."""
        results = []
        demo_dir = DEMO_TRANSCRIPTS_DIR

        if not os.path.exists(demo_dir):
            logger.error(f"Demo transcripts directory not found: {demo_dir}")
            return results

        files = sorted([f for f in os.listdir(demo_dir) if f.endswith('.txt')])
        logger.info(f"Found {len(files)} demo transcripts")

        for filename in files:
            filepath = os.path.join(demo_dir, filename)
            try:
                result = self.process_demo_transcript(filepath)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {filename}: {e}", exc_info=True)
                results.append({
                    "file": filename,
                    "status": "error",
                    "error": str(e)
                })

        return results

    def run_all_onboarding(self) -> List[Dict]:
        """Process all onboarding transcripts (Pipeline B)."""
        results = []
        onboarding_dir = ONBOARDING_TRANSCRIPTS_DIR

        if not os.path.exists(onboarding_dir):
            logger.error(f"Onboarding transcripts directory not found: {onboarding_dir}")
            return results

        files = sorted([f for f in os.listdir(onboarding_dir) if f.endswith('.txt')])
        logger.info(f"Found {len(files)} onboarding transcripts")

        for filename in files:
            filepath = os.path.join(onboarding_dir, filename)
            try:
                result = self.process_onboarding_transcript(filepath)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {filename}: {e}", exc_info=True)
                results.append({
                    "file": filename,
                    "status": "error",
                    "error": str(e)
                })

        return results

    def run_full_pipeline(self) -> Dict:
        """Run the complete pipeline: all demos then all onboarding."""
        logger.info("=" * 70)
        logger.info("STARTING FULL CLARA PIPELINE")
        logger.info("=" * 70)
        start_time = datetime.now(timezone.utc)

        # Phase 1: Process all demo transcripts
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 1: Processing Demo Transcripts (Pipeline A)")
        logger.info("=" * 70)
        demo_results = self.run_all_demos()

        # Phase 2: Process all onboarding transcripts
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 2: Processing Onboarding Transcripts (Pipeline B)")
        logger.info("=" * 70)
        onboarding_results = self.run_all_onboarding()

        # Phase 3: Generate global changelog
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 3: Generating Global Changelog")
        logger.info("=" * 70)
        os.makedirs(CHANGELOG_DIR, exist_ok=True)
        self.version_manager.generate_global_changelog(CHANGELOG_DIR)

        # Phase 4: Generate summary report
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        summary = {
            "pipeline_run": {
                "started_at": start_time.isoformat() + "Z",
                "completed_at": end_time.isoformat() + "Z",
                "duration_seconds": round(duration, 2)
            },
            "demo_results": {
                "total": len(demo_results),
                "success": sum(1 for r in demo_results if r.get("status") == "success"),
                "errors": sum(1 for r in demo_results if r.get("status") == "error"),
                "accounts": demo_results
            },
            "onboarding_results": {
                "total": len(onboarding_results),
                "success": sum(1 for r in onboarding_results if r.get("status") == "success"),
                "errors": sum(1 for r in onboarding_results if r.get("status") == "error"),
                "accounts": onboarding_results
            }
        }

        # Save summary
        summary_path = os.path.join(OUTPUTS_DIR, "pipeline_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        self._print_summary(summary)

        return summary

    def _print_summary(self, summary: Dict):
        """Print a formatted summary to console."""
        print("\n" + "=" * 70)
        print("PIPELINE EXECUTION SUMMARY")
        print("=" * 70)
        print(f"Duration: {summary['pipeline_run']['duration_seconds']}s")
        print(f"\nDemo Processing (Pipeline A):")
        print(f"  Total: {summary['demo_results']['total']}")
        print(f"  Success: {summary['demo_results']['success']}")
        print(f"  Errors: {summary['demo_results']['errors']}")

        print(f"\nOnboarding Processing (Pipeline B):")
        print(f"  Total: {summary['onboarding_results']['total']}")
        print(f"  Success: {summary['onboarding_results']['success']}")
        print(f"  Errors: {summary['onboarding_results']['errors']}")

        print(f"\nAccounts processed:")
        for result in summary['demo_results']['accounts']:
            if result.get('status') == 'success':
                print(f"  {result['account_id']}: {result['company_name']} "
                      f"(confidence: {result['confidence']}, unknowns: {len(result.get('unknowns', []))})")

        print(f"\nOutputs saved to: {OUTPUTS_DIR}")
        print(f"Changelog saved to: {CHANGELOG_DIR}")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Clara Answers Onboarding Automation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py --mode all              Run full pipeline
  python pipeline.py --mode demo             Process demo transcripts only
  python pipeline.py --mode onboarding       Process onboarding transcripts only
  python pipeline.py --mode single --file path/to/transcript.txt --type demo
        """
    )
    parser.add_argument('--mode', choices=['all', 'demo', 'onboarding', 'single'],
                        default='all', help='Pipeline mode')
    parser.add_argument('--file', type=str, help='Path to single transcript (for single mode)')
    parser.add_argument('--type', choices=['demo', 'onboarding'],
                        help='Transcript type (for single mode)')
    parser.add_argument('--clean', action='store_true',
                        help='Clean outputs before running')

    args = parser.parse_args()

    pipeline = ClaraPipeline()

    if args.clean:
        import shutil
        if os.path.exists(OUTPUTS_DIR):
            shutil.rmtree(OUTPUTS_DIR)
            logger.info("Cleaned outputs directory")

    if args.mode == 'all':
        pipeline.run_full_pipeline()
    elif args.mode == 'demo':
        pipeline.run_all_demos()
    elif args.mode == 'onboarding':
        pipeline.run_all_onboarding()
    elif args.mode == 'single':
        if not args.file or not args.type:
            parser.error("--file and --type required for single mode")
        if args.type == 'demo':
            pipeline.process_demo_transcript(args.file)
        else:
            pipeline.process_onboarding_transcript(args.file)


if __name__ == "__main__":
    main()
