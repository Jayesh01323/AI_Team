from typing import Dict, Any, List
from .models import Architecture
from .component_graph import ComponentGraph

class ValidationResult:
    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, message: str):
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }

class ArchitectureValidator:
    @staticmethod
    def validate(arch: Architecture) -> ValidationResult:
        result = ValidationResult()

        comp_ids = set()
        components = []
        
        # Check duplicate components
        for module in arch.modules:
            for comp in module.components:
                if comp.id in comp_ids:
                    result.add_error(f"Duplicate component ID found: {comp.id}")
                comp_ids.add(comp.id)
                components.append(comp)

        # Build graph and check cycles
        graph = ComponentGraph()
        try:
            graph.build_from_architecture(components, arch.dependencies)
            if graph.has_cycle():
                result.add_error("Circular dependency detected in architecture")
        except ValueError as e:
            result.add_error(str(e))
            
        # Check invalid API module references
        for api in arch.apis:
            if api.module_id and api.module_id not in [m.id for m in arch.modules]:
                result.add_error(f"API {api.id} references unknown module {api.module_id}")

        # Check invalid traceability links
        for link in arch.traceability_links:
            if link.target_type == "component" and link.target_id not in comp_ids:
                result.add_error(f"Traceability link points to unknown component {link.target_id}")

        return result
