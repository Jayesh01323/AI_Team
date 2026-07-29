import json
from unittest.mock import MagicMock

from execution.adapters.openhands import OpenHandsAdapter
from execution.engine import ExecutionEngine
from execution.validation.pipeline import (
    RuffValidator,
    ValidationEngine,
    ValidationResult,
)
from models.execution import (
    ExecutionContext,
    ExecutionJob,
    ExecutionReport,
    ExecutionResult,
    ExecutionTask,
)
from models.project_context import ProjectContext


def test_correlation_id_generated_and_propagated(tmp_path):
    # 1. Create task & context without explicit correlation_id
    task = ExecutionTask(
        id="task-cid-1", title="Task CID", description="Test correlation id"
    )
    context = ExecutionContext(
        repository=str(tmp_path),
        branch="main",
        task=task,
        provider="openhands",
    )
    assert context.correlation_id is None

    # Mock WorkspaceManager to avoid Git requirement on tmp_path
    mock_workspace_mgr = MagicMock()
    mock_workspace_mgr.create_workspace.return_value = tmp_path

    # Mock ValidationEngine to return successful validation
    mock_val_engine = MagicMock()
    mock_val_engine.validate.return_value = [
        ValidationResult(success=True, validator_name="MockVal", correlation_id=None)
    ]

    engine = ExecutionEngine(
        workspace_manager=mock_workspace_mgr,
        validation_engine=mock_val_engine,
    )

    report = engine.execute(task, context)

    # 2. Verify correlation_id was generated and attached to context & report
    assert report.correlation_id is not None
    assert len(report.correlation_id) > 0
    assert context.correlation_id == report.correlation_id

    # Verify correlation_id was passed to validation engine
    mock_val_engine.validate.assert_called_once_with(
        tmp_path, correlation_id=report.correlation_id
    )


def test_custom_correlation_id_propagation(tmp_path):
    custom_cid = "custom-cid-12345"
    task = ExecutionTask(id="t-2", title="Custom CID", description="Desc")
    context = ExecutionContext(
        repository=str(tmp_path),
        branch="main",
        task=task,
        provider="openhands",
        correlation_id=custom_cid,
    )
    assert context.correlation_id == custom_cid

    # Prepare OpenHandsAdapter directly with custom_cid in context
    adapter = OpenHandsAdapter()
    proj_context = ProjectContext(project_name="proj")
    proj_context.correlation_id = custom_cid
    adapter.context = proj_context
    adapter.prepare(proj_context, tmp_path)

    result = adapter.execute("Run custom cid task")

    # Verify ExecutionResult has correlation_id
    assert result.correlation_id == custom_cid

    # Verify Plaintext Log has correlation_id
    log_content = adapter.log_file_path.read_text(encoding="utf-8")
    assert f"[cid:{custom_cid}]" in log_content

    # Verify Structured JSON Log has correlation_id
    with open(adapter.json_log_path, encoding="utf-8") as f:
        json_entry = json.loads(f.readline())
        assert json_entry["correlation_id"] == custom_cid


def test_validation_result_correlation_id_propagation(tmp_path):
    cid = "val-cid-999"
    validator = RuffValidator()
    val_res = validator.validate(tmp_path, correlation_id=cid)
    assert val_res.correlation_id == cid

    engine = ValidationEngine(validators=[validator])
    res_list = engine.validate(tmp_path, correlation_id=cid)
    assert len(res_list) == 1
    assert res_list[0].correlation_id == cid


def test_backward_compatibility_default_correlation_id():
    # Verify instantiations without correlation_id work cleanly
    task = ExecutionTask(id="t1", title="T1", description="D1")
    context = ExecutionContext(
        repository="repo", branch="main", task=task, provider="openhands"
    )
    job = ExecutionJob(id="j1", task=task, context=context)
    result = ExecutionResult(task_id="t1")
    report = ExecutionReport(
        job_id="j1", provider="openhands", task_id="t1", status="SUCCESS", timing=1.0
    )

    assert context.correlation_id is None
    assert job.correlation_id is None
    assert result.correlation_id is None
    assert report.correlation_id is None
