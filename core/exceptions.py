"""
Application-level exceptions.

All custom exceptions used across the codebase are defined here.
"""


class AIEngineeringTeamError(Exception):
    """Base exception for all application errors."""
    pass


class ConfigurationError(AIEngineeringTeamError):
    """Raised when required configuration is missing or invalid."""
    pass


class ProviderError(AIEngineeringTeamError):
    """Raised when an AI provider fails to generate a response."""
    pass


class ProviderNotImplementedError(ProviderError):
    """Raised when a provider is not yet implemented."""
    pass


class ProviderAuthenticationError(ProviderError):
    """Raised when provider API key is invalid or missing."""
    pass


class ProviderRateLimitError(ProviderError):
    """Raised when provider rate limit is exceeded."""
    pass


class ProjectError(AIEngineeringTeamError):
    """Raised when a project operation fails."""
    pass


class ProjectExistsError(ProjectError):
    """Raised when trying to create a project that already exists."""
    pass