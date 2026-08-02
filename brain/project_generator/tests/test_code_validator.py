from brain.project_generator.code_models import GeneratedFile, GeneratedProject
from brain.project_generator.code_validator import CodeValidator


def test_validator_valid():
    validator = CodeValidator()
    gf = GeneratedFile(path="a.py", filename="a.py", content="valid", metadata={"a": 1})
    gp = GeneratedProject(generated_files=[gf])
    
    result = validator.validate(gp)
    assert result.is_valid is True

def test_validator_duplicates():
    validator = CodeValidator()
    gf1 = GeneratedFile(path="a.py", filename="a.py", content="valid", metadata={"a": 1})
    gf2 = GeneratedFile(path="a.py", filename="a.py", content="valid2", metadata={"a": 1})
    gp = GeneratedProject(generated_files=[gf1, gf2])
    
    result = validator.validate(gp)
    assert result.is_valid is False
    assert any("Duplicate" in e for e in result.errors)

def test_validator_empty_and_unresolved():
    validator = CodeValidator()
    gf1 = GeneratedFile(path="a.py", filename="a.py", content="  ", metadata={"a": 1})
    gf2 = GeneratedFile(path="b.py", filename="b.py", content="hello {{VAR}}", metadata={"a": 1})
    gp = GeneratedProject(generated_files=[gf1, gf2])
    
    result = validator.validate(gp)
    assert result.is_valid is False
    assert any("Empty" in e for e in result.errors)
    assert any("Unresolved" in e for e in result.errors)
