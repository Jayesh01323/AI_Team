import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TemplateManifest:
    template_id: str
    version: str
    technologies: list[str]
    variables: list[str]
    compatibility: dict[str, str]

    @classmethod
    def load(cls, path: Path) -> "TemplateManifest":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
