from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Dependency(BaseModel):
    source_id: str
    target_id: str
    type: str = "uses" # e.g., uses, inherits, calls

class Component(BaseModel):
    id: str
    name: str
    description: str
    type: str = "component" # service, module, ui_component, database, etc.
    technologies: List[str] = Field(default_factory=list)
    tasks: List[str] = Field(default_factory=list) # Traceability to tasks

class Module(BaseModel):
    id: str
    name: str
    components: List[Component] = Field(default_factory=list)

class APIEndpoint(BaseModel):
    id: str
    path: str
    method: str
    description: str
    module_id: Optional[str] = None

class DataModel(BaseModel):
    id: str
    name: str
    fields: Dict[str, str] = Field(default_factory=dict)
    
class TraceabilityLink(BaseModel):
    source_type: str # requirement, task, feature
    source_id: str
    target_type: str # component, module, api
    target_id: str

class Architecture(BaseModel):
    project_name: str = "Unknown"
    system_overview: str = ""
    architecture_style: str = "Modular Monolith"
    
    modules: List[Module] = Field(default_factory=list)
    apis: List[APIEndpoint] = Field(default_factory=list)
    data_models: List[DataModel] = Field(default_factory=list)
    
    dependencies: List[Dependency] = Field(default_factory=list)
    external_integrations: List[str] = Field(default_factory=list)
    
    technology_mapping: Dict[str, str] = Field(default_factory=dict)
    
    folder_structure: List[str] = Field(default_factory=list)
    data_flow: List[str] = Field(default_factory=list)
    
    security_considerations: List[str] = Field(default_factory=list)
    testing_strategy: List[str] = Field(default_factory=list)
    deployment_summary: str = ""
    configuration_requirements: List[str] = Field(default_factory=list)
    
    risks: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    
    traceability_links: List[TraceabilityLink] = Field(default_factory=list)

