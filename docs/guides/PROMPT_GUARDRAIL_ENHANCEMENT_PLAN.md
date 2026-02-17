# Prompt + Guardrail Enforcement Enhancement Plan

## Goal
Upgrade the orchestrator from instruction-only guardrails to enforceable policy controls, so phase completion is based on verified compliance instead of prompt acknowledgement.

## Target Outcomes
- Phase completes only when compliance verification passes.
- Prompt generation follows a strict, validated structure.
- Guardrail profile selection is accurate for mono-repo and multi-repo setups.
- Reports include required evidence and machine-checkable completion markers.

## Scope
- `roo-orchestrator-auto.py`
- `orchestrator/context_snapshot.py`
- `orchestrator/runbook_renderer.py`
- `scripts/verify_phase.py` (or new verifier script)
- `schemas/*.json`
- `docs/*guardrails-prompt.txt`
- `docs/guides/*.md`
- `tests/*`

## Phased Implementation Plan

### Phase 1: Contracts and Schemas
1. Add `schemas/prompt-contract.schema.json`.
2. Require prompt sections:
   - `role`
   - `objective`
   - `inputs`
   - `constraints`
   - `allowed_actions`
   - `output_requirements`
   - `fallback`
3. Add `schemas/report-contract.schema.json` for required report sections and evidence links.
4. Extend `schemas/phase-output.schema.json` to include:
   - `verified` (boolean)
   - `violations` (array)
   - `required_checks_passed` (boolean)

### Phase 2: Hard Compliance Gate
1. Implement `scripts/verify_phase_compliance.py` with checks for:
   - Changed files are inside `files.json` allowlist.
   - Required commands have logs in `logs/`.
   - Required commands exited successfully.
   - `report.md` contains required sections and PASS/FAIL/BLOCKED outcomes.
2. Update `run_phase()` in `roo-orchestrator-auto.py`:
   - Run compliance verifier before marking success.
   - Do not append phase to `phases_completed` if verifier fails.
   - Store verification output in execution history.
3. Keep `scripts/verify_phase.py` as minimal artifact check, but call it pre-check; call compliance verifier as completion gate.

### Phase 3: Prompt Builder + Validation
1. Refactor prompt assembly into a structured builder object (not only raw string concat).
2. Validate prompt object against `prompt-contract.schema.json` before rendering/writing.
3. Fail closed on missing guardrail files by default.
4. Add override flag for emergencies:
   - `--allow-missing-guardrails` (explicit, off by default)

### Phase 4: Guardrail Profile Accuracy
1. Expand Python detection in `orchestrator/context_snapshot.py`:
   - `requirements.txt`
   - `setup.py`
   - `Pipfile`
2. Add explicit CLI override:
   - `--guardrail-profile react|python-fastapi|java-spring`
3. Make profile selection phase-aware where applicable.
4. Remove duplicate content in:
   - `docs/python/python-fastapi-debug-guardrails-prompt.txt`

### Phase 5: Tests and CI
1. Add unit tests:
   - Guardrail profile detection.
   - Prompt contract generation/validation.
2. Add integration tests with fixtures:
   - Scope violation.
   - Missing required command log.
   - Required command failure.
   - Incomplete report.
3. Add CI checks:
   - Schema validation tests.
   - Verifier tests.

### Phase 6: Rollout Strategy
1. Introduce `--strict-enforcement` flag (initially optional).
2. Run audit mode first:
   - Collect violations without blocking.
3. Flip to strict mode default after stabilization.
4. Update docs:
   - `docs/guides/RUNBOOK_WORKFLOW.md`
   - `docs/guides/AUTOMATION_GUIDE.md`

## Suggested Task Backlog

1. Add new schemas (`prompt-contract`, `report-contract`, phase schema extension).
2. Build compliance verifier script.
3. Wire verifier gate into orchestrator phase completion.
4. Refactor prompt generation into structured contract.
5. Add guardrail profile override + improved detection.
6. Clean duplicated Python debug guardrail prompt.
7. Add tests and CI coverage.
8. Update docs and migration notes.

## Acceptance Criteria
- No phase is marked complete unless compliance verifier returns pass.
- Prompt generation fails fast when required contract sections are missing.
- Guardrail profile can be overridden explicitly and is correct by default for detected tooling.
- Compliance violations are recorded in state/history with actionable details.
- Automated tests cover core pass/fail guardrail paths.

## Risks and Mitigations
- Risk: strict gating interrupts current flow.
  - Mitigation: staged rollout with audit mode and `--strict-enforcement`.
- Risk: false positives in scope validation.
  - Mitigation: add precise glob matcher tests and fixture coverage.
- Risk: multi-language repo ambiguity.
  - Mitigation: phase-aware selection + `--guardrail-profile` override.

## File-Level Change Map
- `roo-orchestrator-auto.py`
  - Add verifier invocation and success gating.
  - Add CLI flags for strict mode and guardrail override.
- `orchestrator/context_snapshot.py`
  - Improve tooling detection signals.
- `orchestrator/runbook_renderer.py`
  - Ensure manifest includes verification fields.
- `scripts/verify_phase_compliance.py` (new)
  - Implement end-to-end compliance checks.
- `schemas/phase-output.schema.json`
  - Extend with verification properties.
- `schemas/prompt-contract.schema.json` (new)
- `schemas/report-contract.schema.json` (new)
- `docs/python/python-fastapi-debug-guardrails-prompt.txt`
  - Remove duplicate prompt block.

## Definition of Done
- All new schema validations and verifier checks are implemented and tested.
- Orchestrator phase completion is gated by verifier pass.
- Documentation reflects strict enforcement behavior and operator workflow.
