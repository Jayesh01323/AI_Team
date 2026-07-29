"""
Cursor adapter — production-ready scaffold.

Cursor is an AI-powered IDE. This adapter provides a scaffold for future
Cursor Composer / Cursor Agent automation integration.

Uses ProviderScaffoldAdapter for all lifecycle methods.
execute() raises ProviderNotImplementedError until a live API is available.
"""

from execution.adapters.scaffold import ProviderScaffoldAdapter


class CursorAdapter(ProviderScaffoldAdapter):
    """Adapter for Cursor IDE (Composer / Agent mode).

    Supports:
      - prepare() — workspace setup, contract/log path creation
      - health_check() — configuration & workspace validation
      - collect_results() — telemetry and output path collection
      - cleanup() — ephemeral state cleanup
      - execute() — raises ProviderNotImplementedError (no live API)
    """

    provider_name: str = "cursor"
