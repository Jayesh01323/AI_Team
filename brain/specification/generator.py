"""
Living Specification Generator — Deterministic specification management.

This module provides the LivingSpecificationGenerator for creating and
managing Living Specifications. It is part of the DETERMINISTIC GENERATION
system, separate from the LLM-powered legacy stage system.

ARCHITECTURE BOUNDARY:
  - LivingSpecificationGenerator: Deterministic, no LLM calls
  - ProjectSpecificationGeneratorStage (below): Legacy LLM-based stage
"""

from typing import Any

# Legacy pipeline imports (only for ProjectSpecificationGeneratorStage below)
from core.logging import get_logger

from .exporter import (
    export_to_dict,
    export_to_json,
    generate_statistics,
    generate_summary,
)
from .merger import merge_specifications
from .models import LivingSpecification
from .updater import update_specification
from .validator import ValidationResult, validate_specification

logger = get_logger(__name__)


class LivingSpecificationGenerator:
    """The deterministic Living Specification Generator."""
    
    @staticmethod
    def generate(knowledge_data: dict[str, Any] | None = None, 
                 intent_data: dict[str, Any] | None = None, 
                 decision_data: dict[str, Any] | None = None) -> LivingSpecification:
        """Generates an initial Living Specification from the outputs of the 
        Knowledge Model, Intent Engine, and Decision Engine."""
        
        knowledge_data = knowledge_data or {}
        intent_data = intent_data or {}
        decision_data = decision_data or {}
        
        spec = LivingSpecification()
        
        # Extract from knowledge
        if "project_name" in knowledge_data:
            spec.project_name = knowledge_data["project_name"]
        if "vision" in knowledge_data:
            spec.vision = knowledge_data["vision"]
        if "mission" in knowledge_data:
            spec.mission = knowledge_data["mission"]
        if "problem_statement" in knowledge_data:
            spec.problem_statement = knowledge_data["problem_statement"]
        if "target_users" in knowledge_data:
            spec.target_users = list(knowledge_data["target_users"])
            
        # Extract from intent
        if "goals" in intent_data:
            spec.goals = list(intent_data["goals"])
        if "success_criteria" in intent_data:
            spec.success_criteria = list(intent_data["success_criteria"])
            
        # Extract from decisions
        if "accepted_decisions" in decision_data:
            spec.accepted_decisions = list(decision_data["accepted_decisions"])
        if "rejected_decisions" in decision_data:
            spec.rejected_decisions = list(decision_data["rejected_decisions"])
        if "superseded_decisions" in decision_data:
            spec.superseded_decisions = list(decision_data["superseded_decisions"])
            
        return spec
    
    @staticmethod
    def update(current: LivingSpecification, update: LivingSpecification) -> tuple[LivingSpecification, ValidationResult]:
        return update_specification(current, update)
        
    @staticmethod
    def validate(spec: LivingSpecification) -> ValidationResult:
        return validate_specification(spec)
        
    @staticmethod
    def merge(current: LivingSpecification, update: LivingSpecification) -> LivingSpecification:
        return merge_specifications(current, update)
        
    @staticmethod
    def export_json(spec: LivingSpecification, indent: int = 2) -> str:
        return export_to_json(spec, indent)
        
    @staticmethod
    def export_dict(spec: LivingSpecification) -> dict[str, Any]:
        return export_to_dict(spec)
        
    @staticmethod
    def summary(spec: LivingSpecification) -> str:
        return generate_summary(spec)
        
    @staticmethod
    def statistics(spec: LivingSpecification) -> dict[str, int]:
        return generate_statistics(spec)


# Note: ProjectSpecificationGeneratorStage has been moved to brain/specification/legacy_stage.py
# to avoid circular imports. It is imported in brain/stages/__init__.py from there.
