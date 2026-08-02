
from brain.project_generator.models import ProjectBlueprint

from .template_models import TemplateMetadata
from .template_registry import TemplateRegistry


class TemplateMatcher:
    def __init__(self, registry: TemplateRegistry):
        self.registry = registry

    def match(self, blueprint: ProjectBlueprint) -> list[TemplateMetadata]:
        languages = []
        frameworks = []
        backends = []
        frontends = []
        databases = []
        
        if blueprint.architecture and hasattr(blueprint.architecture, 'technology_mapping'):
            tech_stack = blueprint.architecture.technology_mapping
            if isinstance(tech_stack, dict):
                backends.append(tech_stack.get('backend', ''))
                frontends.append(tech_stack.get('frontend', ''))
                databases.append(tech_stack.get('database', ''))
                languages.append(tech_stack.get('language', ''))
                frameworks.append(tech_stack.get('framework', ''))
                
        languages = [lang.lower() for lang in languages if lang]
        frameworks = [fw.lower() for fw in frameworks if fw]
        backends = [be.lower() for be in backends if be]
        frontends = [fe.lower() for fe in frontends if fe]
        databases = [db.lower() for db in databases if db]

        matched = []
        for template in self.registry.list_templates():
            def has_match(supported: list[str], required: list[str]) -> bool:
                if not supported: return True
                if not required: return True
                supported_lower = [s.lower() for s in supported]
                return any(req in supported_lower for req in required)

            if not has_match(template.supported_backends, backends):
                continue
            if not has_match(template.supported_frontends, frontends):
                continue
            if not has_match(template.supported_languages, languages):
                continue
            if not has_match(template.supported_databases, databases):
                continue
            
            matched.append(template)
            
        matched.sort(key=lambda t: (-t.priority, t.id))
        return matched
