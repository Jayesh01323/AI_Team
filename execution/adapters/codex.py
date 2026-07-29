"""
OpenAI Codex adapter — production-ready scaffold.

Uses ProviderScaffoldAdapter for all lifecycle methods.
execute() raises ProviderNotImplementedError until a live API integration is configured.
"""

from execution.adapters.scaffold import ProviderScaffoldAdapter


class CodexAdapter(ProviderScaffoldAdapter):
    """Adapter for OpenAI Codex CLI agent.

    Supports:
      - prepare() — workspace setup, contract/log path creation
      - health_check() — configuration & workspace validation
      - collect_results() — telemetry and output path collection
      - cleanup() — ephemeral state cleanup
      - execute() — raises ProviderNotImplementedError (no live API)
    """

    provider_name: str = "codex"
