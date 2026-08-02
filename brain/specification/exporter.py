import json
from typing import Any

from .models import LivingSpecification


def export_to_dict(spec: LivingSpecification) -> dict[str, Any]:
    # Using pydantic's dict export, converting datetimes properly
    return spec.model_dump(mode='json')

def export_to_json(spec: LivingSpecification, indent: int = 2) -> str:
    return json.dumps(export_to_dict(spec), indent=indent)

def generate_summary(spec: LivingSpecification) -> str:
    summary_lines = [
        f"Project: {spec.project_name} (v{spec.version})",
        f"Status: {spec.current_state}",
        f"Confidence: {spec.confidence_score:.2f}",
        f"Vision: {spec.vision[:100]}..." if len(spec.vision) > 100 else f"Vision: {spec.vision}",
        f"Mission: {spec.mission[:100]}..." if len(spec.mission) > 100 else f"Mission: {spec.mission}",
        f"Requirements: {len(spec.functional_requirements)} Functional, {len(spec.non_functional_requirements)} Non-functional",
        f"Decisions: {len(spec.accepted_decisions)} Accepted, {len(spec.rejected_decisions)} Rejected",
        f"Last Updated: {spec.last_updated.isoformat()}"
    ]
    return "\n".join(summary_lines)

def generate_statistics(spec: LivingSpecification) -> dict[str, int]:
    return {
        "goals_count": len(spec.goals),
        "success_criteria_count": len(spec.success_criteria),
        "target_users_count": len(spec.target_users),
        "personas_count": len(spec.personas),
        "functional_requirements_count": len(spec.functional_requirements),
        "non_functional_requirements_count": len(spec.non_functional_requirements),
        "constraints_count": len(spec.constraints),
        "assumptions_count": len(spec.assumptions),
        "open_questions_count": len(spec.open_questions),
        "accepted_decisions_count": len(spec.accepted_decisions),
        "rejected_decisions_count": len(spec.rejected_decisions),
        "superseded_decisions_count": len(spec.superseded_decisions),
        "risks_count": len(spec.risks),
        "dependencies_count": len(spec.dependencies),
        "milestones_count": len(spec.milestones)
    }
