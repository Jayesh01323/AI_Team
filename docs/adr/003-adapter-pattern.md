# ADR-003: Provider Adapter Interface Pattern

## Status
Accepted

## Context
AI coding tools operate via disparate interface protocols (REST APIs, CLI tools, WebSocket streams) and have distinct configuration requirements, response payloads, and failure modes. The Execution Engine requires a standardized contract to interact with any AI provider transparently.

## Decision
We implemented the **Adapter Pattern** via an abstract base class `ExecutionAdapter` in `execution/adapters/base.py`.

### Adapter Lifecycle Contract:
1. `prepare(project_context, workspace_path)`: Prepares provider contract, workspace directory, and environment settings.
2. `execute(instruction, task)`: Dispatches prompt/instructions to the provider and returns `ExecutionResult`.
3. `collect_results()`: Gathers modified files, executed commands, and activity logs.
4. `health_check()`: Verifies authentication, configuration, workspace access, and provider readiness without executing tasks.
5. `cleanup()`: Releases workspace locks and temporary resources.

All provider-specific runtime errors are mapped into standardized exception types (`ProviderAuthenticationError`, `ProviderConfigurationError`, `ProviderRateLimitError`, `ProviderExecutionError`).

## Alternatives Considered
1. **Raw Provider SDK Calls in Engine:** Calling third-party APIs directly inside `ExecutionEngine`. Rejected due to extreme coupling and fragility.
2. **Generic Shell Script Invocation:** Interfacing with providers solely through shell command templates. Rejected because non-CLI providers (REST APIs) could not be supported cleanly.

## Consequences
### Positive:
- Standardized execution contract across all AI coding providers.
- Isolates provider API churn and schema differences within adapter implementations.
- Unified error hierarchy makes exception handling predictable for the engine.

### Negative:
- Each new AI provider requires writing a dedicated adapter implementing the contract.
