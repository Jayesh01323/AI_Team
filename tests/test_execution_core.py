from unittest.mock import MagicMock, patch

import pytest

from execution.engine import ExecutionEngine
from execution.workspace import WorkspaceManager
from models.execution import (
    ExecutionContext,
    ExecutionJob,
    ExecutionReport,
    ExecutionResult,
    ExecutionState,
    ExecutionTask,
)


def test_execution_models():
    # Test task
    task = ExecutionTask(
        id="task-123",
        title="Implement database model",
        description="Write Pydantic schema",
        requirements=["python3.11"],
        acceptance_criteria=["must pass pytest"],
    )
    assert task.id == "task-123"
    assert task.title == "Implement database model"

    # Test context
    context = ExecutionContext(
        repository="test_repo",
        branch="main",
        task=task,
        provider="openhands",
        configuration={"key": "val"},
    )
    assert context.repository == "test_repo"
    assert context.provider == "openhands"

    # Test result
    result = ExecutionResult(
        task_id="task-123",
        status="SUCCESS",
        success=True,
        files_changed=["schema.py"],
        commands_executed=["pytest"],
    )
    assert result.success is True
    assert "schema.py" in result.files_changed

    # Test job
    job = ExecutionJob(
        id="job-123",
        task=task,
        context=context,
        status=ExecutionState.PENDING,
    )
    assert job.status == ExecutionState.PENDING

    # Test state transitions
    job.status = ExecutionState.PREPARING
    assert job.status == ExecutionState.PREPARING

    # Test report
    report = ExecutionReport(
        job_id="job-123",
        provider="openhands",
        task_id="task-123",
        status="COMPLETED",
        timing=1.5,
        files_changed=["schema.py"],
        commands_executed=["pytest"],
        validation_status="SUCCESS",
        errors=[],
    )
    assert report.job_id == "job-123"
    assert report.timing == 1.5


def test_workspace_manager(tmp_path):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    repo_dir = projects_dir / "my_project"
    repo_dir.mkdir()
    (repo_dir / "file.txt").write_text("Hello")

    workspaces_dir = tmp_path / "workspaces"

    with patch("execution.workspace.PROJECTS_DIR", projects_dir):
        wm = WorkspaceManager(base_workspaces_dir=workspaces_dir)

        # Verify repository check
        assert wm.verify_repository_exists("my_project") is True
        assert wm.verify_repository_exists("non_existent") is False

        # Create workspace
        ws_path = wm.create_workspace("my_project")
        assert ws_path.exists()
        assert (ws_path / "file.txt").read_text() == "Hello"

        # Cleanup
        wm.cleanup(ws_path)
        assert not ws_path.exists()


def test_execution_engine_success(tmp_path):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    repo_dir = projects_dir / "my_project"
    repo_dir.mkdir()
    (repo_dir / "file.txt").write_text("Hello")
    workspaces_dir = tmp_path / "workspaces"

    task = ExecutionTask(
        id="task-1",
        title="Do Work",
        description="Make change",
    )
    context = ExecutionContext(
        repository="my_project",
        branch="main",
        task=task,
        provider="openhands",
    )

    # Mock adapter
    mock_adapter = MagicMock()
    mock_adapter.execute.return_value = MagicMock(
        exit_code=0,
        status="SUCCESS",
        files_modified=["file.txt"],
        agent_trajectory_summary="Completed task",
        error_log=None,
    )
    mock_adapter.collect_results.return_value = {"duration": 10}

    # Mock validation engine to succeed
    mock_val_engine = MagicMock()
    mock_val_engine.validate.return_value = [
        MagicMock(success=True, validator_name="MockValidator", errors=[])
    ]

    with (
        patch("execution.workspace.PROJECTS_DIR", projects_dir),
        patch(
            "execution.adapters.factory.AdapterFactory.get_adapter",
            return_value=mock_adapter,
        ),
    ):
        wm = WorkspaceManager(base_workspaces_dir=workspaces_dir)
        engine = ExecutionEngine(
            workspace_manager=wm, validation_engine=mock_val_engine
        )

        report = engine.execute(task, context)

        assert report.status == "COMPLETED"
        assert report.validation_status == "SUCCESS"
        assert "file.txt" in report.files_changed
        assert report.provider == "openhands"
        assert mock_adapter.prepare.called
        assert mock_adapter.execute.called
        assert mock_adapter.cleanup.called


def test_execution_engine_validation_error():
    engine = ExecutionEngine()

    task = ExecutionTask(id="", title="", description="")
    context = ExecutionContext(repository="", branch="", task=task, provider="")

    with pytest.raises(ValueError, match="Task fields"):
        engine.execute(task, context)
