from execution.repository.filesystem import FileSystem
from execution.repository.generator import RepositoryGenerator
from models.architecture import Architecture
from models.project_context import ProjectContext


def test_generator_with_tech_stack(tmp_path):
    generator = RepositoryGenerator(tmp_path)

    context = ProjectContext(project_name="tech_project")
    context.architecture = Architecture(
        system_overview="Test",
        technology_stack={"backend": "fastapi", "frontend": "react"},
    )

    report = generator.generate(context)

    assert report.status == "SUCCESS"

    fs = FileSystem(tmp_path / "tech_project")

    # Assert base files
    assert fs.file_exists("README.md")
    assert fs.file_exists("docker-compose.yml")

    # Assert FastAPI files
    assert fs.file_exists("backend/main.py")
    assert fs.file_exists("backend/requirements.txt")
    assert fs.file_exists("backend/Dockerfile")

    # Assert React files
    assert fs.file_exists("frontend/package.json")
    assert fs.file_exists("frontend/vite.config.ts")
    assert fs.file_exists("frontend/src/App.tsx")
    assert fs.file_exists("frontend/Dockerfile")
