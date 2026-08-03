"""
Centralized configuration management.

All environment-variable loading happens here.
Providers and other modules read config from this module.

Secrets (API keys) are loaded from a local .env file (never committed to git)
OR from system environment variables. .env takes precedence for local dev.
"""

import os
from pathlib import Path

# ── Load .env file (local secrets, never committed) ────────────────────────
# Loads variables from .env into os.environ ONLY IF not already set,
# so system environment variables take precedence over .env values.
try:
    from dotenv import load_dotenv

    _ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(_ENV_PATH, override=False)
except ImportError:  # pragma: no cover - dotenv is a dependency
    pass

# ── Project Paths ──────────────────────────────────────────────────────────

ROOT_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"


# ── AI Provider Configuration ──────────────────────────────────────────────

# Which provider to use: "openai", "anthropic", "gemini", "nvidia", "auto"
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

# NVIDIA
NVIDIA_API_KEY: str | None = os.getenv("NVIDIA_API_KEY")
NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")


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

    if AI_PROVIDER not in ("openai", "anthropic", "gemini", "nvidia", "auto"):
        issues.append(
            f"AI_PROVIDER='{AI_PROVIDER}' is not supported. "
            f"Use 'openai', 'anthropic', 'gemini', 'nvidia', or 'auto'."
        )

    if AI_PROVIDER == "openai" and not OPENAI_API_KEY:
        issues.append("OPENAI_API_KEY is not set.")

    if AI_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
        issues.append("ANTHROPIC_API_KEY is not set.")

    if AI_PROVIDER == "gemini" and not GEMINI_API_KEY:
        issues.append("GEMINI_API_KEY is not set.")

    if AI_PROVIDER == "nvidia" and not NVIDIA_API_KEY:
        issues.append("NVIDIA_API_KEY is not set.")

    if AI_PROVIDER == "auto" and not GEMINI_API_KEY and not NVIDIA_API_KEY:
        issues.append("Neither GEMINI_API_KEY nor NVIDIA_API_KEY is set for auto mode.")

    return issues


