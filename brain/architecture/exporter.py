import json
from typing import Dict, Any, List
from .models import Architecture

class ArchitectureExporter:
    @staticmethod
    def to_dict(arch: Architecture) -> Dict[str, Any]:
        return arch.model_dump(mode='json')

    @staticmethod
    def to_json(arch: Architecture, indent: int = 2) -> str:
        return json.dumps(ArchitectureExporter.to_dict(arch), indent=indent)

    @staticmethod
    def summary(arch: Architecture) -> str:
        lines = [
            f"Architecture for: {arch.project_name}",
            f"Style: {arch.architecture_style}",
            f"Modules: {len(arch.modules)}",
            f"Components: {sum(len(m.components) for m in arch.modules)}",
            f"APIs: {len(arch.apis)}",
            f"Data Models: {len(arch.data_models)}"
        ]
        return "\n".join(lines)

    @staticmethod
    def statistics(arch: Architecture) -> Dict[str, int]:
        return {
            "modules_count": len(arch.modules),
            "components_count": sum(len(m.components) for m in arch.modules),
            "apis_count": len(arch.apis),
            "data_models_count": len(arch.data_models),
            "dependencies_count": len(arch.dependencies),
            "traceability_links_count": len(arch.traceability_links)
        }

