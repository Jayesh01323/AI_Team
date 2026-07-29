"""
Devin adapter — production-ready scaffold.

Devin is an autonomous AI software engineer. This adapter provides a scaffold
for future Devin API / automation integration.

Uses ProviderScaffoldAdapter for all lifecycle methods.
execute() raises ProviderNotImplementedError until a live API is available.
"""

from execution.adapters.scaffold import ProviderScaffoldAdapter


class DevinAdapter(ProviderScaffoldAdapter):
    """Adapter for Devin (autonomous AI software engineer).

    Supports:
      - prepare() — workspace setup, contract/log path creation
      - health_check() — configuration & workspace validation
      - collect_results() — telemetry and output path collection
      - cleanup() — ephemeral state cleanup
      - execute() — raises ProviderNotImplementedError (no live API)
    """

    provider_name: str = "devin"
