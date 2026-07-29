# ADR-001: Layered Unidirectional Architecture

## Status
Accepted

## Context
The AI Engineering Team Execution Engine requires a clean, maintainable, and scalable architectural structure. As the system grew to support multiple AI coding providers, workspace isolation, and automated validation pipelines, a clear separation of concerns was necessary to prevent tight coupling, circular import dependencies, and leaky abstractions.

## Decision
We adopted a strict **Layered Unidirectional Architecture** organized as follows:
1. **Core Utilities (`core.*`):** Primitive abstractions, custom exceptions, logging, and HTTP clients.
2. **Domain Models (`models.*`):** Pure data contracts (`ExecutionTask`, `ExecutionContext`, `ExecutionJob`, `ExecutionReport`).
3. **Validation Pipeline (`execution/validation/*`):** Pluggable post-execution code validators (`RuffValidator`, `PytestValidator`).
4. **Provider Adapters (`execution/adapters/*`):** Provider-specific adapter implementations (`OpenHandsAdapter`, `ClaudeAdapter`).
5. **Execution Engine (`execution/engine.py`):** High-level orchestrator managing task lifecycle and workspace isolation.

### Dependency Flow:
`core` ← `models` ← `execution/validation` & `execution/adapters` ← `execution/engine`

Dependencies flow unidirectionally downwards. Higher-level layers may depend on lower-level layers, but lower-level layers must never import higher-level layers.

## Alternatives Considered
1. **Monolithic Single-Module Engine:** Placing engine orchestration, provider calls, and validation in a single package. Rejected due to high coupling and poor testability.
2. **Microservices Architecture:** Splitting components into separate HTTP microservices. Rejected as unnecessary overhead for local/embedded execution engine usage.

## Consequences
### Positive:
- Clear separation of concerns and component boundaries.
- Eliminates circular imports across core modules.
- Allows domain models and validators to be tested independently without instantiating the engine or providers.

### Negative:
- Developers must respect layer boundaries when adding new features (enforced automatically via `tests/test_architecture.py`).
