from brain.project_generator.assembler import ProjectAssembler
from brain.project_generator.code_models import GeneratedFile, GeneratedProject
from brain.project_generator.models import ProjectBlueprint


def test_project_assembler():
    assembler = ProjectAssembler()
    bp = ProjectBlueprint(project_name="MyApp")
    
    # Path sorting should handle b/1.py before b/a/2.py
    f1 = GeneratedFile(path="src/main.py", filename="main.py", content="content")
    f2 = GeneratedFile(path="src/utils/helpers.py", filename="helpers.py", content="content")
    f3 = GeneratedFile(path="README.md", filename="README.md", content="content")
    
    gp = GeneratedProject(generated_files=[f1, f2, f3])
    
    assembled = assembler.assemble(bp, gp)
    
    assert assembled.project_name == "MyApp"
    assert assembled.root.name == "MyApp"
    assert len(assembled.root.files) == 1
    assert assembled.root.files[0].name == "README.md"
    
    assert len(assembled.root.directories) == 1
    src_dir = assembled.root.directories[0]
    assert src_dir.name == "src"
    assert len(src_dir.files) == 1
    assert src_dir.files[0].name == "main.py"
    
    assert len(src_dir.directories) == 1
    utils_dir = src_dir.directories[0]
    assert utils_dir.name == "utils"
    assert len(utils_dir.files) == 1
    assert utils_dir.files[0].name == "helpers.py"
    
    assert assembled.summary.statistics.total_files == 3
    assert assembled.summary.statistics.total_directories == 2 # src, utils
    
    # Verify immutability of input
    assert len(gp.generated_files) == 3
