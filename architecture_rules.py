"""
Configurable Architecture Rules

Defines all architectural layers, allowed imports, and forbidden dependencies.
Used by tests/test_architecture.py to enforce boundary rules dynamically.
"""

from dataclasses import dataclass, field


@dataclass
class LayerRule:
    name: str
    path_pattern: str  # Path relative to project root (file or directory)
    allowed_imports: list[str] = field(default_factory=list)
    forbidden_imports: list[str] = field(default_factory=list)
    description: str = ""


# Core architectural layers and dependency boundary specifications
ARCHITECTURE_RULES: list[LayerRule] = [
    LayerRule(
        name="Models Layer",
        path_pattern="models",
        allowed_imports=["core", "typing", "dataclasses", "datetime", "enum", "uuid"],
        forbidden_imports=[
            "execution.adapters",
            "execution.engine",
        ],
        description="Domain models must be pure data structures without dependencies on execution adapters or engines.",
    ),
    LayerRule(
        name="Validation Pipeline",
        path_pattern="execution/validation",
        allowed_imports=[
            "core",
            "subprocess",
            "abc",
            "dataclasses",
            "pathlib",
            "typing",
        ],
        forbidden_imports=[
            "execution.adapters",
            "execution.engine",
        ],
        description="Validation pipeline components must be independent of specific provider adapters and engine orchestration.",
    ),
    LayerRule(
        name="Execution Engine",
        path_pattern="execution/engine.py",
        allowed_imports=[
            "core",
            "models",
            "execution.workspace",
            "execution.adapters.factory",
            "execution.adapters.base",
            "execution.validation.pipeline",
        ],
        forbidden_imports=[
            "execution.adapters.openhands",
            "execution.adapters.claude",
            "execution.adapters.codex",
            "execution.adapters.devin",
            "execution.adapters.antigravity",
        ],
        description="ExecutionEngine must remain provider-agnostic and never depend directly on concrete provider adapters.",
    ),
    LayerRule(
        name="Provider Adapters",
        path_pattern="execution/adapters",
        allowed_imports=["core", "models", "execution.adapters"],
        forbidden_imports=[
            "execution.engine",
        ],
        description="Provider adapters must implement the ExecutionAdapter contract without importing ExecutionEngine.",
    ),
]
