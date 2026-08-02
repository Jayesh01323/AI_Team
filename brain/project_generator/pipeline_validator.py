from typing import List, Tuple, Any
from .pipeline_models import PipelineExecution


class PipelineValidator:
    def validate_stage_transition(self, execution: PipelineExecution, current_stage_name: str, expected_order: int) -> Tuple[bool, List[str]]:
        errors = []
        
        # Check ordering
        if len(execution.stages) > 0:
            last_stage = execution.stages[-1]
            if last_stage.execution_order >= expected_order:
                errors.append(f"Invalid stage ordering. Expected > {last_stage.execution_order}, got {expected_order}")
                
            if not last_stage.success:
                errors.append(f"Cannot transition to {current_stage_name}: previous stage {last_stage.name} failed")
                
        # Check duplicate
        if any(s.name == current_stage_name for s in execution.stages):
            errors.append(f"Duplicate execution of stage: {current_stage_name}")
            
        errors.sort()
        return len(errors) == 0, errors

    def validate_dependency(self, obj: Any, obj_name: str) -> Tuple[bool, List[str]]:
        if obj is None:
            return False, [f"Null dependency: {obj_name} is required for the next stage"]
        return True, []
