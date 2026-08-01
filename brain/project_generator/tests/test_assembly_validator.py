from brain.project_generator.assembly_validator import AssemblyValidator
from brain.project_generator.assembly_models import AssembledProject, ProjectDirectory, ProjectFile

def test_validator_valid():
    validator = AssemblyValidator()
    root = ProjectDirectory(name="root")
    root.files.append(ProjectFile(name="a.py", content=""))
    p = AssembledProject(project_name="Test", root=root)
    
    result = validator.validate(p)
    assert result.is_valid is True

def test_validator_duplicate_file():
    validator = AssemblyValidator()
    root = ProjectDirectory(name="root")
    root.files.append(ProjectFile(name="a.py", content=""))
    root.files.append(ProjectFile(name="a.py", content=""))
    p = AssembledProject(project_name="Test", root=root)
    
    result = validator.validate(p)
    assert result.is_valid is False
    assert any("Duplicate file name" in e for e in result.errors)

def test_validator_empty():
    validator = AssemblyValidator()
    root = ProjectDirectory(name="root")
    p = AssembledProject(project_name="Test", root=root)
    
    result = validator.validate(p)
    assert result.is_valid is False
    assert any("empty" in e for e in result.errors)
