import json
from pathlib import Path
from typing import Any

from core.exceptions import ProviderConfigurationError

SUPPORTED_SCHEMA_VERSIONS = {"1.0"}
DEFAULT_SCHEMA_VERSION = "1.0"


def load_and_validate_contract(contract_path: Path) -> dict[str, Any]:
    """Loads a contract JSON file and validates its schema_version.

    Raises:
        ProviderConfigurationError: If the contract file does not exist,
            contains invalid JSON, or specifies an unsupported schema version.

    For backwards compatibility, contracts missing a schema_version field
    default to version '1.0'.
    """
    if not contract_path.exists():
        raise ProviderConfigurationError(
            f"Contract file does not exist: {contract_path}"
        )

    try:
        with open(contract_path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise ProviderConfigurationError(f"Failed to read contract JSON: {e}") from e

    if not isinstance(data, dict):
        raise ProviderConfigurationError("Contract JSON payload must be a JSON object.")

    schema_version = data.get("schema_version", DEFAULT_SCHEMA_VERSION)
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ProviderConfigurationError(
            f"Unsupported contract schema version: '{schema_version}'. Supported versions: {sorted(SUPPORTED_SCHEMA_VERSIONS)}"
        )

    # Ensure schema_version is present on returned dictionary for consistency
    data["schema_version"] = schema_version
    return data
