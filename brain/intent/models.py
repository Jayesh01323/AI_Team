"""
Data models for the Intent Engine.

These models represent the intermediate and final outputs of the intent
analysis pipeline. They are separate from the Product Knowledge Model
(``brain.knowledge``) but are designed to update it.

All models use Pydantic v2 for validation, serialization, and type safety,
consistent with the existing knowledge models.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from brain.knowledge import (
    ConfidenceLevel,
    ConfidenceScore,
    OpenQuestion,
    ProjectKnowledge,
    QuestionImportance,
)

# ---------------------------------------------------------------------------
# Input normalization
# ---------------------------------------------------------------------------


class NormalizedInput(BaseModel):
    """
    Normalized user input ready for deterministic analysis.

    Attributes:
        raw_text: The original, unmodified input text.
        normalized_text: Lowercased, whitespace-collapsed text.
        sentences: The input split into individual sentences.
    """

    model_config = ConfigDict(use_enum_values=True)

    raw_text: str = Field(default="", description="Original input text.")
    normalized_text: str = Field(default="", description="Lowercased, cleaned text.")
    sentences: list[str] = Field(default_factory=list, description="Sentences extracted from input.")


# ---------------------------------------------------------------------------
# Extraction results
# ---------------------------------------------------------------------------


class ExtractedFact(BaseModel):
    """
    A single fact explicitly extracted from the conversation.

    Attributes:
        category: Fact category — ``product``, ``business_model``,
            ``target_user``, ``business_goal``, ``problem``,
            ``requirement``, ``constraint``, or ``preference``.
        value: The extracted value.
        source_text: The text segment from which the fact was extracted.
        confidence: Confidence score for this fact.
    """

    model_config = ConfigDict(use_enum_values=True)

    category: str = Field(..., description="Fact category.")
    value: str = Field(..., min_length=1, description="The extracted value.")
    source_text: str = Field(default="", description="Source text segment.")
    confidence: ConfidenceScore = Field(default_factory=ConfidenceScore)


# ---------------------------------------------------------------------------
# Classification results
# ---------------------------------------------------------------------------


class ClassificationResult(BaseModel):
    """
    Result of classifying an aspect of the project.

    Attributes:
        category: Classification category — ``project_type``, ``domain``,
            or ``product_category``.
        value: The classified value.
        confidence: Confidence score for this classification.
        matched_keywords: Keywords that triggered this classification.
    """

    model_config = ConfigDict(use_enum_values=True)

    category: str = Field(..., description="Classification category.")
    value: str = Field(..., description="The classified value.")
    confidence: ConfidenceScore = Field(default_factory=ConfidenceScore)
    matched_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords that triggered this classification.",
    )


# ---------------------------------------------------------------------------
# Gap detection
# ---------------------------------------------------------------------------


class Gap(BaseModel):
    """
    A detected gap in the project knowledge.

    Attributes:
        section: Schema section name with the gap.
        description: Human-readable description of what is missing.
        is_blocking: Whether this gap blocks further progress.
        importance: Importance level of resolving this gap.
    """

    model_config = ConfigDict(use_enum_values=True)

    section: str = Field(..., description="Schema section name with the gap.")
    description: str = Field(..., description="What is missing.")
    is_blocking: bool = Field(default=False, description="Whether this gap blocks progress.")
    importance: QuestionImportance = Field(
        default=QuestionImportance.MEDIUM,
        description="Importance of resolving this gap.",
    )


# ---------------------------------------------------------------------------
# Confidence
# ---------------------------------------------------------------------------


class SectionConfidence(BaseModel):
    """
    Confidence score for a specific knowledge section.

    Attributes:
        section: Section name.
        score: Numeric confidence score between 0.0 and 1.0.
        level: Qualitative confidence level.
        reasoning: Why this score was assigned.
    """

    model_config = ConfigDict(use_enum_values=True)

    section: str = Field(..., description="Section name.")
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="Numeric confidence score.")
    level: ConfidenceLevel = Field(default=ConfidenceLevel.UNKNOWN)
    reasoning: str = Field(default="", description="Why this score was assigned.")


# ---------------------------------------------------------------------------
# Aggregate results
# ---------------------------------------------------------------------------


class IntentAnalysis(BaseModel):
    """
    Complete intent analysis output.

    Combines all intermediate results from the pipeline stages:
    classification, extraction, gap detection, confidence, and questions.
    """

    model_config = ConfigDict(use_enum_values=True)

    classifications: list[ClassificationResult] = Field(default_factory=list)
    extracted_facts: list[ExtractedFact] = Field(default_factory=list)
    gaps: list[Gap] = Field(default_factory=list)
    section_confidences: list[SectionConfidence] = Field(default_factory=list)
    overall_confidence: SectionConfidence = Field(
        default_factory=lambda: SectionConfidence(section="overall_intent")
    )
    questions: list[OpenQuestion] = Field(default_factory=list)


class IntentResult(BaseModel):
    """
    Final result of the Intent Engine.

    Contains the full intent analysis and the updated ProjectKnowledge.
    """

    model_config = ConfigDict(use_enum_values=True)

    analysis: IntentAnalysis = Field(default_factory=IntentAnalysis)
    knowledge: ProjectKnowledge = Field(default_factory=ProjectKnowledge)