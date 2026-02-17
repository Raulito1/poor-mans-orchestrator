from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from orchestrator.context_snapshot import snapshot_workspace


class ContextSnapshotTests(unittest.TestCase):
    def test_detects_python_from_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "requirements.txt").write_text("fastapi\n", encoding="utf-8")

            repos = snapshot_workspace(root)
            self.assertEqual(len(repos), 1)
            self.assertTrue(repos[0].tooling["python"])
            self.assertTrue(repos[0].tooling["python_requirements"])

    def test_detects_python_from_setup_py(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "setup.py").write_text("from setuptools import setup\n", encoding="utf-8")

            repos = snapshot_workspace(root)
            self.assertEqual(len(repos), 1)
            self.assertTrue(repos[0].tooling["python"])
            self.assertTrue(repos[0].tooling["python_setup_py"])


if __name__ == "__main__":
    unittest.main()
