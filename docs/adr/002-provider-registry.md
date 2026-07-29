# ADR-002: Provider Registry & Dynamic Capability Validation

## Status
Accepted

## Context
The Execution Engine must support diverse AI coding providers (such as OpenHands, Claude, Codex, Devin, and Antigravity). Hardcoding provider class references or instantiation logic directly inside `ExecutionEngine` would break provider agnosticism, create tight coupling, and require modifying the engine whenever a new provider is added.

## Decision
We implemented a centralized `ProviderRegistry` and `AdapterFactory` mechanism:
1. **`ProviderRegistry`:** Maintains a thread-safe mapping of provider names to their corresponding `ExecutionAdapter` class and strongly typed `ProviderCapabilities`.
2. **Dynamic Registration:** Providers register capabilities (e.g. `SHELL`, `WORKSPACE`, `TESTS`) at application startup without modifying engine code.
3. **Pre-Execution Capability Validation:** `ProviderRegistry.validate_capabilities()` checks task `required_capabilities` against provider capabilities before execution, raising `ProviderCapabilityError` if unsupported.

## Alternatives Considered
1. **Direct Engine Imports:** Having `ExecutionEngine` import provider classes directly (`import OpenHandsAdapter`). Rejected because it violates provider agnosticism.
2. **Filesystem Plugin Scanner:** Auto-discovering adapters by scanning directories at runtime. Rejected due to security concerns and implicit loading magic.

## Consequences
### Positive:
- `ExecutionEngine` contains zero imports of concrete provider adapters.
- New AI providers can be added seamlessly by creating a class and registering it with `ProviderRegistry`.
- Invalid task capability demands are rejected cleanly before workspace preparation or task dispatch.

### Negative:
- Providers must be registered explicitly at application startup.
