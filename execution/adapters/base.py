from abc import ABC, abstractmethod
from pathlib import Path

from models.execution import ExecutionResult, HealthCheckResult
from models.project_context import ProjectContext


class ExecutionAdapter(ABC):
    @abstractmethod
    def prepare(self, context: ProjectContext, project_dir: Path) -> None:
        pass

    @abstractmethod
    def execute(self, instruction: str) -> ExecutionResult:
        pass

    @abstractmethod
    def collect_results(self) -> dict:
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass

    def health_check(self) -> HealthCheckResult:
        """Verify configuration, authentication, workspace availability, and provider readiness without executing task."""
        return HealthCheckResult(healthy=True)
