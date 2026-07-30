# Project Backlog

## Overview

**Milestone 3 (v0.3.0)** has been released, introducing the Execution Engine — a provider-agnostic task execution architecture with adapter framework, validation pipeline, structured logging, health checks, and capability validation. The release includes 124 passing tests, 7 registered providers (1 production, 6 scaffold), and comprehensive architecture enforcement.

This backlog captures **verified future improvements** identified through:

- **Post-release performance review** — Analysis of execution engine bottlenecks and resource usage
- **Milestone 3 Final Audit** — Comprehensive engineering audit covering architecture, code quality, testing, documentation, security, and maintainability
- **Release notes known limitations** — Documented constraints from v0.3.0
- **Current repository state** — Verified codebase analysis

Backlog items are **intentionally separated** from completed milestones to preserve release stability. No item in this backlog represents a regression or bug — all are optimizations, technical debt reductions, or enhancements.

---

## Priority Levels

### High

Items that directly impact execution performance, resource usage, or correctness of core workflows.

### Medium

Items that improve efficiency, reduce technical debt, or enhance developer experience without blocking core functionality.

### Low

Items that are desirable but depend on additional analysis, external factors, or future architectural changes.

---

## Backlog Items

---

### HIGH PRIORITY

---

#### PERF-001

**Title:** Optimize workspace creation

**Priority:** High

**Category:** Performance

**Status:** Backlog

**Description:**
Current workspace creation copies the entire source repository for every execution using `shutil.copytree()`. This is a blocking I/O operation that scales linearly with repository size.

**Background:**
Identified during post-release performance review and confirmed in the Milestone 3 Final Audit (Section 10 — Performance Review). The `WorkspaceManager.create_workspace()` method in `execution/workspace.py` (lines 26-49) iterates over all repository contents and copies each file/directory.

**Evidence:**
- `execution/workspace.py` line 26-49: `create_workspace()` uses `shutil.copytree()` for directories and `shutil.copy2()` for files
- Release notes v0.3.0, Known Limitations: "Workspace creation uses `shutil.copytree()` which copies the entire source repository. Large repositories may experience slower workspace preparation times."
- Audit Section 10: "Workspace creation uses `shutil.copytree()` which copies the entire repository. For large repositories, this could be slow."

**Expected Benefit:**
Reduced execution startup time and disk I/O. For large repositories, workspace preparation time could be reduced from seconds to milliseconds with lazy or symlink-based approaches.

**Suggested Milestone:** Milestone 4

---

#### PERF-002

**Title:** Reduce checkpoint overhead

**Priority:** High

**Category:** Performance

**Status:** Backlog

**Description:**
ProjectContext is serialized after every stage in the engineering pipeline. This repeated serialization of the full project context creates unnecessary overhead, especially as the context grows with each stage.

**Background:**
Identified during post-release performance review. The pipeline stages in `brain/stages/` serialize the project context after each stage execution, even when the context has not changed significantly.

**Evidence:**
- Pipeline stage execution pattern serializes `ProjectContext` after each stage
- `models/project_context.py` (142 lines) contains multiple nested dataclass structures that grow as stages add artifacts
- Audit Section 10: "No evidence of repeated file parsing" but notes serialization occurs after every stage

**Expected Benefit:**
Reduced execution time for multi-stage pipelines. Lazy or differential serialization could reduce overhead for stages that make minimal context changes.

**Suggested Milestone:** Milestone 4

---

### MEDIUM PRIORITY

---

#### PERF-003

**Title:** Avoid duplicate stage instantiation

**Priority:** Medium

**Category:** Performance

**Status:** Backlog

**Description:**
The stage registry in `pipeline/registry.py` instantiates a stage class to retrieve its name during registration. This creates unnecessary object allocations and may trigger side effects in stage constructors.

**Background:**
Identified during post-release performance review. The `register_stage()` function in `pipeline/registry.py` calls `stage_class()` to get the instance name, which constructs a full stage object just for metadata extraction.

**Evidence:**
- `pipeline/registry.py` line 20-21: `instance = stage_class()` then `_REGISTRY[instance.name] = stage_class`
- The comment on lines 14-18 acknowledges this: "We need an instance to get the name if it's a property, but since it's a class we'll just instantiate it once to get the name"
- Stage classes may have expensive `__init__` methods or side effects

**Expected Benefit:**
Reduced memory allocation during pipeline initialization. Stage metadata could be registered without constructing instances, using class-level attributes instead.

**Suggested Milestone:** Milestone 4

---

#### PERF-004

**Title:** Reuse provider client instances

**Priority:** Medium

**Category:** Performance

**Status:** Backlog

**Description:**
Provider client instances (e.g., OpenAI, Anthropic, Gemini clients) are created on every execution rather than being cached and reused. This causes repeated initialization overhead including network connection setup and authentication.

**Background:**
Identified during post-release performance review. The `AdapterFactory.get_adapter()` method in `execution/adapters/factory.py` creates a new adapter instance on every call without any caching mechanism.

**Evidence:**
- `execution/adapters/factory.py` line 105: `adapter = adapter_class()` — creates a new instance every time
- No caching or pooling mechanism exists in `AdapterFactory` or `ProviderRegistry`
- Each adapter initialization may set up configuration, validate settings, and prepare internal state

**Expected Benefit:**
Reduced execution overhead for repeated task executions. Client reuse could eliminate redundant initialization and connection setup.

**Suggested Milestone:** Milestone 4

---

#### PERF-005

**Title:** Improve provider retry strategy

**Priority:** Medium

**Category:** Performance

**Status:** Backlog

**Description:**
The current retry mechanism uses a fixed retry count with no exponential backoff, jitter, or circuit breaker pattern. Transient failures (rate limits, network timeouts) retry immediately, increasing load on already-stressed providers.

**Background:**
Identified during post-release performance review. The `AdapterConfiguration` dataclass in `models/execution.py` has a `retries` field defaulting to 3, but there is no backoff strategy implemented.

**Evidence:**
- `models/execution.py` line 156: `retries: int = 3` — hardcoded default with no backoff
- `execution/engine.py` line 94: `retries=context.configuration.get("retries", 3)` — passes retry count without strategy
- No exponential backoff, jitter, or circuit breaker pattern exists in the execution flow
- Audit Section 4: "Magic Numbers" finding for hardcoded `timeout=30.0` and `retries=3`

**Expected Benefit:**
Improved resilience to transient provider failures. Exponential backoff with jitter would reduce provider load during outages and improve overall execution success rates.

**Suggested Milestone:** Milestone 4

---

#### PERF-006

**Title:** Improve JSON serialization performance

**Priority:** Medium

**Category:** Performance

**Status:** Backlog

**Description:**
JSON serialization and deserialization uses the standard `json` module throughout the codebase. For large project contexts and contract files, this can become a bottleneck. Streaming writes or faster serializers (e.g., `orjson`) could improve throughput.

**Background:**
Identified during post-release performance review. Multiple modules perform JSON operations including contract generation, structured logging, and project context serialization.

**Evidence:**
- `execution/adapters/contract.py` uses `json.load()` and `json.dump()` for contract files
- `execution/adapters/logger.py` uses `json.dumps()` for structured log entries
- `brain/json_utils.py` uses standard `json` module for extraction
- No streaming writes are used; entire JSON payloads are loaded into memory

**Expected Benefit:**
Reduced serialization/deserialization time and memory usage for large payloads. Streaming writes would also reduce peak memory consumption.

**Suggested Milestone:** Milestone 4

---

#### PERF-007

**Title:** Reduce logging overhead

**Priority:** Medium

**Category:** Performance

**Status:** Backlog

**Description:**
Logging throughout the codebase uses eager f-string interpolation, which evaluates the string even when the log level would suppress the message. Lazy logging (passing a callable or using `%`-style formatting) would avoid this overhead.

**Background:**
Identified during post-release performance review. The `core/logging.py` module and `execution/adapters/logger.py` both use f-strings for log messages.

**Evidence:**
- `execution/engine.py` line 79: `job.logs.append(f"Workspace preparation failed: {e}")` — eager evaluation
- `execution/workspace.py` line 48: `logger.info(f"Created workspace at: {dest_path}")` — eager evaluation
- Multiple instances of f-string logging throughout `execution/engine.py`, `execution/workspace.py`, and adapter files
- Audit Section 10: "Logging Overhead: Low" — but notes this is a best-practice improvement

**Expected Benefit:**
Reduced CPU overhead for debug/trace level logging. Lazy interpolation would defer string formatting until the log level is confirmed active.

**Suggested Milestone:** Milestone 4

---

### LOW PRIORITY

---

#### PERF-008

**Title:** Reduce redundant filesystem operations

**Priority:** Low

**Category:** Performance

**Status:** Backlog

**Description:**
Multiple filesystem operations (directory existence checks, file reads, path resolutions) are performed redundantly across the execution lifecycle. These could be cached or batched.

**Background:**
Identified during post-release performance review. The execution engine, workspace manager, and adapters each perform independent filesystem checks.

**Evidence:**
- `execution/workspace.py` line 19-24: `verify_repository_exists()` checks path existence
- `execution/adapters/scaffold.py` line 64-67: `prepare()` checks `project_dir.exists()` again
- `execution/engine.py` line 74: `create_workspace()` is called, which internally verifies existence again
- Multiple redundant `Path.exists()` calls across the execution lifecycle

**Expected Benefit:**
Reduced filesystem I/O and improved execution startup time. Caching existence checks could eliminate redundant stat calls.

**Suggested Milestone:** Milestone 4

---

#### PERF-009

**Title:** Investigate pipeline parallelization

**Priority:** Low

**Category:** Performance

**Status:** Backlog

**Description:**
The validation pipeline runs validators sequentially. For large codebases, running Ruff linting, Ruff formatting, and Pytest in parallel could reduce total validation time.

**Background:**
Identified during post-release performance review. The `ValidationEngine` in `execution/validation/pipeline.py` iterates over validators in sequence.

**Evidence:**
- `execution/validation/pipeline.py` lines 149-163: `validate()` iterates `for validator in self.validators:` sequentially
- Each validator runs a subprocess that may take significant time for large codebases
- Audit Section 10: "Potential Bottlenecks" lists validation as a concern for large codebases

**Expected Benefit:**
Reduced validation time for large codebases. Parallel execution could reduce wall-clock time by up to 3x for independent validators.

**Note:** Dependency analysis required before implementation. Validators must be verified as independent before parallelization.

**Suggested Milestone:** Milestone 5

---

#### PERF-010

**Title:** Investigate memory optimization for very large project contexts

**Priority:** Low

**Category:** Performance

**Status:** Backlog

**Description:**
The `ProjectContext` model and related dataclasses hold all project data in memory. For very large projects with extensive requirements, architecture, and task plans, memory usage could become significant.

**Background:**
Identified during post-release performance review. The project context model grows as each pipeline stage adds artifacts.

**Evidence:**
- `models/project_context.py` (142 lines) contains nested dataclasses for requirements, architecture, task plans, and specifications
- `models/execution.py` (170 lines) contains 7 dataclasses and 2 enums
- Audit Section 2: "models/execution.py contains 7 dataclasses and 2 enums (170 lines). This is acceptable but could be split if it grows further."

**Expected Benefit:**
Reduced memory footprint for large projects. Streaming or lazy-loading strategies could keep memory usage bounded.

**Suggested Milestone:** Milestone 5

---

## Technical Debt

---

#### TECH-001

**Title:** Evaluate async provider execution

**Priority:** Medium

**Category:** Architecture

**Status:** Backlog

**Description:**
The current execution engine uses synchronous blocking calls for provider execution. Evaluating async execution would allow concurrent task processing and better resource utilization.

**Background:**
Identified during post-release architecture review. The `ExecutionAdapter.execute()` method is synchronous, and the engine blocks on each call.

**Evidence:**
- `execution/adapters/base.py` line 14: `def execute(self, instruction: str) -> ExecutionResult:` — synchronous signature
- `execution/engine.py` line 146: `adapter_result = adapter.execute(instruction)` — blocking call
- No async/await patterns exist in the execution layer

**Expected Benefit:**
Improved throughput for concurrent task execution. Async execution would enable non-blocking I/O and better resource utilization during provider calls.

**Suggested Milestone:** Milestone 5

---

#### TECH-002

**Title:** Investigate workspace caching

**Priority:** Medium

**Category:** Performance

**Status:** Backlog

**Description:**
Workspace creation copies the entire repository for every execution. A caching mechanism could skip copying when the source repository has not changed, using checksums or timestamps.

**Background:**
Identified during post-release architecture review. The `WorkspaceManager` has no caching logic.

**Evidence:**
- `execution/workspace.py` lines 26-49: `create_workspace()` always performs a full copy
- No cache invalidation or checksum comparison exists
- Audit Section 14 (Optional Improvements): "Add workspace caching — Skip copying if the source hasn't changed"

**Expected Benefit:**
Reduced execution startup time for repeated executions against the same repository. Cached workspaces could be reused in seconds instead of copying.

**Suggested Milestone:** Milestone 4

---

#### TECH-003

**Title:** Review artifact persistence strategy

**Priority:** Low

**Category:** Architecture

**Status:** Backlog

**Description:**
Execution artifacts (contracts, logs, validation results) are stored in workspace directories that are cleaned up after execution. A persistent artifact store would enable post-hoc analysis, debugging, and audit trails.

**Background:**
Identified during post-release architecture review. The current cleanup strategy removes all execution artifacts.

**Evidence:**
- `execution/engine.py` lines 193-199: `finally` block calls `adapter.cleanup()` and `self.workspace_manager.cleanup(workspace_path)`
- `execution/workspace.py` lines 51-59: `cleanup()` removes the entire workspace directory
- No persistent artifact storage exists outside the workspace lifecycle

**Expected Benefit:**
Improved debugging and audit capabilities. Persistent artifacts would allow post-mortem analysis of failed executions and provide an execution history.

**Suggested Milestone:** Milestone 5

---

#### TECH-004

**Title:** Benchmark execution engine performance

**Priority:** Medium

**Category:** Testing

**Status:** Backlog

**Description:**
There are no performance benchmarks for the execution engine. Key metrics (workspace creation time, adapter loading time, validation time, total execution time) are not tracked or regression-tested.

**Background:**
Identified during post-release performance review. The test suite (124 tests) covers correctness but not performance.

**Evidence:**
- No benchmark tests exist in the test suite
- `execution/engine.py` tracks `timing` in `ExecutionReport` but this is not used for regression testing
- Audit Section 10: Performance Review scores 8/10 but notes no performance benchmarks

**Expected Benefit:**
Performance regression protection. Benchmarks would alert developers to performance degradations before they reach production.

**Suggested Milestone:** Milestone 4

---

#### TECH-005

**Title:** Refactor OpenHandsAdapter to inherit from ProviderScaffoldAdapter

**Priority:** High

**Category:** Technical Debt

**Status:** Backlog

**Description:**
`OpenHandsAdapter` (228 lines) and `ProviderScaffoldAdapter` (207 lines) share approximately 80% identical code for lifecycle methods (`__init__`, `prepare`, `health_check`, `_convert_to_contract`, `load_contract`, `_log_provider_activity`, `collect_results`, `cleanup`). The only meaningful differences are `execute()` (real implementation vs. `ProviderNotImplementedError`) and `_validate_configuration()` (provider-specific error triggers).

**Background:**
Identified as the most critical finding in the Milestone 3 Final Audit (Section 4 — Code Quality). The duplication creates a maintenance liability where any bug fix or feature addition to shared lifecycle methods must be made in both files.

**Evidence:**
- Audit Section 4: "CRITICAL FINDING: OpenHandsAdapter (301 lines) and ProviderScaffoldAdapter (208 lines) share ~80% identical code"
- Audit Section 13 (Technical Debt Item 1): "Any bug fix or feature addition must be made in both files. High maintenance cost."
- `execution/adapters/openhands.py` duplicates `__init__`, `prepare`, `health_check`, `_convert_to_contract`, `load_contract`, `_log_provider_activity`, `collect_results`, `cleanup` from `execution/adapters/scaffold.py`
- The docstring in `openhands.py` (lines 1-6) states it inherits from `ProviderScaffoldAdapter`, but the actual code duplicates rather than inherits

**Expected Benefit:**
Eliminated code duplication, reduced maintenance burden, single source of truth for lifecycle methods. Estimated effort: 1-2 hours.

**Acceptance Criteria:**
- `OpenHandsAdapter` extends `ProviderScaffoldAdapter`
- Only `execute()` and `_validate_configuration()` are overridden
- All 124 existing tests pass
- No behavior changes in any lifecycle method
- Architecture tests continue to pass

**Suggested Milestone:** Milestone 4

---

#### TECH-006

**Title:** Remove dead code — `execution/repository/filesystem.py`

**Priority:** Medium

**Category:** Technical Debt

**Status:** Backlog

**Description:**
The file `execution/repository/filesystem.py` exists but is never imported anywhere in the codebase. It is dead code that adds to codebase size and may confuse developers.

**Background:**
Identified in the Milestone 3 Final Audit (Section 3 — Project Structure). The file was likely created as part of an incomplete repository abstraction.

**Evidence:**
- Audit Section 3: "execution/repository/ contains only filesystem.py which is never imported anywhere in the codebase. This is dead code."
- `grep` across the codebase shows zero imports of `execution.repository` or `execution.repository.filesystem`
- The `execution/repository/` directory contains only this single file

**Expected Benefit:**
Reduced codebase size, eliminated developer confusion. Estimated effort: 5 minutes to remove or 1 hour to implement and integrate.

**Acceptance Criteria:**
- File is removed (or implemented and integrated with tests)
- No imports reference the removed module
- All existing tests pass

**Suggested Milestone:** Milestone 4

---

#### TECH-007

**Title:** Remove pointless re-export — `models/execution_result.py`

**Priority:** Medium

**Category:** Technical Debt

**Status:** Backlog

**Description:**
The file `models/execution_result.py` is a 3-line re-export of `ExecutionResult` from `models/execution.py`. It adds no value and creates confusion about where `ExecutionResult` is defined.

**Background:**
Identified in the Milestone 3 Final Audit (Section 3 — Project Structure). The re-export module creates unnecessary indirection.

**Evidence:**
- Audit Section 3: "models/execution_result.py is a 3-line re-export of ExecutionResult from models/execution.py. It adds no value and creates confusion about where ExecutionResult is defined."
- The file contains only: `from models.execution import ExecutionResult` and a re-export
- All actual usage imports from `models.execution` directly

**Expected Benefit:**
Eliminated confusion about the canonical location of `ExecutionResult`. Estimated effort: 5 minutes.

**Acceptance Criteria:**
- File is removed
- No imports reference `models.execution_result`
- All existing tests pass

**Suggested Milestone:** Milestone 4

---

#### TECH-008

**Title:** Refactor long `execute()` method in `ExecutionEngine`

**Priority:** Medium

**Category:** Technical Debt

**Status:** Backlog

**Description:**
The `ExecutionEngine.execute()` method is 170 lines long (lines 42-218 in `execution/engine.py`). It handles input validation, workspace creation, adapter loading, capability validation, execution, result collection, validation dispatch, and report generation — violating the Single Responsibility Principle at the method level.

**Background:**
Identified in the Milestone 3 Final Audit (Section 2 — Architecture Review and Section 4 — Code Quality). The method is too long and handles too many responsibilities.

**Evidence:**
- Audit Section 2: "The execute() method is 170 lines long (lines 42-218). This is too long for a single method. It handles too many responsibilities."
- Audit Section 4: "ExecutionEngine.execute() (lines 42-218, 170 lines) handles: input validation, workspace creation, adapter loading, capability validation, execution, result collection, validation dispatch, report generation."
- The method has 5 distinct phases marked by comments: "Validate inputs", "Prepare workspace", "Initialize execution adapter & dispatch", "Collect results & validation", "Create ExecutionReport"

**Expected Benefit:**
Improved readability, testability, and maintainability. Smaller methods would be easier to unit test and modify independently. Estimated effort: 2-3 hours.

**Acceptance Criteria:**
- `execute()` is refactored into smaller methods (e.g., `_validate_inputs`, `_prepare_workspace`, `_load_adapter`, `_run_execution`, `_collect_results`, `_create_report`)
- Each extracted method has a single responsibility
- All 124 existing tests pass
- No behavior changes

**Suggested Milestone:** Milestone 4

---

#### TECH-009

**Title:** Simplify `ProviderCapabilities` bidirectional synchronization

**Priority:** Low

**Category:** Technical Debt

**Status:** Backlog

**Description:**
The `ProviderCapabilities.__post_init__` method synchronizes boolean flags and the `capabilities` set in both directions, creating two sources of truth. If a boolean flag and the `capabilities` set disagree, the behavior is undefined.

**Background:**
Identified in the Milestone 3 Final Audit (Section 3 — Project Structure and Section 4 — Code Quality). The bidirectional synchronization is complex and error-prone.

**Evidence:**
- `models/execution.py` lines 114-139: `__post_init__` first syncs booleans → set, then set → booleans
- Audit Section 3: "This creates two sources of truth. If a boolean flag is in the set, it sets the boolean flag to True. This creates two sources of truth."
- Audit Section 4: "Bidirectional synchronization in ProviderCapabilities.__post_init__" listed as a code smell
- No test exists for the `__post_init__` synchronization logic

**Expected Benefit:**
Simplified code with a single source of truth. Reduced risk of inconsistent state. Estimated effort: 1 hour.

**Acceptance Criteria:**
- Either boolean flags or the `capabilities` set is chosen as the single source of truth
- The other representation is derived, not stored independently
- All existing tests pass
- No behavior changes in capability validation

**Suggested Milestone:** Milestone 4

---

#### TECH-010

**Title:** Add `.env` support for API key management

**Priority:** Medium

**Category:** Developer Experience

**Status:** Backlog

**Description:**
API keys are loaded exclusively from environment variables. There is no `.env` file support, requiring developers to manually set environment variables for every terminal session.

**Background:**
Identified in the Milestone 3 Final Audit (Section 9 — Security Review). The `core/config.py` module uses `os.getenv()` for all configuration but never loads from a `.env` file.

**Evidence:**
- `core/config.py` lines 23-35: All API keys use `os.getenv()` with no `.env` loading
- Audit Section 9: "No `.env` file support, no key rotation, and no encryption at rest."
- Audit Section 13 (Technical Debt Item 7): "Poor developer experience. Developers must set environment variables manually."
- No `.env.example` file exists in the repository

**Expected Benefit:**
Improved developer experience. Developers can configure API keys once in a `.env` file rather than setting environment variables per session. Estimated effort: 30 minutes.

**Acceptance Criteria:**
- `python-dotenv` (or equivalent) is added as a dependency
- `.env` file is loaded at application startup in `core/config.py`
- Environment variables still take precedence over `.env` values
- `.env.example` template is created with documented variables
- `.env` is added to `.gitignore`
- All existing tests pass

**Suggested Milestone:** Milestone 4

---

#### TECH-011

**Title:** Create developer onboarding guide (CONTRIBUTING.md)

**Priority:** Medium

**Category:** Documentation

**Status:** Backlog

**Description:**
There is no developer onboarding guide or CONTRIBUTING.md. New developers must read ADRs and source code to understand how to set up the project, run tests, add providers, or contribute.

**Background:**
Identified in the Milestone 3 Final Audit (Section 8 — Documentation and Section 11 — Maintainability). The lack of onboarding documentation is a significant barrier to contribution.

**Evidence:**
- Audit Section 8: "No developer onboarding guide or CONTRIBUTING.md"
- Audit Section 8: "No explanation of how to add a new provider (though the code makes it obvious)"
- Audit Section 11: "No developer onboarding guide, no CONTRIBUTING.md, outdated README. A new developer would need to read ADRs and source code to understand the system."
- Audit Section 14 (Optional Improvements): "Add CONTRIBUTING.md — Guide for new developers on how to set up, run tests, add providers, etc."

**Expected Benefit:**
Lower barrier to entry for new contributors. A comprehensive CONTRIBUTING.md would reduce onboarding time from hours to minutes. Estimated effort: 1-2 hours.

**Acceptance Criteria:**
- `CONTRIBUTING.md` is created at repository root
- Document covers: project setup, running tests, adding a new provider, adding a new validator, code style guidelines, and PR process
- Document references relevant ADRs and documentation
- README is updated to link to CONTRIBUTING.md

**Suggested Milestone:** Milestone 4

---

#### TECH-012

**Title:** Add integration test for real validators

**Priority:** Medium

**Category:** Testing

**Status:** Backlog

**Description:**
The end-to-end tests mock `ValidationEngine`, so the real Ruff and Pytest validators are never exercised in an integration context. A regression in `RuffValidator`, `RuffFormatValidator`, or `PytestValidator` would not be caught by the current test suite.

**Background:**
Identified in the Milestone 3 Final Audit (Section 6 — Validation Pipeline and Section 7 — Testing). The validators are tested in isolation but not against actual files.

**Evidence:**
- Audit Section 6: "No integration test that exercises real validators against actual files"
- Audit Section 6: "The e2e tests mock ValidationEngine, so they don't actually test the validation pipeline integration"
- Audit Section 7: "The e2e tests mock ValidationEngine, so they don't actually test the validation pipeline integration. A regression in RuffValidator would not be caught by e2e tests."
- `test_validation_pipeline.py` tests code paths but not behavioral correctness against real files

**Expected Benefit:**
Improved regression protection for the validation pipeline. Real validator integration tests would catch regressions in external tool invocations. Estimated effort: 1-2 hours.

**Acceptance Criteria:**
- Integration test creates a temporary workspace with sample Python files
- Test runs `RuffValidator`, `RuffFormatValidator`, and `PytestValidator` against real files
- Test verifies correct behavior for both passing and failing validation scenarios
- Test is isolated (uses `tmp_path`) and does not depend on external network access
- All existing tests continue to pass

**Suggested Milestone:** Milestone 4

---

#### TECH-013

**Title:** Add pre-check for required CLI tools in validators

**Priority:** Low

**Category:** Reliability

**Status:** Backlog

**Description:**
The validation pipeline runs `ruff check .`, `ruff format --check .`, and `pytest .` via `subprocess.run()`. If these tools are not installed, the validators silently return failure results with no clear indication that the tool is missing.

**Background:**
Identified in the Milestone 3 Final Audit (Section 6 — Validation Pipeline). The validators catch exceptions but do not distinguish between "tool not found" and "validation failed".

**Evidence:**
- Audit Section 6: "If ruff or pytest are not installed, the validators will silently return failure results. There is no test that verifies the validators work correctly against actual Python files."
- Audit Section 6: "No pre-check for required CLI tools (ruff, pytest)"
- `execution/validation/pipeline.py` lines 54-61, 89-96, 124-131: All validators catch generic `Exception` and return `success=False` without distinguishing tool absence from validation failure

**Expected Benefit:**
Clearer error messages when required tools are missing. Developers would immediately know to install `ruff` or `pytest` rather than debugging silent validation failures. Estimated effort: 30 minutes.

**Acceptance Criteria:**
- Each validator checks for tool availability before running validation
- Missing tools produce a clear error message indicating the required installation command
- All existing tests pass

**Suggested Milestone:** Milestone 4

---

#### TECH-014

**Title:** Move `architecture_rules.py` to `docs/` or `tests/`

**Priority:** Low

**Category:** Project Structure

**Status:** Backlog

**Description:**
The `architecture_rules.py` file at the project root is a configuration file for architecture tests, not source code. It would be better placed in `docs/` or `tests/` to keep the project root clean.

**Background:**
Identified in the Milestone 3 Final Audit (Section 3 — Project Structure). The file is misplaced at the project root.

**Evidence:**
- Audit Section 3: "architecture_rules.py at the project root is a configuration file, not source code. It would be better placed in docs/ or tests/."
- The file defines layer rules and import specifications used by `test_architecture.py`
- It is not a runtime dependency of any production code

**Expected Benefit:**
Cleaner project root directory. Configuration files belong in documentation or test directories. Estimated effort: 5 minutes.

**Acceptance Criteria:**
- File is moved to `docs/architecture_rules.py` or `tests/architecture_rules.py`
- All imports referencing the old path are updated
- Architecture tests continue to pass
- README or documentation is updated if it references the file location

**Suggested Milestone:** Milestone 4

---

#### TECH-015

**Title:** Add provider name enum to replace hardcoded strings

**Priority:** Low

**Category:** Technical Debt

**Status:** Backlog

**Description:**
Provider names like "openhands", "claude", "codex" are hardcoded as strings throughout the codebase, particularly in `factory.py` registrations. This is error-prone and lacks IDE support for refactoring.

**Background:**
Identified in the Milestone 3 Final Audit (Section 4 — Code Quality). Hardcoded strings are a code smell that could be addressed with an enum.

**Evidence:**
- Audit Section 4: "Provider names like 'openhands', 'claude', 'codex' are hardcoded as strings in factory.py registrations (lines 115-186). This is acceptable but could use an enum."
- `execution/adapters/factory.py` lines 115-186: All 7 provider registrations use string literals
- Provider names are also used as string arguments in `AdapterFactory.get_adapter()` and `ProviderRegistry` methods

**Expected Benefit:**
Improved type safety and IDE support. An enum would prevent typos and enable automated refactoring. Estimated effort: 1 hour.

**Acceptance Criteria:**
- `ProviderName` enum is created with all 7 provider names
- All hardcoded string references are replaced with enum values
- String-based API is maintained for backward compatibility (or migration path documented)
- All existing tests pass

**Suggested Milestone:** Milestone 5

---

#### TECH-016

**Title:** Add configuration validation schema

**Priority:** Low

**Category:** Reliability

**Status:** Backlog

**Description:**
Configuration validation is done ad-hoc with manual checks in `AdapterFactory.get_adapter()` and individual adapter `_validate_configuration()` methods. There is no centralized schema or validation framework.

**Background:**
Identified during post-release architecture review. Configuration validation is scattered across multiple modules with inconsistent patterns.

**Evidence:**
- `execution/adapters/factory.py` lines 94-102: Manual validation of `timeout > 0` and `retries >= 0`
- `execution/adapters/openhands.py` lines 39-79: Provider-specific validation with manual error triggers
- `execution/adapters/scaffold.py` lines 146-154: Different validation pattern for scaffold adapters
- No shared validation schema or framework exists

**Expected Benefit:**
Consistent configuration validation across all providers. A schema-based approach would reduce boilerplate and ensure all configuration paths are validated. Estimated effort: 2-3 hours.

**Acceptance Criteria:**
- Configuration validation schema is defined (e.g., using Pydantic or a custom schema)
- All existing validation logic is migrated to use the schema
- Error messages are consistent across providers
- All existing tests pass

**Suggested Milestone:** Milestone 5

---

## Future Enhancements

The following items are intentionally deferred. They represent ideas that require additional research, external dependencies, or architectural changes before they can be scheduled.

---

#### FUTURE-001

**Title:** Implement remaining 6 provider execute() implementations

**Priority:** — (Future Consideration)

**Category:** Enhancement

**Status:** Future Consideration

**Description:**
Six of seven registered providers (Claude, Codex, Devin, Cursor, VS Code, Antigravity) raise `ProviderNotImplementedError` on `execute()`. Only OpenHands has a production implementation.

**Background:**
Documented in v0.3.0 release notes and Milestone 3 Final Audit. The scaffold adapters support all lifecycle operations except execution.

**Evidence:**
- Release notes v0.3.0, Known Limitations: "Only the OpenHands provider has a production execute() implementation."
- Audit Section 5: "6 of 7 providers are non-functional stubs"
- Each scaffold adapter (22-25 lines) raises `ProviderNotImplementedError` on `execute()`

**Expected Benefit:**
Full multi-provider code generation capability. Each provider implementation would unlock a different AI coding agent for task execution.

**Note:** Each provider requires its own API integration, authentication, and testing. Effort varies by provider complexity.

---

#### FUTURE-002

**Title:** Add provider discovery via entry points

**Priority:** — (Future Consideration)

**Category:** Architecture

**Status:** Future Consideration

**Description:**
Currently, all providers are imported and registered in `factory.py` at module load time. Python entry points would enable plugin-style provider discovery without modifying the factory.

**Background:**
Identified in the Milestone 3 Final Audit (Section 2 — Architecture Review and Section 14 — Optional Improvements).

**Evidence:**
- Audit Section 2: "execution/adapters/factory.py imports all 7 concrete adapters directly (lines 8-15). While this is necessary for registration, it creates a coupling point."
- Audit Section 14: "Provider discovery via entry points — Instead of importing all providers in factory.py, use Python entry points for plugin-style discovery"

**Expected Benefit:**
Decoupled provider registration. Third-party providers could be installed as separate packages without modifying the core codebase.

---

#### FUTURE-003

**Title:** Add metrics collection and monitoring

**Priority:** — (Future Consideration)

**Category:** Observability

**Status:** Future Consideration

**Description:**
There is no metrics collection for execution times, validation pass/fail rates, provider usage, or error rates. Adding metrics would enable data-driven optimization and capacity planning.

**Background:**
Identified in the Milestone 3 Final Audit (Section 14 — Optional Improvements).

**Evidence:**
- Audit Section 14: "Add metrics collection — Track execution times, validation pass/fail rates, provider usage"
- `ExecutionReport` captures timing data but it is not aggregated or exposed
- No monitoring infrastructure exists

**Expected Benefit:**
Data-driven performance optimization and capacity planning. Metrics would identify slow providers, frequent validation failures, and usage patterns.

---

#### FUTURE-004

**Title:** Add file change detection for workspace scanning

**Priority:** — (Future Consideration)

**Category:** Performance

**Status:** Future Consideration

**Description:**
`OpenHandsAdapter.execute()` scans all files in the workspace with `rglob("*")` and reports them as modified. This is potentially slow for large repositories and may report false positives.

**Background:**
Identified in the Milestone 3 Final Audit (Section 9 — Security Review and Section 10 — Performance Review).

**Evidence:**
- Audit Section 9: "OpenHandsAdapter.execute() scans all files in the workspace directory (lines 243-249) and reports them as modified. This assumes any file in the workspace was modified by the provider, which may not be true."
- Audit Section 10: "File scanning with rglob('*') could be slow for large repos"
- Audit Section 14: "Add file change detection — Instead of scanning all files with rglob('*'), track which files were actually modified"

**Expected Benefit:**
Accurate file modification reporting and reduced scanning time for large repositories.

---

#### FUTURE-005

**Title:** Add parallel validation execution

**Priority:** — (Future Consideration)

**Category:** Performance

**Status:** Future Consideration

**Description:**
The validation pipeline runs validators sequentially. For large codebases, running validators in parallel could reduce total validation time.

**Background:**
Related to PERF-009 but deferred for additional dependency analysis.

**Evidence:**
- `execution/validation/pipeline.py` lines 149-163: Sequential validator execution
- Audit Section 14: "Parallel validation — Run validators in parallel for large codebases"

**Expected Benefit:**
Reduced validation wall-clock time for large codebases.

---

#### FUTURE-006

**Title:** Add structured logging to `core/logging.py`

**Priority:** — (Future Consideration)

**Category:** Observability

**Status:** Future Consideration

**Description:**
Currently, only `execution/adapters/logger.py` has structured JSONL logging. The application-level logging in `core/logging.py` uses standard Python logging. Aligning these would provide consistent observability.

**Background:**
Identified in the Milestone 3 Final Audit (Section 2 — Architecture Review).

**Evidence:**
- Audit Section 2: "The relationship between these two systems is not documented. A developer might not know which to use."
- Audit Section 14: "Add structured logging to core/logging.py — Currently only execution/adapters/logger.py has structured logging"

**Expected Benefit:**
Consistent structured logging across the entire application. Unified log format would simplify log aggregation and analysis.

---

#### FUTURE-007

**Title:** Add pre-commit hooks for code quality

**Priority:** — (Future Consideration)

**Category:** Developer Experience

**Status:** Future Consideration

**Description:**
There are no pre-commit hooks configured. Adding hooks for Ruff linting, Ruff formatting, and architecture tests would catch issues before they reach CI.

**Background:**
Identified in the Milestone 3 Final Audit (Section 14 — Optional Improvements).

**Evidence:**
- Audit Section 14: "Add pre-commit hooks — Run ruff, pytest, and architecture tests before commits"
- No `.pre-commit-config.yaml` exists in the repository

**Expected Benefit:**
Faster feedback loop for developers. Issues are caught before commit rather than in CI.

---

## Summary Statistics

| Category | Count |
|----------|-------|
| High Priority | 3 |
| Medium Priority | 14 |
| Low Priority | 9 |
| Performance Items | 10 |
| Technical Debt Items | 16 |
| Future Considerations | 7 |
| **Total Backlog Items** | **26** |
| **Total Future Enhancements** | **7** |

---

*Backlog generated 2026-07-30. All items are evidence-based and verified against the current repository state. No items represent invented bugs or exaggerated impacts.*