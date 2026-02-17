from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


def _load_compliance_module(workspace: Path):
    module_path = workspace / "scripts" / "verify_phase_compliance.py"
    spec = importlib.util.spec_from_file_location("verify_phase_compliance", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load compliance module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifyPhaseComplianceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.mod = _load_compliance_module(self.repo_root)

    def _create_fixture(self) -> tuple[Path, Path]:
        tmp = tempfile.TemporaryDirectory()
        workspace = Path(tmp.name)
        self.addCleanup(tmp.cleanup)

        subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True)
        (workspace / "README.md").write_text("fixture\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=workspace, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=workspace,
            check=True,
            capture_output=True,
            env={
                **os.environ,
                "GIT_AUTHOR_NAME": "test",
                "GIT_AUTHOR_EMAIL": "test@example.com",
                "GIT_COMMITTER_NAME": "test",
                "GIT_COMMITTER_EMAIL": "test@example.com",
            },
        )

        phase_dir = workspace / "out" / "T-1" / "phase-01-implementation"
        logs_dir = phase_dir / "logs"
        phase_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)

        files_json = phase_dir / "files.json"
        commands_sh = phase_dir / "commands.sh"
        report_md = phase_dir / "report.md"
        phase_json = phase_dir / "phase.json"

        files_json.write_text(
            json.dumps(
                {
                    "allowlist": [
                        {"path": "src/**", "kind": "glob"},
                        {"path": "out/T-1/phase-01-implementation/report.md", "kind": "file"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        commands_sh.write_text(
            "#!/usr/bin/env bash\nrun_cmd repo-lint true 'echo lint'\n",
            encoding="utf-8",
        )
        report_md.write_text(
            "\n".join(
                [
                    "## Summary",
                    "Done.",
                    "## Files Touched",
                    "src/main.py",
                    "## Command Results",
                    "logs/repo-lint.log",
                    "## Acceptance Checks",
                    "- commands_passed: PASS - logs/repo-lint.log",
                    "- scope_respected: PASS - src/main.py",
                    "- report_completed: PASS - sections filled",
                    "## Blockers / Next Steps",
                    "None.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        phase_json.write_text(
            json.dumps(
                {
                    "jira_id": "T-1",
                    "workspace_root": str(workspace),
                    "repos": [{"repo_id": "repo", "path": "."}],
                    "artifacts": {
                        "files_json": str(files_json),
                        "commands_sh": str(commands_sh),
                        "report_md": str(report_md),
                    },
                }
            ),
            encoding="utf-8",
        )

        return workspace, phase_json

    def test_missing_required_command_log_fails(self) -> None:
        _, phase_json = self._create_fixture()
        result = self.mod.verify(phase_json)
        self.assertFalse(result["verified"])
        self.assertTrue(any("Missing log for required command" in v for v in result["violations"]))

    def test_required_command_failure_fails(self) -> None:
        workspace, phase_json = self._create_fixture()
        log_path = workspace / "out" / "T-1" / "phase-01-implementation" / "logs" / "repo-lint.log"
        log_path.write_text("[EXIT] repo-lint -> 1\n", encoding="utf-8")
        result = self.mod.verify(phase_json)
        self.assertFalse(result["verified"])
        self.assertTrue(any("Required command failed" in v for v in result["violations"]))

    def test_incomplete_report_fails(self) -> None:
        workspace, phase_json = self._create_fixture()
        log_path = workspace / "out" / "T-1" / "phase-01-implementation" / "logs" / "repo-lint.log"
        log_path.write_text("[EXIT] repo-lint -> 0\n", encoding="utf-8")
        report_path = workspace / "out" / "T-1" / "phase-01-implementation" / "report.md"
        report_path.write_text("## Summary\nOnly summary\n", encoding="utf-8")
        result = self.mod.verify(phase_json)
        self.assertFalse(result["verified"])
        self.assertTrue(any("Missing report section" in v for v in result["violations"]))

    def test_scope_violation_fails(self) -> None:
        workspace, phase_json = self._create_fixture()
        log_path = workspace / "out" / "T-1" / "phase-01-implementation" / "logs" / "repo-lint.log"
        log_path.write_text("[EXIT] repo-lint -> 0\n", encoding="utf-8")
        (workspace / "unsafe.txt").write_text("oops\n", encoding="utf-8")
        result = self.mod.verify(phase_json)
        self.assertFalse(result["verified"])
        self.assertTrue(any("outside allowlist" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
