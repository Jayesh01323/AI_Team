from typing import List, Dict
from brain.specification.models import LivingSpecification, Requirement
from brain.planner.models import Plan, Task
from .models import Component, Module, TraceabilityLink, Architecture

class ArchitectureMapper:
    @staticmethod
    def map_requirements_to_components(spec: LivingSpecification, arch: Architecture) -> None:
        """
        Maps Functional Requirements to Components deterministically.
        We group requirements into logical components (e.g. grouped by domain keywords if possible, 
        but for deterministic generic mapping, we create a core module and map requirements to services).
        """
        core_module = next((m for m in arch.modules if m.id == "mod_core"), None)
        if not core_module:
            core_module = Module(id="mod_core", name="Core Business Logic")
            arch.modules.append(core_module)
            
        for req in spec.functional_requirements:
            comp_id = f"comp_{req.id}"
            comp = Component(
                id=comp_id,
                name=f"{req.id.capitalize()} Service",
                description=f"Service handling: {req.description}",
                type="service"
            )
            core_module.components.append(comp)
            
            link = TraceabilityLink(
                source_type="requirement",
                source_id=req.id,
                target_type="component",
                target_id=comp_id
            )
            arch.traceability_links.append(link)

    @staticmethod
    def map_tasks_to_components(plan: Plan, arch: Architecture) -> None:
        """
        Maps tasks from the planner to existing components if possible.
        """
        # Find all tasks
        tasks = []
        for m in plan.milestones:
            for e in m.epics:
                for f in e.features:
                    tasks.extend(f.tasks)
                    
        for task in tasks:
            # Simple heuristic mapping for demonstration:
            # We look for a component with similar ID structure or just map it to the first core component.
            # In a deterministic generator, we link task "t_req1" to "comp_req1"
            
            req_id = task.id.replace("t_", "") if task.id.startswith("t_") else task.id
            comp_id = f"comp_{req_id}"
            
            # Verify component exists
            comp_exists = False
            for mod in arch.modules:
                for comp in mod.components:
                    if comp.id == comp_id:
                        comp.tasks.append(task.id)
                        comp_exists = True
                        
                        link = TraceabilityLink(
                            source_type="task",
                            source_id=task.id,
                            target_type="component",
                            target_id=comp_id
                        )
                        arch.traceability_links.append(link)
                        break
                if comp_exists:
                    break

    @staticmethod
    def map_technology(spec: LivingSpecification, arch: Architecture) -> None:
        for key, value in spec.technology_stack.items():
            arch.technology_mapping[key] = value

