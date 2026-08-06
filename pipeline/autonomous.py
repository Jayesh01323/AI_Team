"""
Autonomous Orchestrator — End-to-End Autonomous Software Engineering Pipeline.

Coordinates the complete workflow across:
  Engineering Brain (PipelineEngine)
    -> Execution Engine (ExecutionEngine)
      -> Workspace Diff Engine (WorkspaceDiffTracker)
        -> Parallel Validation Engine (ParallelValidationEngine)
          -> Self-Healing Engine (SelfHealingEngine)
            -> Autonomous Execution Report
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core.logging import get_logger
from execution.engine import ExecutionEngine
from models.execution import (
    ExecutionContext,
    ExecutionReport,
    ExecutionTask,
)
from models.project_context import ProjectContext
from models.task_plan import TaskPlan
from pipeline.engine import PipelineEngine

logger = get_logger(__name__)


class AutonomousState(str, Enum):
    INITIALIZED = "INITIALIZED"
    PLANNING = "PLANNING"
    PREPARING = "PREPARING"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    RECOVERING = "RECOVERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class StageRecord:
    stage_name: str
    status: str  # RUNNING, COMPLETED, FAILED, SKIPPED
    started_at: float
    completed_at: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        duration = (
            round(self.completed_at - self.started_at, 4)
            if self.completed_at > 0
            else 0.0
        )
        return {
            "stage_name": self.stage_name,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": duration,
            "details": self.details,
        }


@dataclass
class AutonomousExecutionReport:
    orchestrator_id: str
    idea: str
    project_name: str
    status: AutonomousState
    stages: list[StageRecord] = field(default_factory=list)
    task_reports: list[ExecutionReport] = field(default_factory=list)
    timing: float = 0.0
    files_changed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    correlation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "orchestrator_id": self.orchestrator_id,
            "idea": self.idea,
            "project_name": self.project_name,
            "status": self.status.value,
            "stages": [s.to_dict() for s in self.stages],
            "task_reports": [
                {
                    "job_id": r.job_id,
                    "task_id": r.task_id,
                    "status": r.status,
                    "validation_status": r.validation_status,
                    "retries": r.retries,
                    "files_changed": r.files_changed,
                    "errors": r.errors,
                }
                for r in self.task_reports
            ],
            "timing": self.timing,
            "files_changed": self.files_changed,
            "errors": self.errors,
            "correlation_id": self.correlation_id,
        }


def extract_execution_tasks(task_plan: TaskPlan) -> list[ExecutionTask]:
    """Convert canonical TaskPlan into actionable ExecutionTasks."""
    tasks: list[ExecutionTask] = []
    if not task_plan or not task_plan.epics:
        return tasks

    task_idx = 1
    for epic in task_plan.epics:
        for story in epic.stories:
            for t in story.tasks:
                task_id = f"task-{task_idx:03d}"
                tasks.append(
                    ExecutionTask(
                        id=task_id,
                        title=t.title,
                        description=f"{epic.title} > {story.title}: {t.description}",
                        requirements=[f"Story: {story.title}"],
                        acceptance_criteria=list(t.acceptance_criteria),
                        priority=t.priority or "Medium",
                        dependencies=list(t.dependencies),
                    )
                )
                task_idx += 1
    return tasks


class AutonomousOrchestrator:
    """Coordinates the complete end-to-end autonomous engineering workflow."""

    def __init__(
        self,
        pipeline_engine: PipelineEngine | None = None,
        execution_engine: ExecutionEngine | None = None,
    ) -> None:
        self.pipeline_engine = pipeline_engine or PipelineEngine.from_registry()
        self.execution_engine = execution_engine or ExecutionEngine()
        self.orchestrator_id: str = str(uuid.uuid4())
        self.state: AutonomousState = AutonomousState.INITIALIZED
        self.stages: list[StageRecord] = []

    def _record_stage_start(
        self, stage_name: str, details: dict[str, Any] | None = None
    ) -> StageRecord:
        record = StageRecord(
            stage_name=stage_name,
            status="RUNNING",
            started_at=time.time(),
            details=details or {},
        )
        self.stages.append(record)
        return record

    def _record_stage_end(
        self,
        record: StageRecord,
        status: str = "COMPLETED",
        details: dict[str, Any] | None = None,
    ) -> None:
        record.completed_at = time.time()
        record.status = status
        if details:
            record.details.update(details)

    def execute_workflow(
        self,
        raw_idea: str | None = None,
        project_name: str = "autonomous-project",
        provider: str = "openhands",
        max_retries: int = 3,
        tasks: list[ExecutionTask] | None = None,
        context: ProjectContext | None = None,
        correlation_id: str | None = None,
    ) -> AutonomousExecutionReport:
        """Executes the complete autonomous engineering pipeline."""
        start_time = time.time()
        cid = correlation_id or str(uuid.uuid4())
        errors: list[str] = []
        task_reports: list[ExecutionReport] = []
        all_files_changed: set[str] = set()

        # 1. PLANNING STAGE (if tasks not directly provided)
        if tasks is None:
            self.state = AutonomousState.PLANNING
            stage_plan = self._record_stage_start("PLANNING")
            try:
                if context is None:
                    if not raw_idea:
                        raise ValueError(
                            "Either raw_idea, tasks, or context must be provided."
                        )
                    context = ProjectContext(raw_idea=raw_idea)

                if not context.project_name:
                    context.project_name = project_name

                # Run Brain Pipeline Engine
                context = self.pipeline_engine.run(context)

                if context.task_plan:
                    tasks = extract_execution_tasks(context.task_plan)

                if not tasks:
                    tasks = [
                        ExecutionTask(
                            id="task-001",
                            title=f"Implement {project_name}",
                            description=context.raw_idea or "Implement project",
                        )
                    ]

                self._record_stage_end(
                    stage_plan,
                    status="COMPLETED",
                    details={"tasks_generated": len(tasks)},
                )
            except Exception as e:  # noqa: BLE001
                err_msg = f"Planning stage failed: {e}"
                errors.append(err_msg)
                self._record_stage_end(
                    stage_plan, status="FAILED", details={"error": err_msg}
                )
                self.state = AutonomousState.FAILED
                return AutonomousExecutionReport(
                    orchestrator_id=self.orchestrator_id,
                    idea=raw_idea or (context.raw_idea if context else ""),
                    project_name=project_name,
                    status=AutonomousState.FAILED,
                    stages=self.stages,
                    task_reports=[],
                    timing=round(time.time() - start_time, 4),
                    errors=errors,
                    correlation_id=cid,
                )

        # 2. PREPARING STAGE
        self.state = AutonomousState.PREPARING
        stage_prep = self._record_stage_start(
            "PREPARING", details={"task_count": len(tasks), "provider": provider}
        )
        self._record_stage_end(stage_prep, status="COMPLETED")

        # Empty workflow handling
        if not tasks:
            self.state = AutonomousState.COMPLETED
            return AutonomousExecutionReport(
                orchestrator_id=self.orchestrator_id,
                idea=raw_idea or "",
                project_name=project_name,
                status=AutonomousState.COMPLETED,
                stages=self.stages,
                task_reports=[],
                timing=round(time.time() - start_time, 4),
                errors=[],
                correlation_id=cid,
            )

        # 3. TASK EXECUTION, VALIDATION & RECOVERY LOOP
        has_failure = False

        for task in tasks:
            # EXECUTING Stage
            self.state = AutonomousState.EXECUTING
            stage_exec = self._record_stage_start(
                f"EXECUTING_{task.id}",
                details={"task_id": task.id, "title": task.title},
            )

            task_context = ExecutionContext(
                repository=project_name,
                branch="main",
                task=task,
                provider=provider,
                correlation_id=cid,
            )

            try:
                report = self.execution_engine.execute(
                    task=task,
                    context=task_context,
                    max_retries=max_retries,
                )
                task_reports.append(report)
                all_files_changed.update(report.files_changed)

                self._record_stage_end(
                    stage_exec,
                    status="COMPLETED",
                    details={"files_changed": report.files_changed},
                )

                # Check if RECOVERING stage occurred
                if report.retries > 0:
                    self.state = AutonomousState.RECOVERING
                    stage_rec = self._record_stage_start(
                        f"RECOVERING_{task.id}",
                        details={
                            "task_id": task.id,
                            "retries": report.retries,
                            "recovery_metadata": report.recovery_metadata,
                        },
                    )
                    rec_status = (
                        "COMPLETED" if report.status == "COMPLETED" else "FAILED"
                    )
                    self._record_stage_end(stage_rec, status=rec_status)

                # VALIDATING Stage
                self.state = AutonomousState.VALIDATING
                stage_val = self._record_stage_start(
                    f"VALIDATING_{task.id}",
                    details={"validation_status": report.validation_status},
                )
                val_status = (
                    "COMPLETED" if report.validation_status == "SUCCESS" else "FAILED"
                )
                self._record_stage_end(stage_val, status=val_status)

                if report.status == "FAILED" or report.validation_status != "SUCCESS":
                    has_failure = True
                    err_summary = f"Task {task.id} failed: {'; '.join(report.errors)}"
                    errors.append(err_summary)
                    # Stop on failure
                    break

            except Exception as e:  # noqa: BLE001
                has_failure = True
                err_msg = f"Task {task.id} execution raised unrecoverable error: {e}"
                errors.append(err_msg)
                self._record_stage_end(
                    stage_exec, status="FAILED", details={"error": err_msg}
                )
                break

        # 4. FINAL STATE RESOLUTION
        if has_failure:
            self.state = AutonomousState.FAILED
        else:
            self.state = AutonomousState.COMPLETED

        total_time = round(time.time() - start_time, 4)

        return AutonomousExecutionReport(
            orchestrator_id=self.orchestrator_id,
            idea=raw_idea or (context.raw_idea if context else ""),
            project_name=project_name,
            status=self.state,
            stages=self.stages,
            task_reports=task_reports,
            timing=total_time,
            files_changed=sorted(all_files_changed),
            errors=errors,
            correlation_id=cid,
        )
