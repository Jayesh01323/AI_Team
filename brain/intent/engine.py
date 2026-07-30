"""
Intent Engine orchestrator.

Coordinates the full intent analysis pipeline:
Normalization → Extraction → Classification → Gap Detection →
Confidence → Question Generation → ProjectKnowledge Update
"""

from __future__ import annotations

from brain.intent.classifier import classify_all
from brain.intent.confidence import calculate_overall_confidence, calculate_section_confidence
from brain.intent.extractor import extract_all_facts
from brain.intent.gap_detector import detect_gaps
from brain.intent.models import (
    ClassificationResult,
    ExtractedFact,
    IntentAnalysis,
    IntentResult,
    SectionConfidence,
)
from brain.knowledge import ProjectKnowledge
from brain.intent.question_generator import generate_questions


class IntentEngine:
    """
    The Intent Engine converts natural language conversations into
    structured Project Knowledge.

    Determines WHAT the user is trying to build.
    Does NOT decide HOW to build it.
    """

    def analyze(self, conversation_text: str) -> IntentResult:
        """
        Analyze a conversation and produce structured intent output.

        Args:
            conversation_text: Raw user conversation text.

        Returns:
            IntentResult containing analysis and updated ProjectKnowledge.
        """
        # Step 1: Normalize input
        normalized = self._normalize(conversation_text)

        # Step 2: Extract explicit facts
        extracted_facts = extract_all_facts(normalized)

        # Step 3: Classify project aspects
        classifications = classify_all(normalized)

        # Step 4: Build initial ProjectKnowledge from extracted facts
        knowledge = self._build_knowledge(extracted_facts, classifications)

        # Step 5: Detect gaps
        knowledge_dict = knowledge.model_dump()
        gaps = detect_gaps(knowledge_dict)

        # Step 6: Calculate confidence per section
        section_confidences = self._calculate_section_confidences(knowledge, extracted_facts)

        # Step 7: Calculate overall confidence
        overall_confidence = calculate_overall_confidence(section_confidences)

        # Step 8: Generate questions only if needed
        known_sections = self._get_known_sections(knowledge)
        questions = generate_questions(gaps, known_sections)

        # Step 9: Assemble final analysis
        analysis = IntentAnalysis(
            classifications=classifications,
            extracted_facts=extracted_facts,
            gaps=gaps,
            section_confidences=section_confidences,
            overall_confidence=overall_confidence,
            questions=questions,
        )

        # Step 10: Update knowledge timestamp
        knowledge.touch()

        return IntentResult(analysis=analysis, knowledge=knowledge)

    def _normalize(self, text: str) -> str:
        """
        Normalize user input.

        Args:
            text: Raw input text.

        Returns:
            Normalized text.
        """
        return text.strip().lower()

    def _build_knowledge(
        self,
        facts: list[ExtractedFact],
        classifications: list[ClassificationResult],
    ) -> ProjectKnowledge:
        """
        Build ProjectKnowledge from extracted facts and classifications.

        Args:
            facts: Extracted facts.
            classifications: Classification results.

        Returns:
            Populated ProjectKnowledge.
        """
        from brain.knowledge import (
            Constraint,
            ConstraintType,
            KnowledgeSource,
            Requirement,
            UserPreference,
        )

        knowledge = ProjectKnowledge()

        # Apply classifications
        for classification in classifications:
            if classification.category == "project_type":
                knowledge.extra["project_type"] = classification.value
            elif classification.category == "domain":
                knowledge.extra["domain"] = classification.value
            elif classification.category == "product_category":
                knowledge.extra["product_category"] = classification.value

        # Apply facts
        for fact in facts:
            if fact.category == "problem":
                knowledge.problem = fact.value
            elif fact.category == "target_user":
                knowledge.target_users.append(fact.value)
            elif fact.category == "business_goal":
                knowledge.business_goals.append(fact.value)
            elif fact.category == "business_model":
                knowledge.extra["business_model"] = fact.value
            elif fact.category == "requirement":
                knowledge.functional_requirements.append(
                    Requirement(
                        title=fact.value,
                        source=KnowledgeSource.USER,
                        confidence=fact.confidence,
                    )
                )
            elif fact.category == "constraint":
                knowledge.constraints.append(
                    Constraint(
                        name=fact.value,
                        type=ConstraintType.TECHNICAL,
                        source=KnowledgeSource.USER,
                        confidence=fact.confidence,
                    )
                )
            elif fact.category == "preference":
                knowledge.user_preferences.append(
                    UserPreference(
                        category="general",
                        key="preference",
                        value=fact.value,
                        source=KnowledgeSource.USER,
                        confidence=fact.confidence,
                    )
                )

        return knowledge

    def _calculate_section_confidences(
        self,
        knowledge: ProjectKnowledge,
        facts: list[ExtractedFact],
    ) -> list[SectionConfidence]:
        """
        Calculate confidence for each knowledge section.

        Args:
            knowledge: Current ProjectKnowledge.
            facts: Extracted facts.

        Returns:
            List of SectionConfidence for each section.
        """
        confidences: list[SectionConfidence] = []

        # Vision
        confidences.append(
            calculate_section_confidence(
                section_name="vision",
                has_content=bool(knowledge.vision),
                explicit_count=sum(1 for f in facts if f.category == "vision"),
                total_indicators=1,
            )
        )

        # Problem
        confidences.append(
            calculate_section_confidence(
                section_name="problem",
                has_content=bool(knowledge.problem),
                explicit_count=sum(1 for f in facts if f.category == "problem"),
                total_indicators=1,
            )
        )

        # Target users
        confidences.append(
            calculate_section_confidence(
                section_name="target_users",
                has_content=len(knowledge.target_users) > 0,
                explicit_count=len(knowledge.target_users),
                total_indicators=max(len(knowledge.target_users), 1),
            )
        )

        # Business goals
        confidences.append(
            calculate_section_confidence(
                section_name="business_goals",
                has_content=len(knowledge.business_goals) > 0,
                explicit_count=len(knowledge.business_goals),
                total_indicators=max(len(knowledge.business_goals), 1),
            )
        )

        # Requirements
        confidences.append(
            calculate_section_confidence(
                section_name="functional_requirements",
                has_content=len(knowledge.functional_requirements) > 0,
                explicit_count=len(knowledge.functional_requirements),
                total_indicators=max(len(knowledge.functional_requirements), 1),
            )
        )

        # Constraints
        confidences.append(
            calculate_section_confidence(
                section_name="constraints",
                has_content=len(knowledge.constraints) > 0,
                explicit_count=len(knowledge.constraints),
                total_indicators=max(len(knowledge.constraints), 1),
            )
        )

        return confidences

    def _get_known_sections(self, knowledge: ProjectKnowledge) -> list[str]:
        """
        Get list of section names that are already populated.

        Args:
            knowledge: Current ProjectKnowledge.

        Returns:
            List of populated section names.
        """
        known: list[str] = []

        if knowledge.vision:
            known.append("vision")
        if knowledge.problem:
            known.append("problem")
        if knowledge.target_users:
            known.append("target_users")
        if knowledge.business_goals:
            known.append("business_goals")
        if knowledge.functional_requirements:
            known.append("functional_requirements")
        if knowledge.non_functional_requirements:
            known.append("non_functional_requirements")
        if knowledge.constraints:
            known.append("constraints")
        if knowledge.user_preferences:
            known.append("user_preferences")

        return known