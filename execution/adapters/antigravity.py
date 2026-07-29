"""
Antigravity adapter — production-ready scaffold.

Antigravity is the IDE used in this project. This adapter provides a scaffold
for future Antigravity Agent automation integration.

Uses ProviderScaffoldAdapter for all lifecycle methods.
execute() raises ProviderNotImplementedError until a live API is available.
"""

from execution.adapters.scaffold import ProviderScaffoldAdapter


class AntigravityAdapter(ProviderScaffoldAdapter):
    """Adapter for Antigravity IDE Agent mode.

    Supports:
      - prepare() — workspace setup, contract/log path creation
      - health_check() — configuration & workspace validation
      - collect_results() — telemetry and output path collection
      - cleanup() — ephemeral state cleanup
      - execute() — raises ProviderNotImplementedError (no live API)
    """

    provider_name: str = "antigravity"
