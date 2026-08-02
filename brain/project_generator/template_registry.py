from collections.abc import Callable

from .template_models import TemplateMetadata


class TemplateRegistry:
    def __init__(self):
        self._templates: dict[str, TemplateMetadata] = {}

    def register_template(self, template: TemplateMetadata) -> None:
        self._templates[template.id] = template

    def unregister_template(self, template_id: str) -> None:
        if template_id in self._templates:
            del self._templates[template_id]

    def get_template(self, template_id: str) -> TemplateMetadata | None:
        return self._templates.get(template_id)

    def list_templates(self) -> list[TemplateMetadata]:
        return list(self._templates.values())

    def filter_templates(self, predicate: Callable[[TemplateMetadata], bool]) -> list[TemplateMetadata]:
        return [t for t in self._templates.values() if predicate(t)]
