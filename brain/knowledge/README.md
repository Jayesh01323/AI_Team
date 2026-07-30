# Product Knowledge Model

## Purpose

The Product Knowledge Model is the **single source of truth** for everything the AI Engineering Team knows about a software project. It captures WHAT the system knows — not HOW that knowledge is extracted or generated.

This package is the foundation of Milestone 4. Every future component reads from and writes to the `ProjectKnowledge` aggregate root.

---

## Design Philosophy

1. **Data, not logic.** These models represent knowledge state. No extraction, inference, decision, or recommendation logic lives here.
2. **Progressive enrichment.** A `ProjectKnowledge` artifact starts empty and is populated section by section as the system learns more.
3. **Strong typing.** All fields use Pydantic v2 with type hints, validation, and enum constraints. No raw strings for status or priority values.
4. **Extensibility.** The `extra` dictionary on `ProjectKnowledge` and the generic `UserPreference` model allow future growth without schema migrations.
5. **Provenance tracking.** Every knowledge artifact records its `source` (user, AI inference, system default, external research, validation) and a `ConfidenceScore`.

---

## Why This Package Exists

Milestones 1–3 built the Engineering Brain pipeline (idea → requirements → PRD → architecture → tasks) and the Execution Engine. However, there was no unified, versioned knowledge model that captured the full state of a project in a single queryable structure.

This package fills that gap. It provides:

- A **versioned** knowledge artifact (`ProjectMetadata.version`)
- A **lifecycle-aware** state machine (`ProjectState` enum)
- **Confidence scoring** on every knowledge item
- **Provenance tracking** for auditability
- A **declarative schema** for completeness validation

---

## Package Structure

```
brain/knowledge/
├── __init__.py      # Public API exports
├── enums.py         # All enumerations (status, priority, confidence, etc.)
├── models.py        # Pydantic v2 data models
├── schema.py        # Declarative project schema definition
└── README.md        # This file
```

---

## Core Models

| Model | Description |
|-------|-------------|
| `ProjectKnowledge` | Aggregate root — the complete knowledge artifact |
| `ProjectMetadata` | Version, timestamps, lifecycle state |
| `Decision` | A decision with topic, value, rationale, alternatives, confidence |
| `Requirement` | Functional or non-functional requirement with priority and status |
| `Constraint` | Budget, technical, time, compliance, or resource constraint |
| `Assumption` | An unverified belief about the project context |
| `OpenQuestion` | An unanswered question with importance and blocking flag |
| `UserPreference` | Generic key-value preference (language, framework, cloud, etc.) |
| `ConfidenceScore` | Qualitative level + optional numeric score + provenance |

---

## Enums

| Enum | Values |
|------|--------|
| `DecisionStatus` | Pending, Accepted, Rejected, Deprecated |
| `RequirementPriority` | Critical, High, Medium, Low |
| `RequirementStatus` | Proposed, Approved, Implemented, Removed |
| `QuestionImportance` | Critical, High, Medium, Low |
| `ConfidenceLevel` | Unknown, Low, Medium, High, Certain |
| `ProjectState` | Initialization, Discovery, Planning, Architecture, Implementation, Testing, Deployment, Completed |
| `ConstraintType` | Budget, Technical, Time, Compliance, Resource, Preference, Other |
| `KnowledgeSource` | User, AI Inference, System Default, External Research, Validation |

---

## Relationship with Future Milestone 4 Components

| Component | Relationship |
|-----------|-------------|
| **Intent Engine** | Reads `vision`, `problem`, `business_goals` to understand user intent. Writes initial `ProjectKnowledge`. |
| **Decision Engine** | Reads and writes `decisions`. Updates `DecisionStatus` as decisions are accepted or rejected. |
| **Product Specification Generator** | Reads `functional_requirements`, `non_functional_requirements`, `constraints`. Writes `architecture_notes`. |
| **Planning Engine** | Reads requirements and decisions to generate task plans. Writes `testing_notes` and `deployment_notes`. |
| **Architecture Engine** | Reads constraints and preferences. Writes `architecture_notes` and tech stack decisions. |
| **Multi-Agent System** | All agents read from and write to `ProjectKnowledge`. Uses `ConfidenceScore` to prioritize work. |

---

## How Future Agents Should Use These Models

1. **Read** the current `ProjectKnowledge` artifact at the start of each task.
2. **Write** new findings back to the appropriate section (e.g., add a `Decision`, append to `assumptions`).
3. **Update** `metadata.updated_at` via `knowledge.touch()` after any modification.
4. **Track provenance** by setting the `source` field on every new artifact.
5. **Assess confidence** by attaching a `ConfidenceScore` to uncertain knowledge.
6. **Validate completeness** using `schema.is_complete()` to identify missing sections.

---

## Usage Example

```python
from brain.knowledge import (
    ProjectKnowledge,
    Decision,
    Requirement,
    RequirementPriority,
    DecisionStatus,
    ConfidenceLevel,
    ConfidenceScore,
)

# Create an empty knowledge artifact
knowledge = ProjectKnowledge()

# Populate vision and problem
knowledge.vision = "Build an AI-powered code review tool"
knowledge.problem = "Code reviews are slow and inconsistent"

# Add a decision
knowledge.decisions.append(
    Decision(
        topic="language",
        value="python",
        rationale="Team expertise and ecosystem",
        alternatives=["typescript", "go"],
        status=DecisionStatus.ACCEPTED,
        confidence=ConfidenceScore(level=ConfidenceLevel.HIGH),
    )
)

# Add a requirement
knowledge.functional_requirements.append(
    Requirement(
        title="PR Analysis",
        description="Analyze pull requests and provide feedback",
        priority=RequirementPriority.CRITICAL,
    )
)

# Update timestamp
knowledge.touch()

# Serialize
data = knowledge.model_dump()