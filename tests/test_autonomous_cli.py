"""
Unit and integration tests for Autonomous CLI (M6-TASK-006).
"""

import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from cli.main import cli
from models.execution import ExecutionReport
from pipeline.autonomous import (
    AutonomousExecutionReport,
    AutonomousState,
    StageRecord,
)


def test_cli_run_empty_idea() -> None:
    """Invoking run with an empty string returns error and exit code 1."""
    runner = CliRunner()
    result = runner.invoke(cli, ["run", ""])

    assert result.exit_code == 1
    assert "ERROR: Project idea cannot be empty." in result.output


def test_cli_run_successful_flow() -> None:
    """Invoking run with valid idea executes AutonomousOrchestrator and prints summary."""
    runner = CliRunner()

    stage1 = StageRecord(
        stage_name="PLANNING", status="COMPLETED", started_at=1.0, completed_at=1.5
    )
    stage2 = StageRecord(
        stage_name="EXECUTING_task-001",
        status="COMPLETED",
        started_at=1.5,
        completed_at=2.0,
    )

    mock_report = AutonomousExecutionReport(
        orchestrator_id="orch-123",
        idea="Build a CRM app",
        project_name="build-a-crm-app",
        status=AutonomousState.COMPLETED,
        stages=[stage1, stage2],
        task_reports=[
            ExecutionReport(
                job_id="j1",
                provider="openhands",
                task_id="task-001",
                status="COMPLETED",
                timing=0.5,
                files_changed=["main.py"],
                validation_status="SUCCESS",
                retries=0,
            )
        ],
        timing=1.0,
        files_changed=["main.py"],
        errors=[],
        correlation_id="cid-999",
    )

    with patch("pipeline.autonomous.AutonomousOrchestrator") as MockOrchestratorClass:
        mock_instance = MagicMock()
        mock_instance.execute_workflow.return_value = mock_report
        MockOrchestratorClass.return_value = mock_instance

        result = runner.invoke(cli, ["run", "Build a CRM app"])

        assert result.exit_code == 0
        assert "=== Running Autonomous AI Engineering Pipeline ===" in result.output
        assert "AUTONOMOUS EXECUTION SUMMARY" in result.output
        assert "✓ PLANNING" in result.output
        assert "Status:           COMPLETED" in result.output
        assert "Files Changed:    1 ['main.py']" in result.output
        assert "SUCCESS: Autonomous workflow completed successfully." in result.output

        mock_instance.execute_workflow.assert_called_once_with(
            raw_idea="Build a CRM app",
            project_name="build-a-crm-app",
            provider="openhands",
            max_retries=3,
        )


def test_cli_run_custom_options() -> None:
    """Invoking run with custom --project-name, --provider, and --max-retries options."""
    runner = CliRunner()

    mock_report = AutonomousExecutionReport(
        orchestrator_id="orch-123",
        idea="Build a web app",
        project_name="custom-name",
        status=AutonomousState.COMPLETED,
        stages=[],
        task_reports=[],
        timing=0.2,
        files_changed=[],
    )

    with patch("pipeline.autonomous.AutonomousOrchestrator") as MockOrchestratorClass:
        mock_instance = MagicMock()
        mock_instance.execute_workflow.return_value = mock_report
        MockOrchestratorClass.return_value = mock_instance

        result = runner.invoke(
            cli,
            [
                "run",
                "Build a web app",
                "-p",
                "custom-name",
                "--provider",
                "claude",
                "--max-retries",
                "5",
            ],
        )

        assert result.exit_code == 0
        assert 'Project:  "custom-name"' in result.output
        assert 'Provider: "claude"' in result.output

        mock_instance.execute_workflow.assert_called_once_with(
            raw_idea="Build a web app",
            project_name="custom-name",
            provider="claude",
            max_retries=5,
        )


def test_cli_run_json_telemetry_output() -> None:
    """Invoking run with --json outputs raw telemetry JSON."""
    runner = CliRunner()

    mock_report = AutonomousExecutionReport(
        orchestrator_id="orch-json-456",
        idea="API Microservice",
        project_name="api-microservice",
        status=AutonomousState.COMPLETED,
        stages=[
            StageRecord(
                stage_name="PLANNING",
                status="COMPLETED",
                started_at=1.0,
                completed_at=1.2,
            )
        ],
        task_reports=[],
        timing=0.2,
        files_changed=["api.py"],
    )

    with patch("pipeline.autonomous.AutonomousOrchestrator") as MockOrchestratorClass:
        mock_instance = MagicMock()
        mock_instance.execute_workflow.return_value = mock_report
        MockOrchestratorClass.return_value = mock_instance

        result = runner.invoke(cli, ["run", "API Microservice", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["orchestrator_id"] == "orch-json-456"
        assert data["status"] == "COMPLETED"
        assert data["files_changed"] == ["api.py"]


def test_cli_run_orchestrator_failure() -> None:
    """Invoking run when orchestrator fails exits with code 1."""
    runner = CliRunner()

    mock_report = AutonomousExecutionReport(
        orchestrator_id="orch-fail",
        idea="Broken app",
        project_name="broken-app",
        status=AutonomousState.FAILED,
        stages=[
            StageRecord(
                stage_name="PLANNING",
                status="FAILED",
                started_at=1.0,
                completed_at=1.1,
            )
        ],
        task_reports=[],
        timing=0.1,
        errors=["Syntax error in blueprint"],
    )

    with patch("pipeline.autonomous.AutonomousOrchestrator") as MockOrchestratorClass:
        mock_instance = MagicMock()
        mock_instance.execute_workflow.return_value = mock_report
        MockOrchestratorClass.return_value = mock_instance

        result = runner.invoke(cli, ["run", "Broken app"])

        assert result.exit_code == 1
        assert "Status:           FAILED" in result.output
        assert "Errors:" in result.output
        assert "- Syntax error in blueprint" in result.output
        assert "FAILED: Autonomous workflow encountered errors." in result.output


def test_cli_run_recovery_telemetry() -> None:
    """Invoking run displays total retries and recovery status."""
    runner = CliRunner()

    mock_report = AutonomousExecutionReport(
        orchestrator_id="orch-rec",
        idea="Self healing test",
        project_name="self-healing-test",
        status=AutonomousState.COMPLETED,
        stages=[],
        task_reports=[
            ExecutionReport(
                job_id="j1",
                provider="openhands",
                task_id="task-001",
                status="COMPLETED",
                timing=0.4,
                files_changed=["healed.py"],
                validation_status="SUCCESS",
                retries=2,
            )
        ],
        timing=0.4,
        files_changed=["healed.py"],
    )

    with patch("pipeline.autonomous.AutonomousOrchestrator") as MockOrchestratorClass:
        mock_instance = MagicMock()
        mock_instance.execute_workflow.return_value = mock_report
        MockOrchestratorClass.return_value = mock_instance

        result = runner.invoke(cli, ["run", "Self healing test"])

        assert result.exit_code == 0
        assert "Total Retries:    2" in result.output
        assert "Validation:       SUCCESS" in result.output


def test_cli_backward_compatibility() -> None:
    """Existing commands (e.g. init --help) continue to work properly."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "init" in result.output
    assert "analyze" in result.output
    assert "generate" in result.output
    assert "pipeline" in result.output
    assert "run" in result.output
