from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


TOOL_MARKERS = (
    "package.json",
    "pyproject.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "go.mod",
    "Cargo.toml",
    "requirements.txt",
    "terraform.tf",
)


@dataclass(frozen=True)
class RepoSnapshot:
    repo_id: str
    rel_path: str
    module_roots: List[str]
    tooling: Dict[str, bool]


def _discover_repo_roots(workspace: Path) -> List[Path]:
    repo_roots: List[Path] = []
    for child in sorted(workspace.iterdir()):
        if child.is_dir() and (child / ".git").exists():
            repo_roots.append(child)
    if not repo_roots:
        repo_roots = [workspace]
    return repo_roots


def _tooling_flags(repo_root: Path) -> Dict[str, bool]:
    return {
        "node": (repo_root / "package.json").exists(),
        "python_poetry": (repo_root / "pyproject.toml").exists(),
        "maven": (repo_root / "pom.xml").exists() or (repo_root / "mvnw").exists(),
        "gradle": (repo_root / "build.gradle").exists() or (repo_root / "build.gradle.kts").exists() or (repo_root / "gradlew").exists(),
        "terraform": any(repo_root.glob("**/*.tf")),
    }


def _discover_module_roots(repo_root: Path, rel_repo_root: str) -> List[str]:
    modules: List[str] = []
    for child in sorted(repo_root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if any((child / marker).exists() for marker in TOOL_MARKERS):
            modules.append(f"{rel_repo_root}/{child.name}" if rel_repo_root != "." else child.name)
    if rel_repo_root == ".":
        modules.insert(0, ".")
    else:
        modules.insert(0, rel_repo_root)
    return modules


def snapshot_workspace(workspace: Path) -> List[RepoSnapshot]:
    repos: List[RepoSnapshot] = []
    for repo_root in _discover_repo_roots(workspace):
        rel = repo_root.relative_to(workspace)
        rel_path = str(rel) if str(rel) else "."
        repo_id = repo_root.name if rel_path != "." else workspace.name
        repos.append(
            RepoSnapshot(
                repo_id=repo_id,
                rel_path=rel_path,
                module_roots=_discover_module_roots(repo_root, rel_path),
                tooling=_tooling_flags(repo_root),
            )
        )
    return repos
