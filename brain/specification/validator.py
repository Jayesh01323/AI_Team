from typing import Dict, Any, List
from .models import LivingSpecification

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


def validate_specification(spec: LivingSpecification) -> ValidationResult:
    result = ValidationResult()

    # 1. Required sections
    if not spec.project_name:
        result.add_error("Missing required section: project_name")
    if not spec.vision:
        result.add_warning("Missing section: vision")
    if not spec.problem_statement:
        result.add_warning("Missing section: problem_statement")

    # 2. Duplicate requirements
    req_ids = set()
    for req in spec.functional_requirements + spec.non_functional_requirements:
        if req.id in req_ids:
            result.add_error(f"Duplicate requirement ID found: {req.id}")
        req_ids.add(req.id)

    # 3. Duplicate decisions
    dec_ids = set()
    for dec in spec.accepted_decisions + spec.rejected_decisions + spec.superseded_decisions:
        if dec.id in dec_ids:
            result.add_error(f"Duplicate decision ID found: {dec.id}")
        dec_ids.add(dec.id)

    # 4. Conflicting tech selections - simplest heuristic, if tech stack has conflicting keys like multiple frameworks
    # As this is a generic deterministic generator, we might just check for duplicate keys in dictionary (which is handled by python Dict)
    # We can check if confidence score is valid
    if not (0.0 <= spec.confidence_score <= 1.0):
        result.add_error(f"Invalid confidence score: {spec.confidence_score}. Must be between 0 and 1.")

    # 5. Constraints consistency - if constraints have duplicate IDs
    const_ids = set()
    for const in spec.constraints:
        if const.id in const_ids:
            result.add_error(f"Duplicate constraint ID found: {const.id}")
        const_ids.add(const.id)

    return result

