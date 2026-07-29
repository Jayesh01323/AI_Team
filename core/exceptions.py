"""
Application-level exceptions.

All custom exceptions used across the codebase are defined here.
"""


class AIEngineeringTeamError(Exception):
    """Base exception for all application errors."""


class ConfigurationError(AIEngineeringTeamError):
    """Raised when required configuration is missing or invalid."""


class ProviderError(AIEngineeringTeamError):
    """Raised when an AI provider fails to generate a response."""


class ProviderNotImplementedError(ProviderError):
    """Raised when a provider is not yet implemented."""


class ProviderAuthenticationError(ProviderError):
    """Raised when provider API key is invalid or missing."""


class ProviderNotRegisteredError(ProviderError):
    """Raised when a provider is not registered in the registry."""


class ProviderConfigurationError(ProviderError):
    """Raised when adapter configuration is invalid or missing."""


class ProviderCapabilityError(ProviderError):
    """Raised when a provider lacks a required capability for a task."""


class ProviderRateLimitError(ProviderError):
    """Raised when provider rate limit is exceeded."""


class ProviderExecutionError(ProviderError):
    """Raised when unexpected runtime execution failures occur during provider execution."""


class ProjectError(AIEngineeringTeamError):
    """Raised when a project operation fails."""


class ProjectExistsError(ProjectError):
    """Raised when trying to create a project that already exists."""


class TemplateRenderError(AIEngineeringTeamError):
    """Raised when template rendering fails due to missing variables or invalid content."""
