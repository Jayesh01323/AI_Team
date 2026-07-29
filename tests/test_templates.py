import json

import pytest

from core.exceptions import TemplateRenderError
from execution.repository.filesystem import FileSystem
from execution.templates.engine import TemplateEngine
from execution.templates.manifest import TemplateManifest
from execution.templates.renderer import TemplateRenderer


def test_manifest_load(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "template_id": "test",
                "version": "v1",
                "technologies": ["test"],
                "variables": ["var1"],
                "compatibility": {"os": "all"},
            }
        )
    )
    manifest = TemplateManifest.load(manifest_path)
    assert manifest.template_id == "test"
    assert manifest.version == "v1"


def test_template_renderer_success(tmp_path):
    """Successful rendering with all variables provided."""
    fs = FileSystem(tmp_path)
    renderer = TemplateRenderer(fs)

    rendered = renderer.render_to_string("Hello ${name}", {"name": "World"})
    assert rendered == "Hello World"

    src = tmp_path / "src.txt"
    src.write_text("Project: ${project_name}")

    renderer.render_to_file(src, "dest.txt", {"project_name": "AI"})
    assert (tmp_path / "dest.txt").read_text() == "Project: AI"


def test_template_renderer_multiple_variables(tmp_path):
    """Rendering with multiple variables substituted correctly."""
    fs = FileSystem(tmp_path)
    renderer = TemplateRenderer(fs)

    template = "${greeting} ${name}, welcome to ${project}!"
    rendered = renderer.render_to_string(
        template, {"greeting": "Hello", "name": "Dev", "project": "AI Team"}
    )
    assert rendered == "Hello Dev, welcome to AI Team!"


def test_template_renderer_missing_variable_raises(tmp_path):
    """Missing variables must raise TemplateRenderError, not silently leave placeholders."""
    fs = FileSystem(tmp_path)
    renderer = TemplateRenderer(fs)

    with pytest.raises(TemplateRenderError, match="missing variable"):
        renderer.render_to_string("Hello ${name}", {})


def test_template_renderer_partial_variables_raises(tmp_path):
    """Providing some but not all variables must raise TemplateRenderError."""
    fs = FileSystem(tmp_path)
    renderer = TemplateRenderer(fs)

    with pytest.raises(TemplateRenderError, match="missing variable"):
        renderer.render_to_string("${greeting} ${name}", {"greeting": "Hello"})


def test_template_renderer_no_unresolved_placeholders(tmp_path):
    """Verify no ${...} patterns survive rendering when all variables are provided."""
    fs = FileSystem(tmp_path)
    renderer = TemplateRenderer(fs)

    rendered = renderer.render_to_string(
        "DB=${database_url} PORT=${api_port}",
        {"database_url": "postgres://localhost/db", "api_port": "8000"},
    )
    assert "${" not in rendered
    assert rendered == "DB=postgres://localhost/db PORT=8000"


def test_template_renderer_bare_dollar_preserved(tmp_path):
    """Bare $name patterns (not ${braced}) must be left untouched.

    Template files like .gitignore contain patterns such as *$py.class
    which are NOT variable references.
    """
    fs = FileSystem(tmp_path)
    renderer = TemplateRenderer(fs)

    rendered = renderer.render_to_string(
        "*.py[cod]\n*$py.class\n${project_name}",
        {"project_name": "MyProject"},
    )
    assert "*$py.class" in rendered
    assert "MyProject" in rendered


def test_template_renderer_file_missing_variable_raises(tmp_path):
    """render_to_file must also fail fast on missing variables."""
    fs = FileSystem(tmp_path)
    renderer = TemplateRenderer(fs)

    src = tmp_path / "template.txt"
    src.write_text("name = ${project_name}")

    with pytest.raises(TemplateRenderError, match="missing variable"):
        renderer.render_to_file(src, "output.txt", {})

    # File must NOT be created
    assert not (tmp_path / "output.txt").exists()


def test_template_engine(tmp_path):
    # Setup mock assets
    assets_dir = tmp_path / "assets"
    base_dir = assets_dir / "base" / "v1"
    src_dir = base_dir / "src"
    src_dir.mkdir(parents=True)

    (base_dir / "manifest.json").write_text(
        json.dumps(
            {
                "template_id": "base",
                "version": "v1",
                "technologies": [],
                "variables": ["var"],
                "compatibility": {},
            }
        )
    )

    (src_dir / "test.txt").write_text("Hello ${var}")

    fs = FileSystem(tmp_path / "output")
    engine = TemplateEngine(assets_dir, fs)

    files = engine.render_template("base", "v1", {"var": "World"})
    assert len(files) == 1
    assert "test.txt" in files[0]
    assert (tmp_path / "output" / "test.txt").read_text() == "Hello World"


def test_template_engine_missing_variable_raises(tmp_path):
    """TemplateEngine must propagate TemplateRenderError when variables are missing."""
    assets_dir = tmp_path / "assets"
    base_dir = assets_dir / "base" / "v1"
    src_dir = base_dir / "src"
    src_dir.mkdir(parents=True)

    (base_dir / "manifest.json").write_text(
        json.dumps(
            {
                "template_id": "base",
                "version": "v1",
                "technologies": [],
                "variables": ["missing_var"],
                "compatibility": {},
            }
        )
    )

    (src_dir / "test.txt").write_text("Value: ${missing_var}")

    fs = FileSystem(tmp_path / "output")
    engine = TemplateEngine(assets_dir, fs)

    with pytest.raises(TemplateRenderError):
        engine.render_template("base", "v1", {})
