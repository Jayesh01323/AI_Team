# ADR-005: Structured JSON Lines Logging & Correlation ID Propagation

## Status
Accepted

## Context
Debugging AI provider execution jobs across multiple layers requires structured log output. Plain text log files lack standard field schemas, making automated log ingestion, duration analysis, error tracing, and cross-layer correlation difficult.

## Decision
We implemented **Structured JSON Lines Logging** and **Correlation ID Propagation**:
1. **`ProviderStructuredLogger`:** Emits structured JSON Lines (`.jsonl`) files into `.ai/logs/<provider>.jsonl`.
2. **Standard Log Entry Schema:** Each JSON entry contains:
   - `timestamp` (ISO 8601 UTC)
   - `provider`
   - `model`
   - `task_id`
   - `execution_id`
   - `status` (`SUCCESS`, `FAILED`, `CANCELLED`)
   - `duration_ms`
   - `error` (nullable error string)
   - `correlation_id` (UUID string)
3. **End-to-End Correlation ID:** Auto-generated when `ExecutionJob` starts if missing, and propagated across `ExecutionContext`, `ExecutionJob`, `ExecutionAdapter`, plaintext activity logs (`[cid:<id>]`), structured JSON logs, `ValidationResult`, `ExecutionResult`, and `ExecutionReport`.

## Alternatives Considered
1. **Unstructured Plain Text Logs Only:** Writing raw stdout/stderr to disk. Rejected because logs could not be parsed reliably by log aggregators.
2. **Centralized Log Server Ingestion:** Sending logs directly to an external logging service (e.g. Datadog or ELK). Rejected to keep the engine self-contained without external networking requirements.

## Consequences
### Positive:
- Fully machine-parseable log entries saved as `.jsonl` files.
- End-to-end trace correlation across all stages and components using `correlation_id`.
- Preserves raw provider logs while supplying structured audit trails.

### Negative:
- Log writing logic must sanitize sensitive token data before persisting.
