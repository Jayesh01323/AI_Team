from typing import List, Dict, Set
from .template_models import TemplateMetadata, ResolvedTemplateSet, TemplateValidationResult
from .template_registry import TemplateRegistry
from .template_matcher import TemplateMatcher
from brain.project_generator.models import ProjectBlueprint

class TemplateResolver:
    def __init__(self, registry: TemplateRegistry):
        self.registry = registry
        self.matcher = TemplateMatcher(registry)

    def resolve_templates(self, blueprint: ProjectBlueprint) -> ResolvedTemplateSet:
        matched = self.matcher.match(blueprint)
        
        selected: Dict[str, TemplateMetadata] = {}
        ordering: List[str] = []
        errors = []
        
        def add_template(template_id: str, trace: Set[str]):
            if template_id in selected:
                return
            if template_id in trace:
                errors.append(f"Circular dependency detected involving {template_id}")
                return
                
            template = self.registry.get_template(template_id)
            if not template:
                errors.append(f"Missing required template dependency: {template_id}")
                return
                
            trace.add(template_id)
            for dep in template.dependencies:
                add_template(dep, trace)
            trace.remove(template_id)
            
            selected[template_id] = template
            ordering.append(template_id)

        for t in matched:
            add_template(t.id, set())

        categories: Dict[str, List[str]] = {}
        for t in selected.values():
            categories.setdefault(t.category, []).append(t.id)
            
        for cat, ids in categories.items():
            if cat in ['backend_framework', 'frontend_framework'] and len(ids) > 1:
                errors.append(f"Incompatible combination: Multiple templates for category {cat}: {', '.join(ids)}")

        validation_result = TemplateValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
        
        rationale = {t.id: "Matched from blueprint requirements or dependencies" for t in selected.values()}

        return ResolvedTemplateSet(
            selected_templates=[selected[tid] for tid in ordering],
            selection_rationale=rationale,
            dependency_ordering=ordering,
            validation_result=validation_result
        )
