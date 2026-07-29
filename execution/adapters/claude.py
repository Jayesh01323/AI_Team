"""
Claude Code adapter — production-ready scaffold.

Uses ProviderScaffoldAdapter for all lifecycle methods.
execute() raises ProviderNotImplementedError until a live API integration is configured.
"""

from execution.adapters.scaffold import ProviderScaffoldAdapter


class ClaudeAdapter(ProviderScaffoldAdapter):
    """Adapter for Anthropic Claude Code (CLI-based agent mode).

    Supports:
      - prepare() — workspace setup, contract/log path creation
      - health_check() — configuration & workspace validation
      - collect_results() — telemetry and output path collection
      - cleanup() — ephemeral state cleanup
      - execute() — raises ProviderNotImplementedError (no live API)
    """

    provider_name: str = "claude"
