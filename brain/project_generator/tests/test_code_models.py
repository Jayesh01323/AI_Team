from brain.project_generator.code_models import GeneratedFile, GeneratedProject, CodeGenerationValidationResult

def test_generated_file_checksum():
    gf = GeneratedFile(
        path="main.py", 
        filename="main.py", 
        content="print('hello')", 
        metadata={"key": "val"}
    )
    assert gf.checksum == ""
    chk = gf.calculate_checksum()
    assert chk != ""
    assert isinstance(chk, str)

def test_generated_project_export():
    gf = GeneratedFile(path="main.py", filename="main.py", content="content", metadata={"a": 1})
    gp = GeneratedProject(
        generated_files=[gf],
        generation_summary="test summary",
        generation_metadata={"gen": "yes"},
        validation_result=CodeGenerationValidationResult(is_valid=True)
    )
    
    d = gp.export_dict()
    assert d["generation_summary"] == "test summary"
    assert len(d["generated_files"]) == 1
    
    j = gp.export_json()
    assert "test summary" in j
    
    s = gp.summary()
    assert "Generated 1 files. Valid: True" in s
