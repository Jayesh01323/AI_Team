"""
VS Code (GitHub Copilot Agent Mode) adapter — production-ready scaffold.

VS Code's GitHub Copilot Agent Mode provides AI-powered coding assistance
within the editor. This adapter provides a scaffold for future automation.

Uses ProviderScaffoldAdapter for all lifecycle methods.
execute() raises ProviderNotImplementedError until a live API is available.
"""

from execution.adapters.scaffold import ProviderScaffoldAdapter


class VSCodeAdapter(ProviderScaffoldAdapter):
    """Adapter for VS Code GitHub Copilot Agent Mode.

    Supports:
      - prepare() — workspace setup, contract/log path creation
      - health_check() — configuration & workspace validation
      - collect_results() — telemetry and output path collection
      - cleanup() — ephemeral state cleanup
      - execute() — raises ProviderNotImplementedError (no live API)
    """

    provider_name: str = "vscode"
