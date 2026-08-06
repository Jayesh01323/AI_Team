"""
Unit and integration tests for ParallelValidationEngine (M6-TASK-004).
"""

import time
from pathlib import Path

import pytest

from execution.validation.parallel import ParallelValidationEngine
from execution.validation.pipeline import ValidationEngine, ValidationResult, Validator


class SlowMockValidator(Validator):
    """Mock validator that sleeps for a short duration to simulate I/O or subprocess work."""

    def __init__(self, name: str, sleep_sec: float = 0.1, success: bool = True) -> None:
        self._name = name
        self.sleep_sec = sleep_sec
        self.success = success

    @property
    def name(self) -> str:
        return self._name

    def validate(
        self, workspace_path: Path, correlation_id: str | None = None
    ) -> ValidationResult:
        time.sleep(self.sleep_sec)
        errors = [] if self.success else [f"{self._name} error"]
        return ValidationResult(
            success=self.success,
            validator_name=self.name,
            errors=errors,
            output=f"Output from {self.name}",
            correlation_id=correlation_id,
        )


class FaultyValidator(Validator):
    """Validator that raises an unhandled Exception during execution."""

    @property
    def name(self) -> str:
        return "FaultyValidator"

    def validate(
        self, workspace_path: Path, correlation_id: str | None = None
    ) -> ValidationResult:
        raise RuntimeError("Unexpected internal crashes")


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "ws"
    ws.mkdir()
    return ws


def test_empty_validator_list(temp_workspace: Path) -> None:
    """Engine with empty validator list returns empty results list."""
    engine = ParallelValidationEngine(validators=[])
    results = engine.validate(temp_workspace, correlation_id="cid-1")
    assert results == []


def test_single_validator_sequential_fallback(temp_workspace: Path) -> None:
    """Engine with a single validator automatically falls back to sequential path."""
    v1 = SlowMockValidator("V1", sleep_sec=0.01)
    engine = ParallelValidationEngine(validators=[v1])

    results = engine.validate(temp_workspace, correlation_id="cid-single")
    assert len(results) == 1
    assert results[0].validator_name == "V1"
    assert results[0].success is True
    assert results[0].correlation_id == "cid-single"


def test_multiple_validators_parallel_execution_and_deterministic_ordering(
    temp_workspace: Path,
) -> None:
    """Multiple validators execute in parallel while returning results in exact registered order."""
    # V1 takes 0.2s, V2 takes 0.05s, V3 takes 0.1s
    v1 = SlowMockValidator("V1", sleep_sec=0.2, success=True)
    v2 = SlowMockValidator("V2", sleep_sec=0.05, success=False)
    v3 = SlowMockValidator("V3", sleep_sec=0.1, success=True)

    engine = ParallelValidationEngine(validators=[v1, v2, v3], max_workers=3)

    start = time.time()
    results = engine.validate(temp_workspace, correlation_id="cid-multi")
    elapsed = time.time() - start

    # Check deterministic ordering: V1, V2, V3 regardless of finish order (V2 finished first)
    assert [r.validator_name for r in results] == ["V1", "V2", "V3"]
    assert results[0].success is True
    assert results[1].success is False
    assert results[1].errors == ["V2 error"]
    assert results[2].success is True

    # Performance sanity check: Max time should be ~0.2s (longest worker), NOT 0.2 + 0.05 + 0.1 = 0.35s
    assert elapsed < 0.32


def test_sequential_fallback_flag(temp_workspace: Path) -> None:
    """Disabling parallel execution explicitly forces sequential mode."""
    v1 = SlowMockValidator("V1", sleep_sec=0.05)
    v2 = SlowMockValidator("V2", sleep_sec=0.05)

    engine = ParallelValidationEngine(validators=[v1, v2], parallel=False)
    results = engine.validate(temp_workspace, parallel=False)

    assert len(results) == 2
    assert [r.validator_name for r in results] == ["V1", "V2"]


def test_validator_exception_handling(temp_workspace: Path) -> None:
    """Unhandled validator exceptions are caught safely without failing other validators."""
    v1 = SlowMockValidator("V1", sleep_sec=0.01, success=True)
    faulty = FaultyValidator()
    v3 = SlowMockValidator("V3", sleep_sec=0.01, success=True)

    engine = ParallelValidationEngine(validators=[v1, faulty, v3])
    results = engine.validate(temp_workspace, correlation_id="cid-faulty")

    assert len(results) == 3
    assert results[0].success is True
    assert results[1].success is False
    assert results[1].validator_name == "FaultyValidator"
    assert "Validator failed with internal error: Unexpected internal crashes" in results[1].errors[0]
    assert results[2].success is True


def test_mixed_pass_fail_validators(temp_workspace: Path) -> None:
    """Results from mixed pass/fail validators match sequential engine output identically."""
    v1 = SlowMockValidator("V1", sleep_sec=0.01, success=True)
    v2 = SlowMockValidator("V2", sleep_sec=0.01, success=False)

    sequential_engine = ValidationEngine(validators=[v1, v2])
    parallel_engine = ParallelValidationEngine(validators=[v1, v2])

    seq_results = sequential_engine.validate(temp_workspace, correlation_id="test-cid")
    par_results = parallel_engine.validate(temp_workspace, correlation_id="test-cid")

    assert len(seq_results) == len(par_results) == 2
    for s, p in zip(seq_results, par_results, strict=True):
        assert s.validator_name == p.validator_name
        assert s.success == p.success
        assert s.errors == p.errors
        assert s.correlation_id == p.correlation_id


def test_api_compatibility() -> None:
    """ParallelValidationEngine is a valid subclass of ValidationEngine."""
    engine = ParallelValidationEngine()
    assert isinstance(engine, ValidationEngine)
    assert len(engine.validators) == 3  # Default Ruff, RuffFormat, Pytest validators
