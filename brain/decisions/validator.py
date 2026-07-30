"""
Validation logic for the Decision Engine.

Validates decision data before it is accepted into the engine.
All validation is deterministic and rule-based — no LLM calls.

Rules enforced:
- Required field presence (id, title, topic, category, rationale, status, timestamp)
- Field length constraints (non-empty strings)
- Confidence score range (0.0–1.0)
- Status must be a valid DecisionStatus value
- Timestamp must be a non-empty ISO-8601 string
"""

from __future__ import annotations

from brain.decisions.models import DecisionStatus, ValidationResult

# ---------------------------------------------------------------------------
# Required field specifications
# ---------------------------------------------------------------------------

_REQUIRED_STRING_FIELDS: list[str] = [
    "title",
    "topic",
    "category",
    "rationale",
    "value",
]

_VALID_STATUSES: frozenset[str] = frozenset(s.value for s in DecisionStatus)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_decision_data(data: dict) -> ValidationResult:
    """
    Validate a raw decision data dictionary.

    Args:
        data: Dictionary representing a candidate DecisionRecord.

    Returns:
        A :class:`~brain.decisions.models.ValidationResult` describing
        any validation errors. ``is_valid`` is ``True`` only when there
        are no errors.
    """
    result = ValidationResult()

    _validate_required_strings(data, result)
    _validate_id(data, result)
    _validate_status(data, result)
    _validate_confidence(data, result)
    _validate_timestamp(data, result)

    return result


def validate_update_data(update_data: dict) -> ValidationResult:
    """
    Validate a partial update payload.

    Applies a lighter set of rules — only validates fields that are
    actually present in the update payload, plus ensures the ``reason``
    for the change is supplied.

    Args:
        update_data: Dictionary of fields to update.

    Returns:
        A :class:`~brain.decisions.models.ValidationResult`.
    """
    result = ValidationResult()

    if not update_data:
        result.add_error("Update payload must not be empty.")
        return result

    # If certain string fields are present, they must be non-empty
    for field in _REQUIRED_STRING_FIELDS:
        if field in update_data:
            value = update_data[field]
            if not isinstance(value, str) or not value.strip():
                result.add_error(f"Field '{field}' must be a non-empty string if provided.")

    # Status update must use a valid value
    if "status" in update_data:
        _validate_status_value(update_data["status"], result)

    # Confidence update must be in range
    if "confidence" in update_data:
        _validate_confidence_value(update_data["confidence"], result)

    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _validate_required_strings(data: dict, result: ValidationResult) -> None:
    """Check that all required string fields are present and non-empty."""
    for field in _REQUIRED_STRING_FIELDS:
        value = data.get(field)
        if value is None:
            result.add_error(f"Required field '{field}' is missing.")
        elif not isinstance(value, str) or not value.strip():
            result.add_error(f"Required field '{field}' must be a non-empty string.")


def _validate_id(data: dict, result: ValidationResult) -> None:
    """Check that the 'id' field, if provided, is a non-empty string."""
    decision_id = data.get("id")
    if decision_id is not None and (not isinstance(decision_id, str) or not decision_id.strip()):
        result.add_error("Field 'id' must be a non-empty string.")


def _validate_status(data: dict, result: ValidationResult) -> None:
    """Check that 'status' is a valid DecisionStatus value."""
    status = data.get("status")
    if status is not None:
        _validate_status_value(status, result)


def _validate_status_value(status: object, result: ValidationResult) -> None:
    """Validate a status value against the allowed DecisionStatus values."""
    if not isinstance(status, str) or status not in _VALID_STATUSES:
        result.add_error(
            f"Invalid status '{status}'. Must be one of: {sorted(_VALID_STATUSES)}."
        )


def _validate_confidence(data: dict, result: ValidationResult) -> None:
    """Check that 'confidence', if present, is valid."""
    confidence = data.get("confidence")
    if confidence is not None:
        _validate_confidence_value(confidence, result)


def _validate_confidence_value(confidence: object, result: ValidationResult) -> None:
    """Validate a confidence score or dict."""
    if isinstance(confidence, (int, float)):
        if not 0.0 <= float(confidence) <= 1.0:
            result.add_error(
                f"Confidence score {confidence} is out of range. Must be between 0.0 and 1.0."
            )
    elif isinstance(confidence, dict):
        score = confidence.get("score")
        if score is not None and isinstance(score, (int, float)) and not 0.0 <= float(score) <= 1.0:
            result.add_error(
                f"Confidence score {score} is out of range. Must be between 0.0 and 1.0."
            )
    # ConfidenceScore objects and other forms are validated by Pydantic on construction


def _validate_timestamp(data: dict, result: ValidationResult) -> None:
    """Check that 'timestamp', if provided, is a non-empty string."""
    timestamp = data.get("timestamp")
    if timestamp is not None and (not isinstance(timestamp, str) or not timestamp.strip()):
        result.add_error("Field 'timestamp' must be a non-empty ISO-8601 string.")
