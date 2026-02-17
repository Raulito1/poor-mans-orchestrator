# Manual Runbook Guide - Roo Orchestrator

This guide documents the **manual-only** workflow for the Roo Orchestrator.

The Python app is non-LLM and does not directly call any LLM endpoint.
It generates deterministic runbook artifacts, and you execute Roo/Codex manually once per phase.

## Scope

- Supported execution mode: `manual` only
- Deprecated/removed modes: Roo CLI transport, VS Code API transport, IntelliJ automation transport
- Source of truth for artifact contract: `docs/guides/RUNBOOK_WORKFLOW.md`

## Quick Start

Start a new feature task:

```bash
python3 roo-orchestrator-auto.py \
  --jira PROJ-123 \
  --type feature \
  --max-tokens 8192 \
  --strict-enforcement
```

Start a new bug task:

```bash
python3 roo-orchestrator-auto.py \
  --jira BUG-88 \
  --type bug \
  --max-tokens 8192
```

Run one specific phase:

```bash
python3 roo-orchestrator-auto.py --jira PROJ-123 --phase implementation
```

Resume an existing task:

```bash
python3 roo-orchestrator-auto.py --jira PROJ-123
```

Check status:

```bash
python3 roo-orchestrator-auto.py --jira PROJ-123 --status
```

Reset task state:

```bash
python3 roo-orchestrator-auto.py --jira PROJ-123 --reset
```

## Wrapper Commands (`roo-auto`)

If you prefer the shell wrapper:

```bash
./roo-auto start PROJ-123 feature
./roo-auto continue PROJ-123
./roo-auto run PROJ-123 implementation
./roo-auto status PROJ-123
./roo-auto list
```

## What Happens Per Phase

1. Orchestrator computes task phase metadata (budget, suggested mode hint, ordering).
2. Orchestrator snapshots repository/module/tooling context.
3. Orchestrator generates a deterministic phase bundle under:
   - `out/{JIRA}/phase-XX-{phase}/`
4. Orchestrator shows a manual prompt that points Roo/Codex to those artifacts.
5. You paste prompt into Roo/Codex and execute the phase manually.
6. Roo/Codex follows runbook contract, writes evidence, and fills report.
7. You return to orchestrator and continue to next phase.

## Phase Artifacts

Generated per phase:

- `runbook.md`: strict instructions Roo must follow
- `files.json`: file scope allowlist
- `commands.sh` and `commands.ps1`: command allowlist runners
- `report.md`: required completion template
- `phase.json`: machine-readable phase manifest
- `logs/`: command output evidence folder

Legacy compatibility output is still written to `.roo-artifacts/{JIRA}/`:

- `phase-<name>-instructions.txt`
- `phase-<name>-output.txt`

## Manual Execution Contract

For each phase, Roo/Codex must:

1. Read `runbook.md`, `files.json`, `commands.sh|commands.ps1`, and `report.md`.
2. Edit only allowlisted files from `files.json`.
3. Run only commands from generated command scripts.
4. Capture evidence logs under `logs/`.
5. Stop on required command failure or scope violation and document blocker in `report.md`.

## Configuration

### CLI Arguments

- `--jira`: Jira ticket id (required)
- `--type`: `feature|bug|spike` (required only for new tasks)
- `--workspace`: workspace root (default `.`)
- `--phase`: run one phase only
- `--status`: show current status
- `--reset`: clear saved state
- `--max-tokens`: planning hint for iteration sizing
- `--strict-enforcement`: block phase completion when compliance checks fail
- `--allow-missing-guardrails`: bypass missing guardrail prompt file failure
- `--guardrail-profile`: override profile (`react|python-fastapi|java-spring`)

### Environment Variables

- `ROO_WORKSPACE`: workspace directory for `roo-auto`
- `ROO_MAX_TOKENS`: max token hint for `roo-auto`

## Retry and Resume

On phase issues, orchestrator asks whether to retry or skip.

State is stored in:

- `.roo-state-{JIRA}.json`

Resuming the same Jira id continues from the saved state.

## Validation

Verify generated phase artifact completeness:

```bash
python3 scripts/verify_phase.py out/PROJ-123/phase-03-implementation/phase.json
```

Run full compliance checks:

```bash
python3 scripts/verify_phase_compliance.py out/PROJ-123/phase-03-implementation/phase.json
```

## Troubleshooting

### Prompt shown but no code changes

- Ensure you pasted the phase prompt into Roo/Codex.
- Confirm Roo/Codex can access workspace paths referenced in prompt.
- Check `out/{JIRA}/phase-XX-{phase}/report.md` for blockers.

### Scope conflicts

- If required changes are outside `files.json`, do not bypass scope.
- Record blocker details in `report.md` and rerun with updated planning.

### Required command fails

- Review `out/{JIRA}/phase-XX-{phase}/logs/*.log`.
- Fix within scope if possible.
- If not possible within scope, document blocker and stop.

### Wrong or stale task type

- Reset state and restart with explicit `--type`:

```bash
python3 roo-orchestrator-auto.py --jira PROJ-123 --reset
python3 roo-orchestrator-auto.py --jira PROJ-123 --type feature
```

## Best Practices

1. Keep one Roo invocation per phase.
2. Keep `--max-tokens` aligned with your IDE plugin settings.
3. Review `report.md` and logs before moving to next phase.
4. Use `--phase` for iterative implementation on large tickets.
5. Keep all edits within scope and avoid ad-hoc commands.

## Related Docs

- `docs/RUNBOOK_WORKFLOW.md`: full runbook artifact contract
- `ROO_CLI_GUIDE.md`: legacy reference only
