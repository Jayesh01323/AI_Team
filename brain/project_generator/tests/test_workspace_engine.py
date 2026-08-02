import os
import shutil

import pytest

from brain.project_generator.assembly_models import (
    AssembledProject,
    ProjectDirectory,
    ProjectFile,
)
from brain.project_generator.export_validator import ExportValidator
from brain.project_generator.project_exporter import ProjectExporter
from brain.project_generator.workspace_manager import WorkspaceManager


@pytest.fixture
def temp_workspace(tmp_path):
    ws_dir = tmp_path / "workspace"
    ws_dir.mkdir()
    yield str(ws_dir)
    if ws_dir.exists():
        shutil.rmtree(ws_dir)

@pytest.fixture
def assembled_project():
    return AssembledProject(
        project_name="TestApp",
        root=ProjectDirectory(
            name="root",
            files=[
                ProjectFile(name="main.py", content="print('hello')", checksum="c1", template_id="t1")
            ],
            directories=[
                ProjectDirectory(
                    name="src",
                    files=[
                        ProjectFile(name="core.py", content="def core(): pass", checksum="c2", template_id="t2")
                    ]
                )
            ]
        )
    )

def test_export_success(temp_workspace, assembled_project):
    exporter = ProjectExporter(overwrite=False)
    result = exporter.export(assembled_project, temp_workspace)
    
    assert result.success is True
    assert len(result.errors) == 0
    assert result.statistics.files_written == 2
    assert result.statistics.directories_written == 2 # root and src
    assert result.statistics.skipped_files == 0
    assert result.statistics.overwritten_files == 0
    
    assert os.path.exists(os.path.join(temp_workspace, "main.py"))
    assert os.path.exists(os.path.join(temp_workspace, "src", "core.py"))

def test_export_overwrite(temp_workspace, assembled_project):
    # Initial export
    exporter = ProjectExporter(overwrite=False)
    exporter.export(assembled_project, temp_workspace)
    
    # Try again without overwrite
    result2 = exporter.export(assembled_project, temp_workspace)
    assert result2.success is True
    assert result2.statistics.files_written == 0
    assert result2.statistics.skipped_files == 2
    
    # Try again with overwrite
    exporter_overwrite = ProjectExporter(overwrite=True)
    result3 = exporter_overwrite.export(assembled_project, temp_workspace)
    assert result3.success is True
    assert result3.statistics.files_written == 2
    assert result3.statistics.overwritten_files == 2

def test_export_validator_duplicate_paths(temp_workspace, assembled_project):
    assembled_project.root.directories[0].files.append(
        ProjectFile(name="core.py", content="dup", checksum="c3", template_id="t3")
    )
    
    validator = ExportValidator()
    is_safe, errors = validator.validate_export_safety(assembled_project, temp_workspace)
    assert is_safe is False
    assert any("Duplicate path" in e for e in errors)

def test_export_validator_invalid_characters(temp_workspace, assembled_project):
    assembled_project.root.files.append(
        ProjectFile(name="bad<name>.py", content="", checksum="c3", template_id="t3")
    )
    
    validator = ExportValidator()
    is_safe, errors = validator.validate_export_safety(assembled_project, temp_workspace)
    assert is_safe is False
    assert any("Invalid characters" in e for e in errors)

def test_export_validator_traversal(temp_workspace, assembled_project):
    assembled_project.root.files.append(
        ProjectFile(name="../outside.py", content="", checksum="c3", template_id="t3")
    )
    
    validator = ExportValidator()
    is_safe, errors = validator.validate_export_safety(assembled_project, temp_workspace)
    assert is_safe is False
    assert any("Path traversal" in e or "resolves outside destination" in e for e in errors)

def test_manifest_generation(temp_workspace, assembled_project):
    manager = WorkspaceManager()
    ws = manager.build_workspace_model(assembled_project, temp_workspace)
    manifest = manager.create_manifest(assembled_project, ws)
    
    assert manifest.project_name == "TestApp"
    assert manifest.total_files == 2
    assert manifest.total_directories == 1 # Note: root dir itself is not counted in _count_directories
    assert "main.py" in manifest.checksums
    assert "src/core.py" in manifest.checksums
    
def test_deterministic_order(temp_workspace, assembled_project):
    manager = WorkspaceManager()
    ws = manager.build_workspace_model(assembled_project, temp_workspace)
    
    # Should be sorted alphabetically
    assert ws.files[0].relative_path == "main.py"
    assert ws.files[1].relative_path == "src/core.py"
