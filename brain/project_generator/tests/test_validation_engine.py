import hashlib

import pytest

from brain.project_generator.assembly_models import (
    AssembledProject,
    ProjectDirectory,
    ProjectFile,
)
from brain.project_generator.models import ProjectBlueprint
from brain.project_generator.repair_planner import RepairPlanner
from brain.project_generator.validation_exporter import ValidationExporter
from brain.project_generator.validation_models import (
    IssueCategory,
    RepairActionType,
    Severity,
)
from brain.project_generator.validator import EngineValidator


@pytest.fixture
def base_blueprint():
    return ProjectBlueprint(project_name="TestApp")

@pytest.fixture
def base_assembled_project():
    def make_file(name, content, meta=None):
        if meta is None:
            meta = {"generated_from": "tpl1", "component": "core"}
        return ProjectFile(
            name=name,
            content=content,
            metadata=meta,
            checksum=hashlib.sha256(content.encode('utf-8')).hexdigest(),
            template_id="tpl1"
        )
        
    return AssembledProject(
        project_name="TestApp",
        root=ProjectDirectory(
            name="root",
            files=[
                make_file("main.py", "print('hello')"),
                make_file("utils.py", "def foo(): pass")
            ],
            directories=[
                ProjectDirectory(
                    name="src",
                    files=[
                        make_file("core.py", "class Core: pass")
                    ]
                )
            ]
        )
    )

def test_validator_clean(base_blueprint, base_assembled_project):
    validator = EngineValidator()
    report = validator.validate(base_blueprint, base_assembled_project)
    assert report.is_valid is True
    assert len(report.issues) == 0

def test_validator_duplicate_file(base_blueprint, base_assembled_project):
    # Add duplicate file
    base_assembled_project.root.directories[0].files.append(
        ProjectFile(name="core.py", content="", metadata={}, checksum="", template_id="")
    )
    validator = EngineValidator()
    report = validator.validate(base_blueprint, base_assembled_project)
    
    dup_issues = [i for i in report.issues if i.type == "duplicate_file"]
    assert len(dup_issues) == 1
    assert report.is_valid is False
    assert dup_issues[0].category == IssueCategory.Structure

def test_validator_empty_file_and_missing_metadata(base_blueprint, base_assembled_project):
    # Empty file and no metadata
    empty_file = ProjectFile(name="empty.py", content="", metadata={}, checksum="", template_id="")
    base_assembled_project.root.files.append(empty_file)
    
    validator = EngineValidator()
    report = validator.validate(base_blueprint, base_assembled_project)
    
    assert report.is_valid is False
    issue_types = {i.type for i in report.issues}
    assert "empty_file" in issue_types
    assert "missing_metadata" in issue_types
    assert "missing_checksum" in issue_types
    
    empty_issues = [i for i in report.issues if i.type == "empty_file"]
    assert empty_issues[0].category == IssueCategory.GeneratedFile
    
    # Check statistics
    assert "GeneratedFile" in report.statistics.issues_by_category
    assert report.statistics.issues_by_category["GeneratedFile"] > 0
    assert report.statistics.issues_by_severity[Severity.ERROR.value] > 0

def test_validator_unresolved_placeholder(base_blueprint, base_assembled_project):
    base_assembled_project.root.files[0].content = "print('{{ placeholder }}')"
    base_assembled_project.root.files[0].checksum = hashlib.sha256(b"print('{{ placeholder }}')").hexdigest()
    
    validator = EngineValidator()
    report = validator.validate(base_blueprint, base_assembled_project)
    
    assert report.is_valid is False
    assert any(i.type == "unresolved_placeholder" for i in report.issues)

def test_repair_planner(base_blueprint, base_assembled_project):
    # Inject some errors
    empty_file = ProjectFile(name="empty.py", content="", metadata={}, checksum="", template_id="")
    base_assembled_project.root.files.append(empty_file)
    base_assembled_project.root.files[0].content = "print('{{ p }}')"
    base_assembled_project.root.files[0].checksum = hashlib.sha256(b"print('{{ p }}')").hexdigest()
    
    validator = EngineValidator()
    report = validator.validate(base_blueprint, base_assembled_project)
    
    planner = RepairPlanner()
    plan = planner.plan_repairs(report)
    
    assert len(plan.actions) > 0
    types = {a.type for a in plan.actions}
    assert RepairActionType.REGENERATE_FILE in types
    assert RepairActionType.UPDATE_METADATA in types
    assert RepairActionType.FIX_PLACEHOLDER in types
    
    # Check issue tracking
    assert plan.actions[0].issue_id is not None
    assert hasattr(plan.actions[0], "metadata")
    assert plan.statistics.actions_by_severity[Severity.ERROR.value] > 0

def test_deterministic_ordering(base_blueprint, base_assembled_project):
    base_assembled_project.root.files.append(ProjectFile(name="a.py", content="", metadata={}, checksum="", template_id=""))
    base_assembled_project.root.files.append(ProjectFile(name="b.py", content="", metadata={}, checksum="", template_id=""))
    
    validator = EngineValidator()
    report = validator.validate(base_blueprint, base_assembled_project)
    planner = RepairPlanner()
    plan1 = planner.plan_repairs(report)
    plan2 = planner.plan_repairs(report)
    
    assert [a.id for a in plan1.actions] == [a.id for a in plan2.actions]
    
    # Explicit ordering check: Priority -> Severity -> Action Type -> Target -> ID
    for i in range(len(plan1.actions) - 1):
        a1 = plan1.actions[i]
        a2 = plan1.actions[i+1]
        a1_sort_key = (a1.deterministic_priority, planner.severity_map.get(a1.severity, 100), a1.type.value, a1.target, a1.id)
        a2_sort_key = (a2.deterministic_priority, planner.severity_map.get(a2.severity, 100), a2.type.value, a2.target, a2.id)
        assert a1_sort_key <= a2_sort_key

def test_exports(base_blueprint, base_assembled_project):
    base_assembled_project.root.files[0].content = ""
    validator = EngineValidator()
    report = validator.validate(base_blueprint, base_assembled_project)
    planner = RepairPlanner()
    plan = planner.plan_repairs(report)
    
    d1 = ValidationExporter.export_report_dict(report)
    j1 = ValidationExporter.export_report_json(report)
    s1 = ValidationExporter.report_summary(report)
    
    assert isinstance(d1, dict)
    assert isinstance(j1, str)
    assert "ValidationReport" in s1
    
    d2 = ValidationExporter.export_plan_dict(plan)
    j2 = ValidationExporter.export_plan_json(plan)
    s2 = ValidationExporter.plan_summary(plan)
    
    assert isinstance(d2, dict)
    assert isinstance(j2, str)
    assert "RepairPlan" in s2
