# MILESTONE_2_API.md

# Autonomous AI Engineering Team
## Milestone 2 API Contracts

Version: 1.0
Status: LOCKED

---

## 1. Repository Generator
```python
class RepositoryGenerator:
    """Orchestrates the creation of the repository."""

    def generate(self, context: ProjectContext) -> GenerationReport:
        """Executes scaffolding, templating, and validation."""
        pass
```

## 2. Project Scaffolder
```python
class ProjectScaffolder:
    """Handles physical file system and git setup."""

    def create(self, context: ProjectContext, output_dir: str) -> None:
        """Initializes directories, .gitignore, and runs git init."""
        pass
```

## 3. Template Engine
```python
class TemplateEngine:
    """Renders parameterized baseline code."""

    def render(
        self, template_name: str, version: str, variables: dict, output_dir: str
    ) -> None:
        """Renders the specified template into the output directory."""
        pass
```

## 4. OpenHands Interface
```python
class OpenHandsInterface:
    """Boundary for autonomous code execution."""

    def execute_task(self, task_payload: dict) -> dict:
        """Sends the JSON Task Request and returns the JSON Task Result."""
        pass
```

## 5. Validation Workflow
```python
class ValidationWorkflow:
    """Orchestrates the sequential quality gates."""

    def validate(self, workspace_dir: str, tech_stack: dict) -> ValidationStep:
        """Runs install, build, test, and lint steps."""
        pass


class RepositoryValidator:
    """Performs static checks on the generated repository."""

    def validate(self, workspace_dir: str) -> bool:
        """Ensures required files exist (e.g. README, .env)."""
        pass
```
