#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_PHASE_FIELDS = {
    "jira_id",
    "phase_id",
    "phase_name",
    "task_type",
    "workspace_root",
    "repos",
    "artifacts",
    "scope_lock",
    "stop_conditions",
    "acceptance_checks",
    "verified",
    "violations",
    "required_checks_passed",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal phase artifact verifier")
    parser.add_argument("phase_json", help="Path to phase.json")
    args = parser.parse_args()

    phase_json_path = Path(args.phase_json).resolve()
    if not phase_json_path.exists():
        print(f"ERROR: phase.json not found: {phase_json_path}")
        return 1

    with open(phase_json_path, "r", encoding="utf-8") as f:
        phase = json.load(f)

    missing = sorted(REQUIRED_PHASE_FIELDS - set(phase.keys()))
    if missing:
        print(f"ERROR: Missing required fields: {', '.join(missing)}")
        return 1

    artifacts = phase.get("artifacts", {})
    required_artifacts = ["runbook_md", "files_json", "commands_sh", "commands_ps1", "report_md"]

    for artifact_key in required_artifacts:
        artifact_path = artifacts.get(artifact_key)
        if not artifact_path:
            print(f"ERROR: Missing artifact path: {artifact_key}")
            return 1
        if not Path(artifact_path).exists():
            print(f"ERROR: Artifact does not exist: {artifact_key} -> {artifact_path}")
            return 1

    print("OK: Phase artifacts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
