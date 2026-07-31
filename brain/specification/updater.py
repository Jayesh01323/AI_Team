from .models import LivingSpecification
from .merger import merge_specifications
from .validator import validate_specification, ValidationResult
from typing import Tuple

def update_specification(current: LivingSpecification, update: LivingSpecification) -> Tuple[LivingSpecification, ValidationResult]:
    """Updates the specification by merging the update into the current specification.
    Returns the new merged specification and its validation result."""
    merged_spec = merge_specifications(current, update)
    validation_result = validate_specification(merged_spec)
    return merged_spec, validation_result

