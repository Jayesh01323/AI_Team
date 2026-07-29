from execution.repository.filesystem import FileSystem
from execution.repository.scaffolder import ProjectScaffolder
from execution.validation.workflow import ValidationWorkflow
from models.project_context import ProjectContext


def test_filesystem_creation(tmp_path):
    fs = FileSystem(tmp_path)
    fs.create_directory("test_dir")
    assert (tmp_path / "test_dir").is_dir()
    fs.write_file("test.txt", "hello")
    assert (tmp_path / "test.txt").read_text() == "hello"


def test_scaffolder(tmp_path):
    fs = FileSystem(tmp_path)
    scaffolder = ProjectScaffolder(fs)
    context = ProjectContext(project_name="test_project")
    scaffolder.scaffold(context)

    assert fs.dir_exists("backend")
    assert fs.dir_exists(".git")


def test_validator_success(tmp_path):
    fs = FileSystem(tmp_path)
    scaffolder = ProjectScaffolder(fs)
    context = ProjectContext(project_name="test_project")

    scaffolder.scaffold(context)

    # Mock template output
    fs.write_file("README.md", "")
    fs.write_file(".gitignore", "")
    fs.write_file(".env.example", "")
    fs.write_file("pyproject.toml", "[project]")
    fs.write_file("docker-compose.yml", "")

    report = ValidationWorkflow.run(tmp_path)

    assert len(report.errors) == 0


def test_validator_failure(tmp_path):
    FileSystem(tmp_path)
    # create dummy dir so it exists
    tmp_path.mkdir(exist_ok=True)
    report = ValidationWorkflow.run(tmp_path)

    assert len(report.errors) > 0
    assert any("README.md" in e for e in report.errors)


def test_list_files_excludes_git_not_github(tmp_path):
    """list_files() must skip .git/ internals but include .github/ files."""
    fs = FileSystem(tmp_path)

    # Create .git internals (should be excluded)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("git-config")
    (tmp_path / ".git" / "refs").mkdir()
    (tmp_path / ".git" / "refs" / "heads").mkdir()
    (tmp_path / ".git" / "refs" / "heads" / "main").write_text("ref")

    # Create .github directory (should be included)
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: CI")

    # Create a regular file
    (tmp_path / "README.md").write_text("hello")

    files = fs.list_files()

    # .github files must be included
    assert ".github/workflows/ci.yml" in files

    # .git files must be excluded
    assert ".git/config" not in files
    assert ".git/refs/heads/main" not in files

    # Regular file must be included
    assert "README.md" in files


def test_list_files_no_false_positive_on_dotgit_prefix(tmp_path):
    """Directories like 'dotgit-example' must not be excluded."""
    fs = FileSystem(tmp_path)

    (tmp_path / "dotgit-example").mkdir()
    (tmp_path / "dotgit-example" / "file.txt").write_text("content")

    files = fs.list_files()
    assert "dotgit-example/file.txt" in files
