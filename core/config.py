"""
Centralized configuration management.

All environment-variable loading happens here.
Providers and other modules read config from this module.
"""

import os
from pathlib import Path

# ── Project Paths ──────────────────────────────────────────────────────────

ROOT_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"


# ── AI Provider Configuration ──────────────────────────────────────────────

# Which provider to use: "openai", "anthropic", "gemini"
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai").lower().strip()

# OpenAI
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

# Anthropic
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
ANTHROPIC_MAX_TOKENS: int = int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096"))

# Gemini
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")


# ── Logging Configuration ──────────────────────────────────────────────────

LOG_LEVEL: str = os.getenv("AI_TEAM_LOG_LEVEL", "INFO").upper()
LOG_FORMAT: str = os.getenv(
    "AI_TEAM_LOG_FORMAT",
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


# ── Validation ─────────────────────────────────────────────────────────────


def validate() -> list[str]:
    """Validate configuration and return a list of issues (empty if valid)."""
    issues: list[str] = []

    if AI_PROVIDER not in ("openai", "anthropic", "gemini"):
        issues.append(
            f"AI_PROVIDER='{AI_PROVIDER}' is not supported. "
            f"Use 'openai', 'anthropic', or 'gemini'."
        )

    if AI_PROVIDER == "openai" and not OPENAI_API_KEY:
        issues.append("OPENAI_API_KEY is not set.")

    if AI_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
        issues.append("ANTHROPIC_API_KEY is not set.")

    if AI_PROVIDER == "gemini" and not GEMINI_API_KEY:
        issues.append("GEMINI_API_KEY is not set.")

    return issues
