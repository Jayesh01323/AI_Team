from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class ExecutionState(str, Enum):
    PENDING = "PENDING"
    PREPARING = "PREPARING"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ProviderCapability(str, Enum):
    STREAMING = "streaming"
    WORKSPACE = "workspace"
    RESUME = "resume"
    IMAGES = "images"
    SHELL = "shell"
    TESTS = "tests"


@dataclass
class ExecutionTask:
    id: str
    title: str
    description: str
    requirements: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    priority: str = "Medium"
    artifacts: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    required_capabilities: list[ProviderCapability | str] = field(default_factory=list)


@dataclass
class ExecutionContext:
    repository: str
    branch: str
    task: ExecutionTask
    provider: str
    configuration: dict[str, Any] = field(default_factory=dict)
    workspace: str | None = None
    execution_metadata: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None


@dataclass
class ExecutionResult:
    # Existing fields for backward compatibility
    task_id: str = ""
    status: str = "SUCCESS"
    files_modified: list[str] = field(default_factory=list)
    agent_trajectory_summary: str = ""
    error_log: str | None = None
    exit_code: int = 0

    # New fields for Milestone 3 & 6
    success: bool = True
    files_changed: list[str] = field(default_factory=list)
    added_files: list[str] = field(default_factory=list)
    modified_files: list[str] = field(default_factory=list)
    deleted_files: list[str] = field(default_factory=list)
    commands_executed: list[str] = field(default_factory=list)
    validation: str = "PENDING"
    metrics: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    correlation_id: str | None = None
    retries: int = 0
    recovery_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionJob:
    id: str
    task: ExecutionTask
    context: ExecutionContext
    status: ExecutionState = ExecutionState.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    retries: int = 0
    logs: list[str] = field(default_factory=list)
    adapter: str | None = None
    validation_status: str = "PENDING"
    result: ExecutionResult | None = None
    correlation_id: str | None = None


@dataclass
class ExecutionReport:
    job_id: str
    provider: str
    task_id: str
    status: str
    timing: float
    files_changed: list[str] = field(default_factory=list)
    added_files: list[str] = field(default_factory=list)
    modified_files: list[str] = field(default_factory=list)
    deleted_files: list[str] = field(default_factory=list)
    commands_executed: list[str] = field(default_factory=list)
    validation_status: str = "PENDING"
    errors: list[str] = field(default_factory=list)
    correlation_id: str | None = None
    retries: int = 0
    recovery_metadata: dict[str, Any] = field(default_factory=dict)




@dataclass
class ProviderCapabilities:
    provider_name: str
    capabilities: set[ProviderCapability] = field(default_factory=set)
    supports_streaming: bool = False
    supports_workspace: bool = True
    supports_resume: bool = False
    supports_images: bool = False
    supports_shell: bool = False
    supports_tests: bool = False
    max_context: int = 4096
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.supports_streaming:
            self.capabilities.add(ProviderCapability.STREAMING)
        if self.supports_workspace:
            self.capabilities.add(ProviderCapability.WORKSPACE)
        if self.supports_resume:
            self.capabilities.add(ProviderCapability.RESUME)
        if self.supports_images:
            self.capabilities.add(ProviderCapability.IMAGES)
        if self.supports_shell:
            self.capabilities.add(ProviderCapability.SHELL)
        if self.supports_tests:
            self.capabilities.add(ProviderCapability.TESTS)

        if ProviderCapability.STREAMING in self.capabilities:
            self.supports_streaming = True
        if ProviderCapability.WORKSPACE in self.capabilities:
            self.supports_workspace = True
        if ProviderCapability.RESUME in self.capabilities:
            self.supports_resume = True
        if ProviderCapability.IMAGES in self.capabilities:
            self.supports_images = True
        if ProviderCapability.SHELL in self.capabilities:
            self.supports_shell = True
        if ProviderCapability.TESTS in self.capabilities:
            self.supports_tests = True

    def has_capability(self, capability: ProviderCapability | str) -> bool:
        if isinstance(capability, ProviderCapability):
            return capability in self.capabilities
        try:
            enum_cap = ProviderCapability(capability.lower().strip())
            return enum_cap in self.capabilities
        except ValueError:
            return bool(self.metadata.get(capability.lower().strip()))


@dataclass
class AdapterConfiguration:
    provider_name: str
    model: str
    timeout: float = 30.0
    retries: int = 3
    environment: dict[str, str] = field(default_factory=dict)
    workspace_options: dict[str, Any] = field(default_factory=dict)
    provider_specific_settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheckResult:
    healthy: bool
    configuration_valid: bool = True
    authenticated: bool = True
    workspace_available: bool = True
    provider_ready: bool = True
    message: str = "Provider is healthy."
    errors: list[str] = field(default_factory=list)
