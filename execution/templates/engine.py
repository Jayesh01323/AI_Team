from pathlib import Path

from execution.repository.filesystem import FileSystem
from execution.templates.loader import TemplateLoader
from execution.templates.renderer import TemplateRenderer


class TemplateEngine:
    def __init__(self, assets_dir: Path, fs: FileSystem):
        self.loader = TemplateLoader(assets_dir)
        self.renderer = TemplateRenderer(fs)

    def render_template(
        self, template_id: str, version: str, variables: dict
    ) -> list[str]:
        """Renders an entire template directory to the filesystem."""
        template_dir = self.loader.get_template_dir(template_id, version)
        src_dir = template_dir / "src"
        if not src_dir.exists():
            return []

        rendered_files = []
        for path in src_dir.rglob("*"):
            if path.is_file():
                rel_path = path.relative_to(src_dir)
                dest_path = str(rel_path).replace("\\", "/")
                self.renderer.render_to_file(path, dest_path, variables)
                rendered_files.append(dest_path)
        return rendered_files
