# ADR-004: Pluggable Post-Execution Validation Pipeline

## Status
Accepted

## Context
Code produced by AI providers may contain syntax errors, formatting inconsistencies, or failing unit tests. To guarantee repository stability and code quality, the Execution Engine must automatically run post-execution validation before marking a job as `COMPLETED`.

## Decision
We implemented a pluggable **Validation Pipeline**:
1. **`Validator` Interface:** Abstract base class defining `validate(workspace_path) -> list[ValidationResult]`.
2. **Standard Concrete Validators:**
   - `RuffValidator`: Runs static lint checks (`ruff check .`).
   - `RuffFormatValidator`: Checks code formatting (`ruff format --check .`).
   - `PytestValidator`: Executes unit test suite (`pytest`).
3. **`ValidationEngine`:** Orchestrates a sequence of pluggable validators and aggregates `ValidationResult` objects into the final `ExecutionReport`.

Validation runs automatically in `ExecutionEngine` post-adapter execution without modifying provider adapters or shell abstractions.

## Alternatives Considered
1. **Embedding Validation in Adapters:** Forcing each provider adapter to run linting/pytest internally. Rejected because validation logic would be duplicated across adapters and break separation of concerns.
2. **Manual Execution Validation:** Relying on human reviewers to manually run linters and test suites. Rejected to preserve automated execution engine autonomy.

## Consequences
### Positive:
- Pluggable validator architecture allows adding new linters/analyzers without changing engine or adapter code.
- Uniform `ValidationResult` reporting with exit codes, logs, and correlation IDs.
- Prevents broken AI-generated code from being marked as successful.

### Negative:
- Validation requires linter and test runner binaries to be installed in the runtime environment.
