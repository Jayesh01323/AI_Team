"""
Deterministic rules for the Intent Engine.

This module contains all keyword-based rules used for classification,
extraction, and gap detection. No heuristics, no guessing, no hallucination.
Every rule is explicit and deterministic.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Project type classification rules
# ---------------------------------------------------------------------------

PROJECT_TYPE_RULES: dict[str, list[str]] = {
    "web_app": [
        "web app", "website", "web application", "web-based",
        "frontend", "backend", "fullstack", "full-stack",
        "react", "vue", "angular", "django", "flask", "fastapi",
        "streamlit", "gradio",
    ],
    "desktop": [
        "desktop app", "desktop application", "gui", "tkinter",
        "pyqt", "qt", "electron", "native app",
    ],
    "cli": [
        "cli", "command line", "command-line", "terminal tool",
        "console app", "console application",
    ],
    "library": [
        "library", "sdk", "package", "module", "framework",
        "api library",
    ],
    "api": [
        "api", "rest api", "graphql", "endpoint", "web service",
        "microservice",
    ],
    "browser_extension": [
        "browser extension", "chrome extension", "firefox extension",
        "plugin", "addon",
    ],
    "mobile": [
        "mobile app", "ios", "android", "flutter", "react native",
        "mobile application",
    ],
}

# ---------------------------------------------------------------------------
# Domain classification rules
# ---------------------------------------------------------------------------

DOMAIN_RULES: dict[str, list[str]] = {
    "ai": [
        "ai", "artificial intelligence", "machine learning", "ml",
        "deep learning", "neural network", "llm", "gpt", "claude",
        "computer vision", "nlp", "natural language processing",
        "rag", "retrieval augmented", "langchain", "llamaindex",
    ],
    "education": [
        "education", "edtech", "learning", "course", "student",
        "teacher", "classroom", "lms", "tutoring",
    ],
    "healthcare": [
        "healthcare", "health", "medical", "patient", "hospital",
        "clinic", "ehr", "emr", "hipaa",
    ],
    "finance": [
        "finance", "fintech", "banking", "payment", "trading",
        "investment", "crypto", "blockchain", "accounting",
    ],
    "developer_tools": [
        "developer tool", "devtool", "cli tool", "code review",
        "linter", "formatter", "debugger", "ide", "vscode",
        "git", "ci/cd", "deployment",
    ],
    "productivity": [
        "productivity", "task manager", "todo", "calendar",
        "notes", "notion", "project management", "kanban",
    ],
    "security": [
        "security", "cybersecurity", "vulnerability", "penetration",
        "firewall", "encryption", "authentication", "authorization",
    ],
    "ecommerce": [
        "ecommerce", "e-commerce", "shop", "store", "marketplace",
        "cart", "checkout", "payment gateway",
    ],
    "social": [
        "social", "chat", "messaging", "forum", "community",
        "social network", "feed",
    ],
    "iot": [
        "iot", "internet of things", "sensor", "embedded",
        "raspberry pi", "arduino",
    ],
}

# ---------------------------------------------------------------------------
# Product category rules
# ---------------------------------------------------------------------------

PRODUCT_CATEGORY_RULES: dict[str, list[str]] = {
    "saas": [
        "saas", "software as a service", "subscription", "cloud service",
        "hosted service", "multi-tenant",
    ],
    "open_source": [
        "open source", "open-source", "github", "free software",
        "community driven",
    ],
    "enterprise": [
        "enterprise", "b2b", "business-to-business", "corporate",
        "organization", "on-premise",
    ],
    "consumer": [
        "consumer", "b2c", "business-to-consumer", "mobile app",
        "game", "entertainment",
    ],
    "internal_tool": [
        "internal tool", "internal", "admin panel", "dashboard",
        "reporting tool", "analytics",
    ],
}

# ---------------------------------------------------------------------------
# Constraint extraction rules
# ---------------------------------------------------------------------------

CONSTRAINT_RULES: dict[str, tuple[list[str], str]] = {
    "technical": (
        [
            "python only", "python", "javascript only", "typescript only",
            "rust only", "go only", "java only", "offline first",
            "offline", "no cloud", "no docker", "docker required",
            "local deployment", "must run locally", "no external dependencies",
            "lightweight", "minimal dependencies",
        ],
        "technical",
    ),
    "budget": (
        [
            "budget", "free tier", "free", "low cost", "cost-effective",
            "affordable", "no budget", "limited budget", "$", "dollars",
        ],
        "budget",
    ),
    "time": (
        [
            "deadline", "timeline", "urgent", "asap", "quick",
            "fast", "short timeline", "weeks", "months",
        ],
        "time",
    ),
    "compliance": (
        [
            "gdpr", "hipaa", "pci dss", "sox", "compliance",
            "regulated", "audit", "privacy", "data protection",
        ],
        "compliance",
    ),
    "resource": (
        [
            "small team", "solo developer", "one person", "limited team",
            "part-time", "contractor", "freelancer",
        ],
        "resource",
    ),
    "preference": (
        [
            "prefer", "preferable", "ideally", "would like",
            "rather", "instead of",
        ],
        "preference",
    ),
}

# ---------------------------------------------------------------------------
# Preference extraction rules
# ---------------------------------------------------------------------------

PREFERENCE_RULES: dict[str, list[str]] = {
    "language": [
        "python", "javascript", "typescript", "rust", "go", "java",
        "c#", "ruby", "php", "swift", "kotlin", "use python",
        "use javascript", "written in",
    ],
    "framework": [
        "react", "vue", "angular", "django", "flask", "fastapi",
        "spring", "express", "next.js", "nuxt", "svelte",
        "use react", "use django", "built with",
    ],
    "database": [
        "postgresql", "postgres", "mysql", "mongodb", "redis",
        "sqlite", "elasticsearch", "dynamodb", "use postgres",
        "use mongodb", "database",
    ],
    "cloud": [
        "aws", "azure", "gcp", "google cloud", "heroku", "vercel",
        "netlify", "cloudflare", "deploy to aws", "hosted on",
    ],
    "architecture": [
        "microservices", "monolith", "serverless", "event-driven",
        "mvc", "mvvm", "clean architecture",
    ],
}

# ---------------------------------------------------------------------------
# Problem statement indicators
# ---------------------------------------------------------------------------

PROBLEM_INDICATORS: list[str] = [
    "problem", "issue", "pain point", "challenge", "difficulty",
    "struggle", "frustrated", "annoying", "slow", "inefficient",
    "manual", "tedious", "repetitive",
]

# ---------------------------------------------------------------------------
# Target user indicators
# ---------------------------------------------------------------------------

TARGET_USER_INDICATORS: list[str] = [
    "for", "target", "users", "customers", "clients",
    "personas", "audience", "market", "segment",
]

# ---------------------------------------------------------------------------
# Business goal indicators
# ---------------------------------------------------------------------------

BUSINESS_GOAL_INDICATORS: list[str] = [
    "goal", "objective", "target", "metric", "kpi",
    "increase", "decrease", "reduce", "improve", "optimize",
    "revenue", "profit", "growth", "retention", "engagement",
]

# ---------------------------------------------------------------------------
# Business model rules
# ---------------------------------------------------------------------------

BUSINESS_MODEL_RULES: dict[str, list[str]] = {
    "saas": ["saas", "subscription", "monthly", "yearly", "recurring"],
    "freemium": ["freemium", "free tier", "free plan", "premium"],
    "one_time": ["one-time", "perpetual", "lifetime", "single payment"],
    "marketplace": ["marketplace", "platform", "commission", "transaction"],
    "advertising": ["ads", "advertising", "sponsored", "ad-supported"],
    "open_source": ["open source", "free software", "community"],
}

# ---------------------------------------------------------------------------
# Confidence scoring rules
# ---------------------------------------------------------------------------

# Base confidence for explicit statements
EXPLICIT_STATEMENT_CONFIDENCE: float = 0.9

# Confidence reduction factors
CONFIDENCE_REDUCTION_AMBIGUOUS: float = 0.2
CONFIDENCE_REDUCTION_IMPLIED: float = 0.3
CONFIDENCE_REDUCTION_VAGUE: float = 0.4

# Minimum confidence threshold for including a fact
MIN_CONFIDENCE_THRESHOLD: float = 0.5

# ---------------------------------------------------------------------------
# Gap detection thresholds
# ---------------------------------------------------------------------------

# Minimum required sections that must be populated
MIN_REQUIRED_SECTIONS: int = 4

# Confidence threshold below which a section is considered incomplete
GAP_CONFIDENCE_THRESHOLD: float = 0.6

# ---------------------------------------------------------------------------
# Question generation limits
# ---------------------------------------------------------------------------

MAX_QUESTIONS: int = 5
MIN_QUESTION_IMPORTANCE: str = "medium"

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def match_keywords(text: str, keywords: list[str]) -> bool:
    """
    Check if any keyword is present in the text.

    Args:
        text: Text to search in.
        keywords: List of keywords to match.

    Returns:
        True if any keyword is found, False otherwise.
    """
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def get_matched_keywords(text: str, keywords: list[str]) -> list[str]:
    """
    Get all keywords that match in the text.

    Args:
        text: Text to search in.
        keywords: List of keywords to match.

    Returns:
        List of matched keywords.
    """
    text_lower = text.lower()
    return [keyword for keyword in keywords if keyword in text_lower]


def classify_by_rules(
    text: str,
    rules: dict[str, list[str]],
) -> tuple[str | None, float, list[str]]:
    """
    Classify text using keyword rules.

    Args:
        text: Text to classify.
        rules: Mapping of category to list of keywords.

    Returns:
        Tuple of (category, confidence, matched_keywords).
        Returns (None, 0.0, []) if no match found.
    """
    best_category: str | None = None
    best_score: float = 0.0
    best_keywords: list[str] = []

    for category, keywords in rules.items():
        matched = get_matched_keywords(text, keywords)
        if matched:
            # Confidence based on number of matches
            confidence = min(0.5 + (len(matched) * 0.1), 1.0)
            if confidence > best_score:
                best_category = category
                best_score = confidence
                best_keywords = matched

    return best_category, best_score, best_keywords


def is_explicit_statement(text: str) -> bool:
    """
    Check if text appears to be an explicit statement.

    Args:
        text: Text to check.

    Returns:
        True if text appears explicit, False otherwise.
    """
    text_lower = text.lower().strip()
    explicit_indicators = [
        "i want", "i need", "i would like", "build", "create",
        "develop", "make", "design", "implement",
    ]
    # Must start with an explicit indicator
    return any(text_lower.startswith(indicator) for indicator in explicit_indicators)


def is_ambiguous(text: str) -> bool:
    """
    Check if text contains ambiguous language.

    Args:
        text: Text to check.

    Returns:
        True if text is ambiguous, False otherwise.
    """
    ambiguous_indicators = [
        "maybe", "possibly", "might", "could", "perhaps",
        "not sure", "i think", "probably", "somewhat",
    ]
    return match_keywords(text, ambiguous_indicators)


def is_vague(text: str) -> bool:
    """
    Check if text is vague or underspecified.

    Args:
        text: Text to check.

    Returns:
        True if text is vague, False otherwise.
    """
    vague_indicators = [
        "stuff", "things", "something", "anything", "whatever",
        "etc", "and so on", "and stuff", "or something",
    ]
    return match_keywords(text, vague_indicators)