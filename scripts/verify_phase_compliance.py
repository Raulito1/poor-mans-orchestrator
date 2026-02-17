#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

REQUIRED_REPORT_HEADINGS = [
    "## Summary",
    "## Files Touched",
    "## Command Results",
    "## Acceptance Checks",
    "## Blockers / Next Steps",
]

OUTCOME_PATTERN = re.compile(r"\b(PASS|FAIL|BLOCKED)\b")
EXIT_PATTERN = re.compile(r"\[EXIT\]\s+([^\s]+)\s+->\s+(-?\d+)")
COMMAND_PATTERN = re.compile(r"^run_cmd\s+(\S+)\s+(true|false)\s+", re.MULTILINE)


def _load_json(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _list_changed_files(workspace: Path, repos: List[Dict[str, object]]) -> List[str]:
    changed: set[str] = set()
    for repo in repos:
        rel_repo_path = str(repo.get("path", "."))
        repo_path = workspace if rel_repo_path == "." else workspace / rel_repo_path
        if not (repo_path / ".git").exists():
            continue
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_path),
            text=True,
            capture_output=True,
            check=False,
        )
        for line in proc.stdout.splitlines():
            if not line:
                continue
            candidate = line[3:]
            if " -> " in candidate:
                candidate = candidate.split(" -> ", 1)[1]
            full = Path(candidate)
            if full.is_absolute():
                continue
            if rel_repo_path == ".":
                changed.add(full.as_posix())
            else:
                changed.add((Path(rel_repo_path) / full).as_posix())
    return sorted(changed)


def _allowlist_match(path: str, allowlist: List[Dict[str, str]]) -> bool:
    for entry in allowlist:
        entry_path = entry.get("path", "")
        kind = entry.get("kind", "glob")
        if kind == "file" and path == entry_path:
            return True
        if kind == "glob" and fnmatch.fnmatch(path, entry_path):
            return True
    return False


def _parse_required_commands(commands_sh: Path) -> List[str]:
    text = commands_sh.read_text(encoding="utf-8")
    required: List[str] = []
    for cmd_id, required_flag in COMMAND_PATTERN.findall(text):
        if required_flag == "true":
            required.append(cmd_id.strip("'\""))
    return required


def _check_command_logs(logs_dir: Path, required_ids: List[str]) -> Tuple[List[str], List[str]]:
    violations: List[str] = []
    evidence: List[str] = []
    for command_id in required_ids:
        log_file = logs_dir / f"{command_id}.log"
        if not log_file.exists():
            violations.append(f"Missing log for required command: {command_id}")
            continue

        content = log_file.read_text(encoding="utf-8")
        exits = EXIT_PATTERN.findall(content)
        if not exits:
            violations.append(f"Missing exit marker in log: {command_id}")
            continue

        last_id, last_rc = exits[-1]
        if last_id != command_id:
            violations.append(
                f"Exit marker command ID mismatch for {command_id}: found {last_id}"
            )
            continue

        if int(last_rc) != 0:
            violations.append(f"Required command failed: {command_id} (exit {last_rc})")
        else:
            evidence.append(f"{command_id}:exit=0")
    return violations, evidence


def _extract_report_sections(report_text: str) -> Dict[str, str]:
    section_map: Dict[str, str] = {}
    for idx, heading in enumerate(REQUIRED_REPORT_HEADINGS):
        start = report_text.find(heading)
        if start < 0:
            continue
        if idx + 1 < len(REQUIRED_REPORT_HEADINGS):
            next_start = report_text.find(REQUIRED_REPORT_HEADINGS[idx + 1], start + len(heading))
            body = report_text[start + len(heading): next_start if next_start >= 0 else None]
        else:
            body = report_text[start + len(heading):]
        section_map[heading] = body.strip()
    return section_map


def verify(phase_json_path: Path) -> Dict[str, object]:
    phase = _load_json(phase_json_path)
    workspace = Path(phase["workspace_root"]).resolve()
    artifacts = phase.get("artifacts", {})

    files_json = Path(artifacts["files_json"]).resolve()
    commands_sh = Path(artifacts["commands_sh"]).resolve()
    report_md = Path(artifacts["report_md"]).resolve()
    logs_dir = commands_sh.parent / "logs"
    phase_dir = report_md.parent

    violations: List[str] = []
    evidence: List[str] = []

    if not files_json.exists():
        violations.append(f"Missing files.json: {files_json}")
    if not commands_sh.exists():
        violations.append(f"Missing commands.sh: {commands_sh}")
    if not report_md.exists():
        violations.append(f"Missing report.md: {report_md}")

    allowlist: List[Dict[str, str]] = []
    if files_json.exists():
        files_data = _load_json(files_json)
        allowlist = files_data.get("allowlist", [])

    changed_files = _list_changed_files(workspace, phase.get("repos", []))
    rel_phase_dir = phase_dir.relative_to(workspace).as_posix()
    rel_state = f".roo-state-{phase.get('jira_id', '')}.json"
    ignored_prefixes = [f"{rel_phase_dir}/", f".roo-artifacts/{phase.get('jira_id', '')}/"]
    filtered_changed = [
        item
        for item in changed_files
        if not any(item.startswith(prefix) for prefix in ignored_prefixes) and item != rel_state
    ]
    out_of_scope = [item for item in filtered_changed if not _allowlist_match(item, allowlist)]
    if out_of_scope:
        violations.append(
            "Files modified outside allowlist: " + ", ".join(out_of_scope)
        )
    else:
        evidence.append(f"scope_ok:{len(filtered_changed)}_files")

    required_commands: List[str] = []
    if commands_sh.exists():
        required_commands = _parse_required_commands(commands_sh)
        cmd_violations, cmd_evidence = _check_command_logs(logs_dir, required_commands)
        violations.extend(cmd_violations)
        evidence.extend(cmd_evidence)

    if report_md.exists():
        report_text = report_md.read_text(encoding="utf-8")
        sections = _extract_report_sections(report_text)
        for heading in REQUIRED_REPORT_HEADINGS:
            if heading not in sections:
                violations.append(f"Missing report section: {heading}")
                continue
            if not sections[heading]:
                violations.append(f"Empty report section: {heading}")

        acceptance_body = sections.get("## Acceptance Checks", "")
        outcomes = OUTCOME_PATTERN.findall(acceptance_body)
        if not outcomes:
            violations.append("Acceptance Checks section must contain PASS/FAIL/BLOCKED outcomes")
        else:
            evidence.append(f"acceptance_outcomes:{len(outcomes)}")

    verified = len(violations) == 0
    result = {
        "phase_json": str(phase_json_path),
        "verified": verified,
        "required_checks_passed": verified,
        "violations": violations,
        "changed_files": changed_files,
        "changed_files_considered": filtered_changed,
        "required_commands": required_commands,
        "evidence": evidence,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify phase compliance against runbook contract")
    parser.add_argument("phase_json", help="Path to phase.json")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()

    phase_json_path = Path(args.phase_json).resolve()
    if not phase_json_path.exists():
        print(json.dumps({"verified": False, "violations": [f"Missing phase.json: {phase_json_path}"]}, indent=2))
        return 1

    result = verify(phase_json_path)
    payload = json.dumps(result, indent=2)
    print(payload)

    if args.output:
        Path(args.output).resolve().write_text(payload + "\n", encoding="utf-8")

    return 0 if result["verified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
