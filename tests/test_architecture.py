import ast
import importlib
from pathlib import Path

from architecture_rules import ARCHITECTURE_RULES

PROJECT_ROOT = Path(__file__).parent.parent


def get_imports_from_file(file_path: Path) -> set[str]:
    """Parse a python file using AST and return all imported module names."""
    if not file_path.exists():
        return set()

    code = file_path.read_text(encoding="utf-8")
    tree = ast.parse(code, filename=str(file_path))
    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)

    return imports


def test_configurable_architecture_rules():
    """Dynamically tests all architectural layers defined in architecture_rules.py."""
    for rule in ARCHITECTURE_RULES:
        target_path = PROJECT_ROOT / rule.path_pattern
        if target_path.is_file():
            files = [target_path]
        elif target_path.is_dir():
            files = list(target_path.rglob("*.py"))
        else:
            continue

        for py_file in files:
            if "__pycache__" in py_file.parts:
                continue

            imports = get_imports_from_file(py_file)
            for forbidden in rule.forbidden_imports:
                violating_imports = [
                    imp
                    for imp in imports
                    if imp == forbidden or imp.startswith(forbidden + ".")
                ]
                assert not violating_imports, (
                    f"Architecture violation in layer '{rule.name}' ({py_file.relative_to(PROJECT_ROOT)}): "
                    f"Imports forbidden module(s) {violating_imports}. Rule: {rule.description}"
                )


def test_no_circular_imports():
    """Verify that importing all core modules completes without circular import errors."""
    modules_to_test = [
        "core.exceptions",
        "core.logging",
        "models.execution",
        "models.project_context",
        "execution.workspace",
        "execution.adapters.base",
        "execution.adapters.contract",
        "execution.adapters.logger",
        "execution.adapters.factory",
        "execution.adapters.openhands",
        "execution.validation.pipeline",
        "execution.engine",
    ]

    for mod_name in modules_to_test:
        mod = importlib.import_module(mod_name)
        assert mod is not None
