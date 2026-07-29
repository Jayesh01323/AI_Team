from pathlib import Path
from unittest.mock import MagicMock, patch

from execution.engine import ExecutionEngine
from execution.validation.pipeline import (
    PytestValidator,
    RuffFormatValidator,
    RuffValidator,
    ValidationEngine,
    ValidationResult,
)
from execution.workspace import WorkspaceManager
from models.execution import ExecutionContext, ExecutionTask


def test_validation_result():
    result = ValidationResult(
        success=True, validator_name="TestVal", errors=[], output="ok"
    )
    assert result.success is True
    assert result.validator_name == "TestVal"


def test_validation_engine():
    mock_val1 = MagicMock()
    mock_val1.name = "Val1"
    mock_val1.validate.return_value = ValidationResult(
        success=True, validator_name="Val1"
    )

    mock_val2 = MagicMock()
    mock_val2.name = "Val2"
    mock_val2.validate.return_value = ValidationResult(
        success=False, validator_name="Val2", errors=["Error 2"]
    )

    engine = ValidationEngine(validators=[mock_val1, mock_val2])
    results = engine.validate(Path("/dummy"))

    assert len(results) == 2
    assert results[0].success is True
    assert results[1].success is False
    assert results[1].errors == ["Error 2"]


@patch("subprocess.run")
def test_ruff_validator_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="All clean", stderr="")
    validator = RuffValidator()
    result = validator.validate(Path("/dummy"))
    assert result.success is True
    assert result.output == "All clean"


@patch("subprocess.run")
def test_ruff_validator_failure(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout="Linter error", stderr="")
    validator = RuffValidator()
    result = validator.validate(Path("/dummy"))
    assert result.success is False
    assert "Linter error" in result.errors[0]


@patch("subprocess.run")
def test_ruff_format_validator(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="Formatted", stderr="")
    validator = RuffFormatValidator()
    result = validator.validate(Path("/dummy"))
    assert result.success is True


@patch("subprocess.run")
def test_pytest_validator(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout="Test failed", stderr="")
    validator = PytestValidator()
    result = validator.validate(Path("/dummy"))
    assert result.success is False
    assert "Test failed" in result.errors[0]


def test_engine_integration_validation_failure(tmp_path):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    repo_dir = projects_dir / "my_project"
    repo_dir.mkdir()

    task = ExecutionTask(id="task-1", title="Do Work", description="Make change")
    context = ExecutionContext(
        repository="my_project",
        branch="main",
        task=task,
        provider="openhands",
    )

    mock_adapter = MagicMock()
    mock_adapter.execute.return_value = MagicMock(
        exit_code=0,
        status="SUCCESS",
        files_modified=["file.txt"],
        agent_trajectory_summary="Completed",
        error_log=None,
    )
    mock_adapter.collect_results.return_value = {}

    mock_validator = MagicMock()
    mock_validator.name = "FailingValidator"
    mock_validator.validate.return_value = ValidationResult(
        success=False, validator_name="FailingValidator", errors=["Failed lint check"]
    )
    val_engine = ValidationEngine(validators=[mock_validator])

    with (
        patch("execution.workspace.PROJECTS_DIR", projects_dir),
        patch(
            "execution.adapters.factory.AdapterFactory.get_adapter",
            return_value=mock_adapter,
        ),
    ):
        wm = WorkspaceManager(base_workspaces_dir=tmp_path / "workspaces")
        engine = ExecutionEngine(workspace_manager=wm, validation_engine=val_engine)

        report = engine.execute(task, context)

        assert report.status == "COMPLETED"
        assert report.validation_status == "FAILED"
        assert "Failed lint check" in report.errors
