"""
Unit and integration tests for Autonomous Orchestrator (M6-TASK-005).
"""

from pathlib import Path
from unittest.mock import MagicMock

from core.exceptions import ProviderAuthenticationError
from execution.engine import ExecutionEngine
from models.execution import (
    ExecutionReport,
    ExecutionTask,
)
from models.project_context import ProjectContext
from models.task_plan import Epic, Story, TaskPlan
from models.task_plan import Task as PlanTask
from pipeline.autonomous import (
    AutonomousOrchestrator,
    AutonomousState,
    extract_execution_tasks,
)


def test_extract_execution_tasks() -> None:
    """Extracts ExecutionTask list from canonical TaskPlan."""
    plan = TaskPlan(
        project_title="Test App",
        epics=[
            Epic(
                title="Auth Epic",
                description="Authentication features",
                stories=[
                    Story(
                        title="Login Story",
                        description="User login flow",
                        priority="High",
                        tasks=[
                            PlanTask(
                                title="Login UI",
                                description="Create login form",
                                priority="High",
                                acceptance_criteria=["Renders inputs"],
                            )
                        ],
                    )
                ],
            )
        ],
    )

    tasks = extract_execution_tasks(plan)
    assert len(tasks) == 1
    assert tasks[0].id == "task-001"
    assert tasks[0].title == "Login UI"
    assert "Auth Epic > Login Story" in tasks[0].description
    assert tasks[0].acceptance_criteria == ["Renders inputs"]


def test_empty_workflow() -> None:
    """Empty task list returns COMPLETED status immediately."""
    orchestrator = AutonomousOrchestrator()
    report = orchestrator.execute_workflow(tasks=[])

    assert report.status == AutonomousState.COMPLETED
    assert len(report.task_reports) == 0
    assert report.timing >= 0.0


def test_successful_workflow_execution(tmp_path: Path) -> None:
    """Executes a 2-task workflow successfully with deterministic stage records."""
    mock_exec_engine = MagicMock(spec=ExecutionEngine)

    report_t1 = ExecutionReport(
        job_id="j1",
        provider="mock",
        task_id="task-001",
        status="COMPLETED",
        timing=0.1,
        files_changed=["app.py"],
        validation_status="SUCCESS",
        retries=0,
    )
    report_t2 = ExecutionReport(
        job_id="j2",
        provider="mock",
        task_id="task-002",
        status="COMPLETED",
        timing=0.1,
        files_changed=["test_app.py"],
        validation_status="SUCCESS",
        retries=0,
    )

    mock_exec_engine.execute.side_effect = [report_t1, report_t2]

    orchestrator = AutonomousOrchestrator(execution_engine=mock_exec_engine)

    tasks = [
        ExecutionTask(id="task-001", title="Task 1", description="Build app"),
        ExecutionTask(id="task-002", title="Task 2", description="Test app"),
    ]

    report = orchestrator.execute_workflow(
        project_name="demo-proj",
        tasks=tasks,
        provider="mock",
    )

    assert report.status == AutonomousState.COMPLETED
    assert len(report.task_reports) == 2
    assert report.files_changed == ["app.py", "test_app.py"]
    assert report.errors == []

    # Check stage ordering
    stage_names = [s.stage_name for s in report.stages]
    assert stage_names == [
        "PREPARING",
        "EXECUTING_task-001",
        "VALIDATING_task-001",
        "EXECUTING_task-002",
        "VALIDATING_task-002",
    ]


def test_validation_failure_stops_workflow() -> None:
    """Validation failure on first task stops subsequent task execution."""
    mock_exec_engine = MagicMock(spec=ExecutionEngine)

    report_fail = ExecutionReport(
        job_id="j1",
        provider="mock",
        task_id="task-001",
        status="COMPLETED",
        timing=0.1,
        files_changed=["app.py"],
        validation_status="FAILED",
        errors=["SyntaxError in app.py"],
        retries=0,
    )

    mock_exec_engine.execute.return_value = report_fail

    orchestrator = AutonomousOrchestrator(execution_engine=mock_exec_engine)

    tasks = [
        ExecutionTask(id="task-001", title="Task 1", description="Build app"),
        ExecutionTask(id="task-002", title="Task 2", description="Test app"),
    ]

    report = orchestrator.execute_workflow(
        project_name="demo-proj",
        tasks=tasks,
        max_retries=0,
    )

    assert report.status == AutonomousState.FAILED
    assert len(report.task_reports) == 1
    assert "Task task-001 failed" in report.errors[0]
    assert mock_exec_engine.execute.call_count == 1


def test_successful_recovery_stage_recorded() -> None:
    """Task that retries and succeeds records a RECOVERING stage."""
    mock_exec_engine = MagicMock(spec=ExecutionEngine)

    report_recovered = ExecutionReport(
        job_id="j1",
        provider="mock",
        task_id="task-001",
        status="COMPLETED",
        timing=0.2,
        files_changed=["app.py"],
        validation_status="SUCCESS",
        retries=1,
        recovery_metadata={"category": "RECOVERABLE_VALIDATION"},
    )

    mock_exec_engine.execute.return_value = report_recovered

    orchestrator = AutonomousOrchestrator(execution_engine=mock_exec_engine)
    tasks = [ExecutionTask(id="task-001", title="Task 1", description="Fix code")]

    report = orchestrator.execute_workflow(tasks=tasks, max_retries=3)

    assert report.status == AutonomousState.COMPLETED
    assert report.task_reports[0].retries == 1

    stage_names = [s.stage_name for s in report.stages]
    assert "RECOVERING_task-001" in stage_names


def test_unrecoverable_exception_handling() -> None:
    """Unrecoverable exception (e.g. Auth error) marks stage and workflow as FAILED."""
    mock_exec_engine = MagicMock(spec=ExecutionEngine)
    mock_exec_engine.execute.side_effect = ProviderAuthenticationError(
        "Invalid API Key"
    )

    orchestrator = AutonomousOrchestrator(execution_engine=mock_exec_engine)
    tasks = [ExecutionTask(id="task-001", title="Task 1", description="Build app")]

    report = orchestrator.execute_workflow(tasks=tasks)

    assert report.status == AutonomousState.FAILED
    assert "Invalid API Key" in report.errors[0]


def test_brain_planning_integration_flow() -> None:
    """Runs complete flow from raw_idea through mock PipelineEngine and ExecutionEngine."""
    mock_pipeline_engine = MagicMock()

    dummy_plan = TaskPlan(
        project_title="SaaS App",
        epics=[
            Epic(
                title="Core Epic",
                description="Core features",
                stories=[
                    Story(
                        title="Backend",
                        description="Setup FastAPI",
                        priority="High",
                        tasks=[
                            PlanTask(
                                title="Init DB",
                                description="Setup Postgres schema",
                                priority="High",
                            )

                        ],
                    )
                ],
            )
        ],
    )

    def mock_run_brain(ctx: ProjectContext) -> ProjectContext:
        ctx.task_plan = dummy_plan
        return ctx

    mock_pipeline_engine.run.side_effect = mock_run_brain

    mock_exec_engine = MagicMock(spec=ExecutionEngine)
    mock_exec_engine.execute.return_value = ExecutionReport(
        job_id="j1",
        provider="mock",
        task_id="task-001",
        status="COMPLETED",
        timing=0.1,
        files_changed=["db.py"],
        validation_status="SUCCESS",
    )

    orchestrator = AutonomousOrchestrator(
        pipeline_engine=mock_pipeline_engine,
        execution_engine=mock_exec_engine,
    )

    report = orchestrator.execute_workflow(
        raw_idea="Build a SaaS backend in FastAPI",
        project_name="saas-backend",
    )

    assert report.status == AutonomousState.COMPLETED
    assert report.project_name == "saas-backend"
    assert report.idea == "Build a SaaS backend in FastAPI"
    assert len(report.task_reports) == 1
    assert report.task_reports[0].task_id == "task-001"
    assert "PLANNING" in [s.stage_name for s in report.stages]


def test_report_serialization() -> None:
    """Verifies report.to_dict() produces valid serializable dictionary."""
    orchestrator = AutonomousOrchestrator()
    report = orchestrator.execute_workflow(tasks=[])

    d = report.to_dict()
    assert d["status"] == "COMPLETED"
    assert isinstance(d["stages"], list)
    assert isinstance(d["task_reports"], list)
    assert "orchestrator_id" in d
