from .code_models import GeneratedProject, GeneratedFile
from .code_renderer import CodeRenderer
from .code_validator import CodeValidator
from brain.project_generator.models import ProjectBlueprint
from brain.project_generator.template_models import ResolvedTemplateSet

class CodeGenerator:
    def __init__(self):
        self.renderer = CodeRenderer()
        self.validator = CodeValidator()

    def generate(self, blueprint: ProjectBlueprint, templates: ResolvedTemplateSet) -> GeneratedProject:
        variables = {
            "PROJECT_NAME": blueprint.project_name
        }
        
        generated_files = []
        
        # Deterministically order generation by dependency ordering if available, else by id
        ordered_templates = sorted(templates.selected_templates, key=lambda t: templates.dependency_ordering.index(t.id) if t.id in templates.dependency_ordering else 999)
        
        for template in ordered_templates:
            # Generate deterministic mock content for the template
            raw_content = f"Project: {{{{PROJECT_NAME}}}}\nTemplate: {template.name}"
            content = self.renderer.render(raw_content, variables)
            
            gf = GeneratedFile(
                path=f"src/{template.id}/main.py",
                filename="main.py",
                content=content,
                language="python",
                category=template.category,
                component="core",
                template_id=template.id,
                generated_from="code_generator",
                metadata={"source": "template"}
            )
            gf.checksum = gf.calculate_checksum()
            generated_files.append(gf)
            
        project = GeneratedProject(
            generated_files=generated_files,
            generation_summary=f"Generated from {len(templates.selected_templates)} templates",
            generation_metadata={"blueprint_name": blueprint.project_name}
        )
        
        project.validation_result = self.validator.validate(project)
        return project
