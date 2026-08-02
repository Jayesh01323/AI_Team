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
    technologies: list[str] = Field(default_factory=list)
    tasks: list[str] = Field(default_factory=list) # Traceability to tasks

class Module(BaseModel):
    id: str
    name: str
    components: list[Component] = Field(default_factory=list)

class APIEndpoint(BaseModel):
    id: str
    path: str
    method: str
    description: str
    module_id: str | None = None

class DataModel(BaseModel):
    id: str
    name: str
    fields: dict[str, str] = Field(default_factory=dict)
    
class TraceabilityLink(BaseModel):
    source_type: str # requirement, task, feature
    source_id: str
    target_type: str # component, module, api
    target_id: str

class Architecture(BaseModel):
    project_name: str = "Unknown"
    system_overview: str = ""
    architecture_style: str = "Modular Monolith"
    
    modules: list[Module] = Field(default_factory=list)
    apis: list[APIEndpoint] = Field(default_factory=list)
    data_models: list[DataModel] = Field(default_factory=list)
    
    dependencies: list[Dependency] = Field(default_factory=list)
    external_integrations: list[str] = Field(default_factory=list)
    
    technology_mapping: dict[str, str] = Field(default_factory=dict)
    
    folder_structure: list[str] = Field(default_factory=list)
    data_flow: list[str] = Field(default_factory=list)
    
    security_considerations: list[str] = Field(default_factory=list)
    testing_strategy: list[str] = Field(default_factory=list)
    deployment_summary: str = ""
    configuration_requirements: list[str] = Field(default_factory=list)
    
    risks: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    
    traceability_links: list[TraceabilityLink] = Field(default_factory=list)

