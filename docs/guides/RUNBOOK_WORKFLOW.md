# Runbook Workflow Guide

This document describes the runbook-based orchestration flow implemented in this repository.

## Purpose

The orchestrator is non-LLM Python code that prepares deterministic phase artifacts.
Roo/Codex (inside IDE/CLI plugin) executes each phase using those artifacts.

Design goals:
- One Roo invocation per phase
- Scope lock for file edits
- Command allowlist for automation
- Evidence logs and auditable outputs

## High-Level Flow

1. Run orchestrator for a Jira ticket and phase.
2. Orchestrator snapshots workspace repos/modules/tooling.
3. Orchestrator generates phase bundle under `out/{JIRA}/phase-XX-{name}/`.
4. Orchestrator sends Roo a strict prompt pointing at generated runbook artifacts.
5. Roo executes phase following runbook contract.
6. Roo fills report and logs command evidence.
7. Orchestrator runs compliance verification and records pass/fail evidence.

## Generated Artifacts Per Phase

Path:
- `out/{JIRA}/phase-XX-{phase}/`

Files:
- `runbook.md`: strict phase instructions and stop conditions
- `files.json`: file scope allowlist for edits
- `commands.sh`: allowlisted Linux/macOS command runner (writes logs)
- `commands.ps1`: allowlisted PowerShell runner
- `report.md`: completion template Roo must fill
- `phase.json`: machine-readable manifest tying all artifacts together
- `logs/`: command output evidence (created by command scripts)
- `compliance.json`: verifier result (generated after manual phase execution)

Legacy compatibility:
- `.roo-artifacts/{JIRA}/phase-*-instructions.txt` is still written for execution history.

## Runbook Contract

Roo must follow these rules in each phase:

1. Read `runbook.md`, `files.json`, `commands.sh|commands.ps1`, `report.md`.
2. Modify only files allowed in `files.json`.
3. Run only commands present in generated command script.
4. Capture command output in `logs/`.
5. If a required command fails or required file is out of scope, stop and document blocker in `report.md`.

## Command Allowlist + Evidence

`commands.sh` / `commands.ps1` are generated from detected repo tooling:
- Python Poetry repos: format/lint/test commands
- Node repos: format/lint/test commands
- Maven/Gradle repos: test commands
- Terraform repos: fmt/validate commands

All commands write logs to:
- `out/{JIRA}/phase-XX-{phase}/logs/*.log`

Required commands fail the script and should stop phase execution.

## Scope Lock

`files.json` defines a per-phase allowlist.
Typical behavior:
- Code phases: source-path globs
- Test phase: test/source globs
- Documentation phase: docs/readme globs
- Analysis/research/review phases: report-only edits

If required changes are outside allowlist, Roo should not proceed with ad-hoc edits.

## Phase Manifest (`phase.json`)

`phase.json` includes:
- Jira + phase identity
- Task type
- Workspace root
- Repo/module snapshot
- Artifact file paths
- Scope lock metadata
- Stop conditions
- Acceptance checks
- Verification fields (`verified`, `violations`, `required_checks_passed`)

Schema reference:
- `schemas/phase-output.schema.json`

## CLI Usage

Start full task:

```bash
python3 roo-orchestrator-auto.py --jira PROJ-123 --type feature

# optional strict enforcement (block completion on compliance failures)
python3 roo-orchestrator-auto.py --jira PROJ-123 --type feature --strict-enforcement
```

Run one phase:

```bash
python3 roo-orchestrator-auto.py --jira PROJ-123 --type feature --phase implementation
```

Resume existing task:

```bash
python3 roo-orchestrator-auto.py --jira PROJ-123
```

Guardrail profile override:

```bash
python3 roo-orchestrator-auto.py --jira PROJ-123 --guardrail-profile python-fastapi
```

## Verify Phase Bundle

Minimal verifier:

```bash
python3 scripts/verify_phase.py out/PROJ-123/phase-03-implementation/phase.json
```

This validates required top-level fields and artifact file existence.

Compliance verifier (scope/log/report checks):

```bash
python3 scripts/verify_phase_compliance.py out/PROJ-123/phase-03-implementation/phase.json
```

## State + Output Locations

- State: `.roo-state-{JIRA}.json`
- Legacy instruction/output: `.roo-artifacts/{JIRA}/`
- Runbook bundle: `out/{JIRA}/phase-XX-{phase}/`

## Enforcement Modes

- Default mode is audit: compliance violations are recorded but do not block phase completion.
- `--strict-enforcement` blocks completion unless compliance verification passes.
- Missing guardrail prompt files fail closed by default.
- `--allow-missing-guardrails` explicitly overrides missing guardrail prompt failures.
