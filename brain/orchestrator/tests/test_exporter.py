import pytest
import json
from brain.orchestrator.exporter import OrchestratorExporter
from brain.orchestrator.models import Workflow, TaskAssignment, AgentType, ExecutionStatus

def test_export_dict():
    workflow = Workflow(
        id="w1",
        assignments={
            "t1": TaskAssignment(task_id="t1", agent_type=AgentType.CODING)
        }
    )
    
    d = OrchestratorExporter.to_dict(workflow)
    assert d["id"] == "w1"
    assert "t1" in d["assignments"]

def test_export_json():
    workflow = Workflow(
        id="w1"
    )
    j = OrchestratorExporter.to_json(workflow)
    assert "w1" in j
    assert json.loads(j)["id"] == "w1"

def test_summary():
    workflow = Workflow(
        id="w1",
        assignments={
            "t1": TaskAssignment(task_id="t1", agent_type=AgentType.CODING, status=ExecutionStatus.COMPLETED)
        }
    )
    s = OrchestratorExporter.summary(workflow)
    assert "w1" in s
    assert "Total Tasks: 1" in s
    assert "completed: 1" in s

def test_statistics():
    workflow = Workflow(
        id="w1",
        assignments={
            "t1": TaskAssignment(task_id="t1", agent_type=AgentType.CODING, status=ExecutionStatus.COMPLETED)
        }
    )
    stats = OrchestratorExporter.statistics(workflow)
    assert stats["total_tasks"] == 1
    assert stats["status_completed"] == 1
