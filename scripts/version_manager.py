"""
Clara Answers - Version Manager
================================
Handles v1 -> v2 updates, diffing, and changelog generation.
Merges onboarding data with existing demo-derived account memos.
"""

import json
import os
import copy
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

import logging

logger = logging.getLogger(__name__)


class VersionManager:
    """Manages versioning, diffing, and changelog for account configurations."""

    def __init__(self, outputs_dir: str):
        self.outputs_dir = outputs_dir

    def get_account_dir(self, account_id: str) -> str:
        """Get the directory for a specific account."""
        return os.path.join(self.outputs_dir, account_id)

    def save_v1(self, account_id: str, memo: Dict, agent_spec: Dict) -> str:
        """Save v1 artifacts (from demo call)."""
        account_dir = self.get_account_dir(account_id)
        v1_dir = os.path.join(account_dir, "v1")
        os.makedirs(v1_dir, exist_ok=True)

        memo["account_id"] = account_id
        memo["version"] = "v1"
        agent_spec["account_id"] = account_id
        agent_spec["version"] = "v1"

        # Save memo
        memo_path = os.path.join(v1_dir, "account_memo.json")
        with open(memo_path, 'w', encoding='utf-8') as f:
            json.dump(memo, f, indent=2, ensure_ascii=False)

        # Save agent spec
        spec_path = os.path.join(v1_dir, "agent_spec.json")
        with open(spec_path, 'w', encoding='utf-8') as f:
            json.dump(agent_spec, f, indent=2, ensure_ascii=False)

        # Save prompt separately for easy reading
        prompt_path = os.path.join(v1_dir, "system_prompt.md")
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(f"# System Prompt - {memo.get('company_name', 'Unknown')} (v1)\n\n")
            f.write(agent_spec.get("system_prompt", ""))

        logger.info(f"Saved v1 for {account_id} at {v1_dir}")
        return v1_dir

    def load_v1(self, account_id: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """Load existing v1 memo and agent spec."""
        v1_dir = os.path.join(self.get_account_dir(account_id), "v1")

        memo = None
        spec = None

        memo_path = os.path.join(v1_dir, "account_memo.json")
        if os.path.exists(memo_path):
            with open(memo_path, 'r', encoding='utf-8') as f:
                memo = json.load(f)

        spec_path = os.path.join(v1_dir, "agent_spec.json")
        if os.path.exists(spec_path):
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec = json.load(f)

        return memo, spec

    def apply_update(self, account_id: str, onboarding_memo: Dict) -> Tuple[Dict, List[Dict]]:
        """
        Apply onboarding data to existing v1 memo to produce v2.
        Returns (v2_memo, list_of_changes).
        """
        v1_memo, _ = self.load_v1(account_id)
        if v1_memo is None:
            logger.warning(f"No v1 found for {account_id}, treating onboarding as v1")
            onboarding_memo["version"] = "v1"
            return onboarding_memo, []

        v2_memo = copy.deepcopy(v1_memo)
        changes = []

        # Update each field from onboarding data, tracking changes
        fields_to_merge = [
            "company_name", "business_hours", "office_address",
            "services_supported", "emergency_definition",
            "emergency_routing_rules", "non_emergency_routing_rules",
            "call_transfer_rules", "integration_constraints",
            "after_hours_flow_summary", "office_hours_flow_summary",
            "special_rules", "greeting", "business_hours_routing",
            "notes"
        ]

        for field in fields_to_merge:
            old_value = v1_memo.get(field)
            new_value = onboarding_memo.get(field)

            if new_value is None:
                continue  # No update for this field

            if self._values_differ(old_value, new_value):
                # Check if onboarding data is more complete
                if self._is_better_data(old_value, new_value):
                    v2_memo[field] = new_value
                    changes.append({
                        "field": field,
                        "action": "updated",
                        "old_value": self._summarize_value(old_value),
                        "new_value": self._summarize_value(new_value),
                        "reason": "Onboarding provided confirmed/more detailed data"
                    })
                elif self._is_merge_needed(old_value, new_value):
                    merged = self._merge_values(old_value, new_value)
                    v2_memo[field] = merged
                    changes.append({
                        "field": field,
                        "action": "merged",
                        "old_value": self._summarize_value(old_value),
                        "new_value": self._summarize_value(merged),
                        "reason": "Merged onboarding data with existing demo data"
                    })

        # Update version and timestamps
        v2_memo["version"] = "v2"
        v2_memo["source"] = "onboarding_call"
        v2_memo["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"

        # Re-evaluate unknowns
        old_unknowns = v1_memo.get("questions_or_unknowns", [])
        new_unknowns = onboarding_memo.get("questions_or_unknowns", [])

        # Remove unknowns that were resolved
        resolved = [u for u in old_unknowns if u not in new_unknowns]
        if resolved:
            changes.append({
                "field": "questions_or_unknowns",
                "action": "resolved",
                "old_value": resolved,
                "new_value": new_unknowns,
                "reason": "Onboarding resolved previously unknown items"
            })

        v2_memo["questions_or_unknowns"] = new_unknowns

        return v2_memo, changes

    def save_v2(self, account_id: str, memo: Dict, agent_spec: Dict, changes: List[Dict]) -> str:
        """Save v2 artifacts and changelog."""
        account_dir = self.get_account_dir(account_id)
        v2_dir = os.path.join(account_dir, "v2")
        os.makedirs(v2_dir, exist_ok=True)

        memo["account_id"] = account_id
        memo["version"] = "v2"
        agent_spec["account_id"] = account_id
        agent_spec["version"] = "v2"

        # Save memo
        memo_path = os.path.join(v2_dir, "account_memo.json")
        with open(memo_path, 'w', encoding='utf-8') as f:
            json.dump(memo, f, indent=2, ensure_ascii=False)

        # Save agent spec
        spec_path = os.path.join(v2_dir, "agent_spec.json")
        with open(spec_path, 'w', encoding='utf-8') as f:
            json.dump(agent_spec, f, indent=2, ensure_ascii=False)

        # Save prompt separately
        prompt_path = os.path.join(v2_dir, "system_prompt.md")
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(f"# System Prompt - {memo.get('company_name', 'Unknown')} (v2)\n\n")
            f.write(agent_spec.get("system_prompt", ""))

        # Save changelog
        changelog_path = os.path.join(account_dir, "changes.json")
        changelog = {
            "account_id": account_id,
            "company_name": memo.get("company_name", "Unknown"),
            "updated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "version_from": "v1",
            "version_to": "v2",
            "total_changes": len(changes),
            "changes": changes
        }
        with open(changelog_path, 'w', encoding='utf-8') as f:
            json.dump(changelog, f, indent=2, ensure_ascii=False)

        # Also save human-readable changelog
        md_path = os.path.join(account_dir, "changes.md")
        self._write_changelog_md(md_path, changelog, memo)

        logger.info(f"Saved v2 for {account_id} with {len(changes)} changes")
        return v2_dir

    def _write_changelog_md(self, path: str, changelog: Dict, memo: Dict):
        """Write human-readable markdown changelog."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# Changelog: {changelog['company_name']}\n\n")
            f.write(f"**Account ID:** {changelog['account_id']}  \n")
            f.write(f"**Updated:** {changelog['updated_at']}  \n")
            f.write(f"**Version:** v1 → v2  \n")
            f.write(f"**Total Changes:** {changelog['total_changes']}  \n\n")
            f.write("---\n\n")

            for i, change in enumerate(changelog["changes"], 1):
                f.write(f"### Change {i}: `{change['field']}`\n\n")
                f.write(f"- **Action:** {change['action']}\n")
                f.write(f"- **Reason:** {change['reason']}\n")

                old = change.get('old_value')
                new = change.get('new_value')

                if old is not None:
                    f.write(f"- **Previous (v1):**\n")
                    if isinstance(old, (list, dict)):
                        f.write(f"  ```json\n  {json.dumps(old, indent=2)}\n  ```\n")
                    else:
                        f.write(f"  `{old}`\n")

                if new is not None:
                    f.write(f"- **Updated (v2):**\n")
                    if isinstance(new, (list, dict)):
                        f.write(f"  ```json\n  {json.dumps(new, indent=2)}\n  ```\n")
                    else:
                        f.write(f"  `{new}`\n")

                f.write("\n")

    def _values_differ(self, old: Any, new: Any) -> bool:
        """Check if two values are meaningfully different."""
        if old is None and new is not None:
            return True
        if isinstance(old, list) and isinstance(new, list):
            return set(str(x) for x in old) != set(str(x) for x in new)
        if isinstance(old, dict) and isinstance(new, dict):
            return json.dumps(old, sort_keys=True) != json.dumps(new, sort_keys=True)
        return str(old) != str(new)

    def _is_better_data(self, old: Any, new: Any) -> bool:
        """Check if new data is more complete than old."""
        if old is None:
            return True
        if isinstance(old, list) and isinstance(new, list):
            return len(new) >= len(old)
        if isinstance(old, dict) and isinstance(new, dict):
            old_filled = sum(1 for v in old.values() if v is not None and v != [] and v != "")
            new_filled = sum(1 for v in new.values() if v is not None and v != [] and v != "")
            return new_filled >= old_filled
        if isinstance(old, str) and isinstance(new, str):
            return len(new) >= len(old) or old in ["", "Not specified"]
        return True

    def _is_merge_needed(self, old: Any, new: Any) -> bool:
        """Check if values should be merged rather than replaced."""
        if isinstance(old, list) and isinstance(new, list):
            return len(set(str(x) for x in old) & set(str(x) for x in new)) < len(old)
        return False

    def _merge_values(self, old: Any, new: Any) -> Any:
        """Merge two values intelligently."""
        if isinstance(old, list) and isinstance(new, list):
            # Combine lists, dedup
            combined = list(old)
            for item in new:
                if item not in combined:
                    combined.append(item)
            return combined
        if isinstance(old, dict) and isinstance(new, dict):
            merged = copy.deepcopy(old)
            for key, value in new.items():
                if value is not None and value != "" and value != []:
                    merged[key] = value
            return merged
        return new

    def _summarize_value(self, value: Any) -> Any:
        """Create a summary of a value for changelog display."""
        if value is None:
            return "Not set"
        if isinstance(value, str) and len(value) > 200:
            return value[:200] + "..."
        if isinstance(value, list) and len(value) > 5:
            return value[:5] + [f"... and {len(value) - 5} more"]
        if isinstance(value, dict):
            # Summarize dict
            summary = {}
            for k, v in value.items():
                if v is not None and v != "" and v != []:
                    if isinstance(v, str) and len(v) > 100:
                        summary[k] = v[:100] + "..."
                    else:
                        summary[k] = v
            return summary
        return value

    def generate_global_changelog(self, changelog_dir: str) -> str:
        """Generate a global changelog across all accounts."""
        all_changes = []

        for account_id in os.listdir(self.outputs_dir):
            account_dir = os.path.join(self.outputs_dir, account_id)
            changes_file = os.path.join(account_dir, "changes.json")
            if os.path.exists(changes_file):
                with open(changes_file, 'r', encoding='utf-8') as f:
                    changes = json.load(f)
                    all_changes.append(changes)

        # Write global changelog
        global_path = os.path.join(changelog_dir, "global_changelog.md")
        with open(global_path, 'w', encoding='utf-8') as f:
            f.write("# Global Changelog - Clara Answers Pipeline\n\n")
            f.write(f"**Generated:** {datetime.now(timezone.utc).isoformat()}Z  \n")
            f.write(f"**Total Accounts Updated:** {len(all_changes)}  \n\n")
            f.write("---\n\n")

            for changes in all_changes:
                f.write(f"## {changes.get('company_name', 'Unknown')} ({changes['account_id']})\n\n")
                f.write(f"- **Changes:** {changes['total_changes']}\n")
                f.write(f"- **Updated:** {changes['updated_at']}\n\n")

                for change in changes["changes"]:
                    f.write(f"  - `{change['field']}`: {change['action']} — {change['reason']}\n")

                f.write("\n---\n\n")

        logger.info(f"Generated global changelog at {global_path}")
        return global_path
