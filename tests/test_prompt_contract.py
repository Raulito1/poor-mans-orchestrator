from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def _load_orchestrator_module(workspace: Path):
    module_path = workspace / "roo-orchestrator-auto.py"
    spec = importlib.util.spec_from_file_location("roo_orchestrator_auto", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load orchestrator module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PromptContractValidationTests(unittest.TestCase):
    def test_prompt_contract_missing_required_field_fails(self) -> None:
        workspace = Path(__file__).resolve().parents[1]
        module = _load_orchestrator_module(workspace)
        orchestrator = module.RooOrchestrator(
            jira_id="TEST-1",
            task_type=module.TaskType.FEATURE,
            workspace_dir=str(workspace),
        )
        contract = {
            "role": "executor",
            "objective": "run phase",
            "inputs": ["a"],
            "constraints": ["b"],
            "allowed_actions": ["c"],
            "output_requirements": ["d"],
        }
        with self.assertRaises(ValueError):
            orchestrator._validate_prompt_contract(contract)


if __name__ == "__main__":
    unittest.main()
