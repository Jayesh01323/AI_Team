# ADR-006: Architecture Boundary Tests & Configurable Layer Rules

## Status
Accepted

## Context
As software systems evolve, architectural boundaries tend to erode over time. Developers adding features may accidentally introduce illegal imports (such as importing a concrete provider adapter inside `ExecutionEngine` or referencing adapters inside domain models), leading to tight coupling and circular import cycles.

## Decision
We implemented **Configurable Architecture Boundary Tests**:
1. **Configurable Rules (`architecture_rules.py`):** Centralized specification of architectural layer rules (`LayerRule`), defining allowed imports and forbidden imports per layer (`Models`, `Validation`, `Execution Engine`, `Provider Adapters`).
2. **Automated AST Testing (`tests/test_architecture.py`):** Uses Python's Abstract Syntax Tree (`ast`) module to inspect import statements across all source files dynamically.
3. **Automated Enforcement:** CI/test execution fails immediately if any module imports a forbidden dependency specified in `architecture_rules.py`.
4. **Circular Import Prevention:** Tests import all core modules in sequence to verify that zero import cycles exist.

## Alternatives Considered
1. **Manual Code Reviews:** Relying on human reviewers to spot invalid import statements. Rejected as error-prone and non-deterministic.
2. **External Third-Party Linter Plugins:** Using third-party tools like `import-linter`. Rejected to avoid unnecessary external project dependencies and keep the test suite self-contained with standard `pytest`.

## Consequences
### Positive:
- Automated, instant feedback on architectural boundary violations.
- Decouples test implementation from rule definitions, enabling new layers to be added via `architecture_rules.py` without changing test code.
- Guarantees provider agnosticism and layer independence in CI pipelines.

### Negative:
- Developers adding new architectural layers must define corresponding `LayerRule` entries in `architecture_rules.py`.
