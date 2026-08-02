from brain.project_generator.assembly_models import (
    AssembledProject,
    AssemblyValidationResult,
    ProjectDirectory,
    ProjectFile,
)


def test_project_directory_rebuild():
    d = ProjectDirectory(name="root")
    sub = ProjectDirectory(name="src")
    f = ProjectFile(name="main.py", content="print('hi')")
    sub.files.append(f)
    d.directories.append(sub)
    
    assert d.directories[0].name == "src"
    assert d.directories[0].files[0].name == "main.py"

def test_assembled_project_export():
    d = ProjectDirectory(name="root")
    p = AssembledProject(
        project_name="TestApp",
        root=d,
        validation_result=AssemblyValidationResult(is_valid=True)
    )
    assert p.summary_text() == "AssembledProject: TestApp, Dirs: 0, Files: 0. Valid: True"
    assert "TestApp" in p.export_json()
