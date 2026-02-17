from __future__ import annotations

import json
import shlex
from pathlib import Path
from typing import Dict, List

from orchestrator.context_snapshot import RepoSnapshot

CODE_PHASES = {"implementation", "fix", "poc"}
TEST_PHASES = {"testing"}
DOC_PHASES = {"documentation"}
ANALYSIS_PHASES = {
    "analysis",
    "planning",
    "review",
    "reproduce",
    "diagnosis",
    "research",
    "recommendations",
}


def _phase_dir(workspace: Path, jira_id: str, phase_index: int, phase: str) -> Path:
    return workspace / "out" / jira_id / f"phase-{phase_index:02d}-{phase}"


def _code_globs_for_repo(repo: RepoSnapshot) -> List[str]:
    base = "" if repo.rel_path == "." else f"{repo.rel_path}/"
    candidates = [
        "src/**",
        "app/**",
        "lib/**",
        "packages/**",
        "modules/**",
        "services/**",
        "client/**",
        "rest/**",
        "models/**",
    ]
    return [f"{base}{item}" for item in candidates]


def _test_globs_for_repo(repo: RepoSnapshot) -> List[str]:
    base = "" if repo.rel_path == "." else f"{repo.rel_path}/"
    return [f"{base}tests/**", f"{base}test/**", f"{base}src/**"]


def _doc_globs_for_repo(repo: RepoSnapshot) -> List[str]:
    base = "" if repo.rel_path == "." else f"{repo.rel_path}/"
    return [f"{base}README.md", f"{base}docs/**", f"{base}CHANGELOG.md"]


def _build_files_allowlist(
    workspace: Path,
    jira_id: str,
    phase: str,
    phase_dir: Path,
    repos: List[RepoSnapshot],
) -> Dict:
    allowlist: List[Dict[str, str]] = []

    if phase in CODE_PHASES:
        for repo in repos:
            for glob in _code_globs_for_repo(repo):
                allowlist.append({"repo_id": repo.repo_id, "path": glob, "kind": "glob"})
    elif phase in TEST_PHASES:
        for repo in repos:
            for glob in _test_globs_for_repo(repo):
                allowlist.append({"repo_id": repo.repo_id, "path": glob, "kind": "glob"})
    elif phase in DOC_PHASES:
        for repo in repos:
            for glob in _doc_globs_for_repo(repo):
                allowlist.append({"repo_id": repo.repo_id, "path": glob, "kind": "glob"})
    else:
        allowlist = []

    rel_phase_dir = str(phase_dir.relative_to(workspace))
    allowlist.append({"repo_id": "orchestrator", "path": f"{rel_phase_dir}/report.md", "kind": "file"})

    return {
        "jira_id": jira_id,
        "phase": phase,
        "scope_lock": True,
        "allowlist": allowlist,
        "notes": [
            "Only edit files matching allowlist entries.",
            "If required work is outside scope, stop and write blocker details in report.md.",
        ],
    }


def _commands_for_repo(repo: RepoSnapshot, phase: str) -> List[Dict[str, object]]:
    commands: List[Dict[str, object]] = []
    repo_cd = "." if repo.rel_path == "." else repo.rel_path

    commands.append(
        {
            "id": f"{repo.repo_id}-git-status",
            "name": f"Git status ({repo.repo_id})",
            "repo_id": repo.repo_id,
            "required": False,
            "shell": f'(cd "{repo_cd}" && git status --short)',
            "powershell": f'Push-Location "{repo_cd}"; git status --short; Pop-Location',
        }
    )

    if phase in CODE_PHASES | TEST_PHASES | DOC_PHASES:
        if repo.tooling.get("python_poetry"):
            commands.extend(
                [
                    {
                        "id": f"{repo.repo_id}-format",
                        "name": f"Format ({repo.repo_id})",
                        "repo_id": repo.repo_id,
                        "required": False,
                        "shell": f'(cd "{repo_cd}" && poetry run ruff format .)',
                        "powershell": f'Push-Location "{repo_cd}"; poetry run ruff format .; Pop-Location',
                    },
                    {
                        "id": f"{repo.repo_id}-lint",
                        "name": f"Lint ({repo.repo_id})",
                        "repo_id": repo.repo_id,
                        "required": True,
                        "shell": f'(cd "{repo_cd}" && poetry run ruff check .)',
                        "powershell": f'Push-Location "{repo_cd}"; poetry run ruff check .; Pop-Location',
                    },
                    {
                        "id": f"{repo.repo_id}-test",
                        "name": f"Test ({repo.repo_id})",
                        "repo_id": repo.repo_id,
                        "required": phase in CODE_PHASES | TEST_PHASES,
                        "shell": f'(cd "{repo_cd}" && poetry run pytest -q)',
                        "powershell": f'Push-Location "{repo_cd}"; poetry run pytest -q; Pop-Location',
                    },
                ]
            )

        if repo.tooling.get("node"):
            commands.extend(
                [
                    {
                        "id": f"{repo.repo_id}-format",
                        "name": f"Format ({repo.repo_id})",
                        "repo_id": repo.repo_id,
                        "required": False,
                        "shell": f'(cd "{repo_cd}" && npm run format --if-present)',
                        "powershell": f'Push-Location "{repo_cd}"; npm run format --if-present; Pop-Location',
                    },
                    {
                        "id": f"{repo.repo_id}-lint",
                        "name": f"Lint ({repo.repo_id})",
                        "repo_id": repo.repo_id,
                        "required": True,
                        "shell": f'(cd "{repo_cd}" && npm run lint --if-present)',
                        "powershell": f'Push-Location "{repo_cd}"; npm run lint --if-present; Pop-Location',
                    },
                    {
                        "id": f"{repo.repo_id}-test",
                        "name": f"Test ({repo.repo_id})",
                        "repo_id": repo.repo_id,
                        "required": phase in CODE_PHASES | TEST_PHASES,
                        "shell": f'(cd "{repo_cd}" && npm test --if-present)',
                        "powershell": f'Push-Location "{repo_cd}"; npm test --if-present; Pop-Location',
                    },
                ]
            )

        if repo.tooling.get("maven"):
            commands.append(
                {
                    "id": f"{repo.repo_id}-test",
                    "name": f"Maven test ({repo.repo_id})",
                    "repo_id": repo.repo_id,
                    "required": phase in CODE_PHASES | TEST_PHASES,
                    "shell": f'(cd "{repo_cd}" && ./mvnw test)',
                    "powershell": f'Push-Location "{repo_cd}"; ./mvnw test; Pop-Location',
                }
            )

        if repo.tooling.get("gradle"):
            commands.append(
                {
                    "id": f"{repo.repo_id}-test",
                    "name": f"Gradle test ({repo.repo_id})",
                    "repo_id": repo.repo_id,
                    "required": phase in CODE_PHASES | TEST_PHASES,
                    "shell": f'(cd "{repo_cd}" && ./gradlew test)',
                    "powershell": f'Push-Location "{repo_cd}"; ./gradlew test; Pop-Location',
                }
            )

        if repo.tooling.get("terraform"):
            commands.extend(
                [
                    {
                        "id": f"{repo.repo_id}-tf-fmt",
                        "name": f"Terraform fmt ({repo.repo_id})",
                        "repo_id": repo.repo_id,
                        "required": False,
                        "shell": f'(cd "{repo_cd}" && terraform fmt -recursive)',
                        "powershell": f'Push-Location "{repo_cd}"; terraform fmt -recursive; Pop-Location',
                    },
                    {
                        "id": f"{repo.repo_id}-tf-validate",
                        "name": f"Terraform validate ({repo.repo_id})",
                        "repo_id": repo.repo_id,
                        "required": phase in CODE_PHASES | TEST_PHASES,
                        "shell": f'(cd "{repo_cd}" && terraform validate)',
                        "powershell": f'Push-Location "{repo_cd}"; terraform validate; Pop-Location',
                    },
                ]
            )

    return commands


def _build_command_plan(repos: List[RepoSnapshot], phase: str) -> List[Dict[str, object]]:
    commands: List[Dict[str, object]] = []
    for repo in repos:
        commands.extend(_commands_for_repo(repo, phase))
    if not commands:
        commands.append(
            {
                "id": "no-op",
                "name": "No-op",
                "repo_id": "orchestrator",
                "required": False,
                "shell": 'echo "No allowlisted commands for this phase"',
                "powershell": 'Write-Output "No allowlisted commands for this phase"',
            }
        )
    return commands


def _render_commands_sh(commands: List[Dict[str, object]]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "BASE_DIR=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)\"",
        "LOG_DIR=\"$BASE_DIR/logs\"",
        "mkdir -p \"$LOG_DIR\"",
        "",
        "run_cmd() {",
        "  local id=\"$1\"",
        "  local required=\"$2\"",
        "  shift 2",
        "  local cmd=\"$*\"",
        "  local log=\"$LOG_DIR/${id}.log\"",
        "  echo \"[RUN] $id\" | tee \"$log\"",
        "  bash -lc \"$cmd\" 2>&1 | tee -a \"$log\"",
        "  local rc=${PIPESTATUS[0]}",
        "  echo \"[EXIT] $id -> $rc\" | tee -a \"$log\"",
        "  if [[ \"$required\" == \"true\" && $rc -ne 0 ]]; then",
        "    echo \"Required command failed: $id\"",
        "    exit $rc",
        "  fi",
        "}",
        "",
    ]

    for cmd in commands:
        lines.append(
            f"run_cmd {shlex.quote(str(cmd['id']))} {'true' if cmd['required'] else 'false'} {shlex.quote(str(cmd['shell']))}"
        )

    lines.append('echo "Command plan complete. Logs: $LOG_DIR"')
    return "\n".join(lines) + "\n"


def _render_commands_ps1(commands: List[Dict[str, object]]) -> str:
    lines = [
        "$ErrorActionPreference = 'Stop'",
        "$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path",
        "$LogDir = Join-Path $BaseDir 'logs'",
        "New-Item -ItemType Directory -Force -Path $LogDir | Out-Null",
        "",
        "function Run-Cmd {",
        "  param([string]$Id, [bool]$Required, [string]$Cmd)",
        "  $Log = Join-Path $LogDir ($Id + '.log')",
        "  \"[RUN] $Id\" | Tee-Object -FilePath $Log",
        "  Invoke-Expression $Cmd 2>&1 | Tee-Object -FilePath $Log -Append",
        "  if ($LASTEXITCODE -ne 0 -and $Required) {",
        "    throw \"Required command failed: $Id\"",
        "  }",
        "}",
        "",
    ]

    for cmd in commands:
        escaped = str(cmd["powershell"]).replace("'", "''")
        lines.append(f"Run-Cmd -Id '{cmd['id']}' -Required ${str(cmd['required']).lower()} -Cmd '{escaped}'")

    lines.append('Write-Output "Command plan complete. Logs: $LogDir"')
    return "\n".join(lines) + "\n"


def _render_report_template(
    jira_id: str,
    task_type: str,
    phase: str,
    phase_index: int,
    runbook_path: Path,
    files_path: Path,
    commands_path: Path,
) -> str:
    return f"""# Phase Report - {jira_id}

- Task type: {task_type}
- Phase: {phase_index:02d} ({phase})
- Runbook: {runbook_path.name}
- Scope lock: {files_path.name}
- Command allowlist: {commands_path.name}

## Summary

<!-- Fill concise summary of work completed -->

## Files Touched

<!-- List exact files touched and why -->

## Command Results

<!-- Link logs from ./logs and summarize pass/fail -->

## Acceptance Checks

<!-- Mark each check as PASS/FAIL/BLOCKED with evidence -->
- commands_passed: BLOCKED - add evidence link from ./logs
- scope_respected: BLOCKED - list changed files
- report_completed: BLOCKED - summarize completeness and residual risks

## Blockers / Next Steps

<!-- If stopped, include actionable next step and owner -->

<!-- completion_marker: INCOMPLETE -->
"""


def _render_runbook(
    jira_id: str,
    task_type: str,
    phase: str,
    phase_index: int,
    phase_total: int,
    budget: int,
    mode: str,
) -> str:
    stop_conditions = [
        "If any required command in commands.sh / commands.ps1 fails, stop immediately.",
        "If required file changes are outside files.json allowlist, stop and report blocker.",
        "If requirements are ambiguous, do not guess; report assumptions needed.",
    ]

    acceptance = [
        "All required commands completed successfully with logs in ./logs.",
        "Only files in files.json allowlist were modified.",
        "report.md completed with evidence and remaining risks.",
    ]

    return "\n".join(
        [
            f"# Runbook - {jira_id} Phase {phase_index:02d}/{phase_total:02d}",
            "",
            f"- Task type: {task_type}",
            f"- Phase: {phase}",
            f"- Budget hint: {budget:,} tokens",
            f"- Recommended Roo mode: {mode}",
            "",
            "## Required Inputs",
            "- files.json",
            "- commands.sh (or commands.ps1 on Windows)",
            "- report.md",
            "",
            "## Execution Contract",
            "1. Read files.json and lock scope to allowlisted files only.",
            "2. Execute only commands from commands.sh / commands.ps1.",
            "3. Capture evidence in ./logs and summarize in report.md.",
            "4. Do not add unapproved commands or files.",
            "",
            "## Stop Conditions",
            *[f"- {item}" for item in stop_conditions],
            "",
            "## Acceptance Checks",
            *[f"- [ ] {item}" for item in acceptance],
            "",
            "## Completion",
            "- Fill report.md completely.",
            "- Include explicit PASS/FAIL/BLOCKED per acceptance check.",
        ]
    ) + "\n"


def render_phase_bundle(
    workspace: Path,
    jira_id: str,
    task_type: str,
    phase: str,
    phase_index: int,
    phase_total: int,
    budget: int,
    mode: str,
    repos: List[RepoSnapshot],
) -> Dict[str, str]:
    phase_dir = _phase_dir(workspace, jira_id, phase_index, phase)
    logs_dir = phase_dir / "logs"
    phase_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    runbook_path = phase_dir / "runbook.md"
    files_path = phase_dir / "files.json"
    commands_sh_path = phase_dir / "commands.sh"
    commands_ps1_path = phase_dir / "commands.ps1"
    report_path = phase_dir / "report.md"
    manifest_path = phase_dir / "phase.json"

    files_data = _build_files_allowlist(workspace, jira_id, phase, phase_dir, repos)
    commands = _build_command_plan(repos, phase)

    runbook_path.write_text(
        _render_runbook(jira_id, task_type, phase, phase_index, phase_total, budget, mode),
        encoding="utf-8",
    )
    files_path.write_text(json.dumps(files_data, indent=2), encoding="utf-8")
    commands_sh_path.write_text(_render_commands_sh(commands), encoding="utf-8")
    commands_ps1_path.write_text(_render_commands_ps1(commands), encoding="utf-8")
    report_path.write_text(
        _render_report_template(
            jira_id,
            task_type,
            phase,
            phase_index,
            runbook_path,
            files_path,
            commands_sh_path,
        ),
        encoding="utf-8",
    )

    try:
        commands_sh_path.chmod(0o755)
    except OSError:
        pass

    manifest = {
        "jira_id": jira_id,
        "phase_id": phase_index,
        "phase_name": phase,
        "task_type": task_type,
        "workspace_root": str(workspace),
        "repos": [
            {
                "repo_id": repo.repo_id,
                "path": repo.rel_path,
                "module_roots": repo.module_roots,
            }
            for repo in repos
        ],
        "artifacts": {
            "runbook_md": str(runbook_path),
            "files_json": str(files_path),
            "commands_sh": str(commands_sh_path),
            "commands_ps1": str(commands_ps1_path),
            "report_md": str(report_path),
        },
        "scope_lock": {"allowed_files_only": True},
        "stop_conditions": [
            "required-command-failure",
            "scope-violation",
            "ambiguous-requirement",
        ],
        "acceptance_checks": [
            {
                "id": "commands_passed",
                "description": "All required commands completed successfully",
                "required": True,
            },
            {
                "id": "scope_respected",
                "description": "Only allowlisted files were modified",
                "required": True,
            },
            {
                "id": "report_completed",
                "description": "report.md is completed with evidence",
                "required": True,
            },
        ],
        "verified": False,
        "violations": [],
        "required_checks_passed": False,
    }

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return {
        "phase_dir": str(phase_dir),
        "runbook_md": str(runbook_path),
        "files_json": str(files_path),
        "commands_sh": str(commands_sh_path),
        "commands_ps1": str(commands_ps1_path),
        "report_md": str(report_path),
        "phase_json": str(manifest_path),
    }
