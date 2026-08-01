from typing import Dict, Any
from .assembly_models import AssembledProject

class AssemblyExporter:
    def export_dict(self, project: AssembledProject) -> Dict[str, Any]:
        return project.export_dict()
        
    def export_json(self, project: AssembledProject) -> str:
        return project.export_json()
        
    def summary(self, project: AssembledProject) -> str:
        return project.summary_text()
