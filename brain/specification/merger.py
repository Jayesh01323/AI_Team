from datetime import datetime
from typing import Any

from .models import (
    Decision,
    EntityStatus,
    LivingSpecification,
)


def merge_lists(existing: list[Any], new: list[Any], key_attr: str = "id") -> list[Any]:
    """Merges two lists of objects, preferring new objects if they exist, 
    but retaining existing objects if not in new list."""
    merged_dict = {getattr(item, key_attr): item for item in existing}
    for item in new:
        merged_dict[getattr(item, key_attr)] = item
    return list(merged_dict.values())

def merge_decisions(existing: list[Decision], new: list[Decision]) -> list[Decision]:
    """Merges decisions. Never silently removes accepted decisions. 
    If a decision was accepted, and new update doesn't have it, keep it.
    If new update changes status of accepted decision without explicit supersede/reject, keep it accepted."""
    merged_dict = {item.id: item for item in existing}
    for item in new:
        if item.id in merged_dict:
            old_item = merged_dict[item.id]
            if old_item.status == EntityStatus.ACCEPTED and item.status not in [EntityStatus.REJECTED, EntityStatus.SUPERSEDED]:
                # Preserve accepted status if not explicitly rejected or superseded
                item.status = EntityStatus.ACCEPTED
        merged_dict[item.id] = item
    return list(merged_dict.values())

def merge_specifications(current: LivingSpecification, update: LivingSpecification) -> LivingSpecification:
    """Deterministically merges an updated specification into the current specification."""
    
    # 1. Scalar fields (prefer update if truthy)
    project_name = update.project_name if update.project_name and update.project_name != "Unknown Project" else current.project_name
    version = update.version if update.version and update.version != "0.1.0" else current.version
    vision = update.vision or current.vision
    mission = update.mission or current.mission
    problem_statement = update.problem_statement or current.problem_statement
    architecture_summary = update.architecture_summary or current.architecture_summary
    current_state = update.current_state or current.current_state
    
    # Update confidence score
    confidence_score = update.confidence_score if update.confidence_score > 0 else current.confidence_score

    # 2. List fields of strings (union and deduplicate, preserve order)
    def merge_string_lists(l1: list[str], l2: list[str]) -> list[str]:
        seen = set()
        result = []
        for item in l1 + l2:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    goals = merge_string_lists(current.goals, update.goals)
    success_criteria = merge_string_lists(current.success_criteria, update.success_criteria)
    target_users = merge_string_lists(current.target_users, update.target_users)
    assumptions = merge_string_lists(current.assumptions, update.assumptions)
    open_questions = merge_string_lists(current.open_questions, update.open_questions)
    risks = merge_string_lists(current.risks, update.risks)
    dependencies = merge_string_lists(current.dependencies, update.dependencies)
    milestones = merge_string_lists(current.milestones, update.milestones)
    
    # 3. Object lists (merge by id/name)
    personas = merge_lists(current.personas, update.personas, key_attr="name")
    functional_requirements = merge_lists(current.functional_requirements, update.functional_requirements)
    non_functional_requirements = merge_lists(current.non_functional_requirements, update.non_functional_requirements)
    constraints = merge_lists(current.constraints, update.constraints)
    
    # 4. Decisions
    accepted_decisions = merge_decisions(current.accepted_decisions, update.accepted_decisions)
    rejected_decisions = merge_decisions(current.rejected_decisions, update.rejected_decisions)
    superseded_decisions = merge_decisions(current.superseded_decisions, update.superseded_decisions)
    
    # 5. Technology Stack (dict update)
    technology_stack = current.technology_stack.copy()
    technology_stack.update(update.technology_stack)

    # Reconstruct merged spec
    merged_spec = LivingSpecification(
        project_name=project_name,
        version=version,
        vision=vision,
        mission=mission,
        problem_statement=problem_statement,
        goals=goals,
        success_criteria=success_criteria,
        target_users=target_users,
        personas=personas,
        functional_requirements=functional_requirements,
        non_functional_requirements=non_functional_requirements,
        constraints=constraints,
        assumptions=assumptions,
        open_questions=open_questions,
        accepted_decisions=accepted_decisions,
        rejected_decisions=rejected_decisions,
        superseded_decisions=superseded_decisions,
        technology_stack=technology_stack,
        architecture_summary=architecture_summary,
        risks=risks,
        dependencies=dependencies,
        milestones=milestones,
        current_state=current_state,
        confidence_score=confidence_score,
        last_updated=datetime.utcnow()
    )
    
    return merged_spec
