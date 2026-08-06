"""
Unit and integration tests for Self-Healing Error Recovery Engine (M6-TASK-003).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
)
from execution.engine import ExecutionEngine
from execution.recovery.self_healing import (
    FailureCategory,
    RecoveryAttempt,
    SelfHealingEngine,
)
from execution.validation.pipeline import ValidationResult
from models.execution import (
    ExecutionContext,
    ExecutionResult,
    ExecutionTask,
)


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "ws"
    ws.mkdir(parents=True, exist_ok=True)
    return ws


def test_classify_failure_none() -> None:
    """Classifies successful execution and validation as NONE."""
    engine = SelfHealingEngine()
    result = ExecutionResult(task_id="t1", status="SUCCESS", exit_code=0)
    val_results = [ValidationResult(success=True, validator_name="Ruff")]

    category, _reason, errors = engine.classify_failure(result, val_results)
    assert category == FailureCategory.NONE
    assert errors == []


def test_classify_failure_recoverable_validation() -> None:
    """Classifies failed validation results as RECOVERABLE_VALIDATION."""
    engine = SelfHealingEngine()
    result = ExecutionResult(task_id="t1", status="SUCCESS", exit_code=0)
    val_results = [
        ValidationResult(
            success=False, validator_name="RuffLinter", errors=["Line too long"]
        )
    ]

    category, reason, errors = engine.classify_failure(result, val_results)
    assert category == FailureCategory.RECOVERABLE_VALIDATION
    assert "RuffLinter" in reason
    assert errors == ["Line too long"]


def test_classify_failure_recoverable_execution() -> None:
    """Classifies adapter execution failure as RECOVERABLE_EXECUTION."""
    engine = SelfHealingEngine()
    result = ExecutionResult(
        task_id="t1", status="FAILED", exit_code=1, error_log="Runtime error"
    )

    category, reason, _errors = engine.classify_failure(result, [])
    assert category == FailureCategory.RECOVERABLE_EXECUTION
    assert "Adapter execution failed" in reason



def test_classify_failure_non_recoverable_exception() -> None:
    """Classifies non-recoverable exceptions (e.g. Auth errors) as NON_RECOVERABLE."""
    engine = SelfHealingEngine()
    auth_err = ProviderAuthenticationError("Invalid API key")

    category, reason, errors = engine.classify_failure(None, [], exception=auth_err)
    assert category == FailureCategory.NON_RECOVERABLE
    assert "ProviderAuthenticationError" in reason
    assert errors == ["Invalid API key"]


def test_evaluate_recovery_successful_first_try() -> None:
    """Successful execution on attempt 1 requires 0 retries."""
    engine = SelfHealingEngine(max_retries=3)
    result = ExecutionResult(task_id="t1", status="SUCCESS", exit_code=0)
    val_results = [ValidationResult(success=True, validator_name="Ruff")]

    decision = engine.evaluate_recovery(
        original_instruction="Build API",
        adapter_result=result,
        validation_results=val_results,
        current_attempt=1,
    )

    assert decision.should_retry is False
    assert decision.category == FailureCategory.NONE
    assert decision.remediation_prompt is None


def test_evaluate_recovery_retry_triggered() -> None:
    """Recoverable failure on attempt 1 triggers retry with remediation prompt."""
    engine = SelfHealingEngine(max_retries=3)
    val_results = [
        ValidationResult(
            success=False, validator_name="Pytest", errors=["test_foo failed"]
        )
    ]

    decision = engine.evaluate_recovery(
        original_instruction="Write function foo()",
        adapter_result=ExecutionResult(task_id="t1", status="SUCCESS", exit_code=0),
        validation_results=val_results,
        current_attempt=1,
    )

    assert decision.should_retry is True
    assert decision.category == FailureCategory.RECOVERABLE_VALIDATION
    assert decision.attempt == 2
    assert decision.remediation_prompt is not None
    assert "RECOVERY ATTEMPT 2/3" in decision.remediation_prompt
    assert "test_foo failed" in decision.remediation_prompt


def test_evaluate_recovery_retry_limit_exhausted() -> None:
    """Reaching max_retries limit prevents further retries."""
    engine = SelfHealingEngine(max_retries=3)
    val_results = [
        ValidationResult(
            success=False, validator_name="Pytest", errors=["test_foo failed"]
        )
    ]

    decision = engine.evaluate_recovery(
        original_instruction="Write function foo()",
        adapter_result=ExecutionResult(task_id="t1", status="SUCCESS", exit_code=0),
        validation_results=val_results,
        current_attempt=3,
    )

    assert decision.should_retry is False
    assert decision.category == FailureCategory.RETRY_EXHAUSTED
    assert "Retry limit exhausted" in decision.reason


def test_evaluate_recovery_non_recoverable_immediate_stop() -> None:
    """Non-recoverable error stops execution immediately without retries."""
    engine = SelfHealingEngine(max_retries=3)
    config_err = ProviderConfigurationError("Invalid timeout setting")

    decision = engine.evaluate_recovery(
        original_instruction="Task instruction",
        adapter_result=None,
        validation_results=[],
        current_attempt=1,
        exception=config_err,
    )

    assert decision.should_retry is False
    assert decision.category == FailureCategory.NON_RECOVERABLE


def test_recovery_history_tracking() -> None:
    """Evaluations append structured RecoveryAttempt records to history."""
    engine = SelfHealingEngine(max_retries=3)
    val_results = [
        ValidationResult(
            success=False, validator_name="Ruff", errors=["Syntax error"]
        )
    ]

    history: list[RecoveryAttempt] = []

    # Attempt 1
    d1 = engine.evaluate_recovery(
        "Instruction", None, val_results, 1, history=history
    )
    assert len(d1.history) == 1
    assert d1.history[0].attempt == 1
    assert d1.history[0].category == FailureCategory.RECOVERABLE_VALIDATION

    # Attempt 2
    d2 = engine.evaluate_recovery(
        "Instruction", None, val_results, 2, history=d1.history
    )
    assert len(d2.history) == 2
    assert d2.history[1].attempt == 2


def test_execution_engine_integration_self_healing_retry(
    tmp_path: Path,
) -> None:
    """ExecutionEngine retries task when validation fails and succeeds on 2nd attempt."""
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    repo_dir = projects_dir / "my_project"
    repo_dir.mkdir()

    task = ExecutionTask(id="task-recovery", title="Fix Code", description="Fix bug")

    context = ExecutionContext(
        repository="my_project", branch="main", task=task, provider="mock"
    )

    mock_adapter = MagicMock()

    # Turn 1 fails validation, Turn 2 succeeds
    val_result_fail = [ValidationResult(success=False, validator_name="Ruff", errors=["Syntax error"])]
    val_result_pass = [ValidationResult(success=True, validator_name="Ruff")]

    mock_val_engine = MagicMock()
    mock_val_engine.validate.side_effect = [val_result_fail, val_result_pass]

    mock_adapter.execute.return_value = MagicMock(
        exit_code=0,
        status="SUCCESS",
        files_modified=["app.py"],
        agent_trajectory_summary="Fixed app.py",
        error_log=None,
    )
    mock_adapter.collect_results.return_value = {}

    with (
        patch("execution.workspace.PROJECTS_DIR", projects_dir),
        patch(
            "execution.adapters.factory.AdapterFactory.get_adapter",
            return_value=mock_adapter,
        ),
    ):
        engine = ExecutionEngine(validation_engine=mock_val_engine)

        report = engine.execute(task, context, max_retries=2)

        assert report.status == "COMPLETED"
        assert report.validation_status == "SUCCESS"
        assert report.retries == 1
        assert report.recovery_metadata["category"] == FailureCategory.NONE.value
        assert mock_adapter.execute.call_count == 2
