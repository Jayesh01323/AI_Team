import logging
from pathlib import Path

from execution.templates.manifest import TemplateManifest

logger = logging.getLogger(__name__)


class TemplateLoader:
    def __init__(self, assets_dir: Path):
        self.assets_dir = assets_dir

    def discover_templates(self) -> dict[str, dict[str, Path]]:
        """Returns dict mapping template_id -> version -> Path"""
        templates: dict[str, dict[str, Path]] = {}
        if not self.assets_dir.exists():
            return templates

        for tech_dir in self.assets_dir.iterdir():
            if not tech_dir.is_dir():
                continue
            for version_dir in tech_dir.iterdir():
                if not version_dir.is_dir():
                    continue
                manifest_path = version_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        manifest = TemplateManifest.load(manifest_path)
                        if manifest.template_id not in templates:
                            templates[manifest.template_id] = {}
                        templates[manifest.template_id][manifest.version] = version_dir
                    except (ValueError, KeyError, OSError) as e:
                        logger.warning(
                            "Skipping invalid manifest %s: %s", manifest_path, e
                        )
        return templates

    def get_template_dir(self, template_id: str, version: str) -> Path:
        templates = self.discover_templates()
        if template_id not in templates or version not in templates[template_id]:
            raise ValueError(f"Template {template_id} version {version} not found.")
        return templates[template_id][version]
