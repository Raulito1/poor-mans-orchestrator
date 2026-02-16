from __future__ import annotations

from typing import Dict, List

FEATURE_PHASES: Dict[str, int] = {
    "analysis": 25_000,
    "planning": 20_000,
    "implementation": 60_000,
    "testing": 30_000,
    "documentation": 15_000,
    "review": 20_000,
}

BUG_PHASES: Dict[str, int] = {
    "reproduce": 20_000,
    "diagnosis": 40_000,
    "fix": 60_000,
    "testing": 30_000,
    "documentation": 20_000,
}

SPIKE_PHASES: Dict[str, int] = {
    "research": 50_000,
    "poc": 60_000,
    "analysis": 40_000,
    "recommendations": 20_000,
}

MODE_RECOMMENDATIONS: Dict[str, str] = {
    "analysis": "Architect",
    "planning": "Architect",
    "implementation": "Code",
    "testing": "Debug",
    "documentation": "Code",
    "review": "Architect",
    "reproduce": "Debug",
    "diagnosis": "Debug",
    "fix": "Code",
    "research": "Architect",
    "poc": "Code",
    "recommendations": "Architect",
}


def get_phase_sequence(task_type: str) -> List[str]:
    if task_type == "feature":
        return list(FEATURE_PHASES.keys())
    if task_type == "bug":
        return list(BUG_PHASES.keys())
    if task_type == "spike":
        return list(SPIKE_PHASES.keys())
    raise ValueError(f"Unsupported task type: {task_type}")


def get_phase_budget(task_type: str, phase: str) -> int:
    if task_type == "feature":
        return FEATURE_PHASES.get(phase, 30_000)
    if task_type == "bug":
        return BUG_PHASES.get(phase, 30_000)
    if task_type == "spike":
        return SPIKE_PHASES.get(phase, 30_000)
    raise ValueError(f"Unsupported task type: {task_type}")


def get_phase_mode(phase: str) -> str:
    return MODE_RECOMMENDATIONS.get(phase, "Code")
