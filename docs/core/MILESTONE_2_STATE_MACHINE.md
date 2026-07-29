# MILESTONE_2_STATE_MACHINE.md

# Autonomous AI Engineering Team
## Repository Lifecycle State Machine

Version: 1.0
Status: LOCKED

---

## State Flow

The following defines the lifecycle of a repository during Milestone 2 execution.

```text
[INIT]
  │
  ▼
[SCAFFOLDING] ──(Failure)──▶ [FAILED_SCAFFOLD]
  │
  ▼
[TEMPLATING] ──(Failure)──▶ [FAILED_TEMPLATES]
  │
  ▼
[DEPENDENCY_INSTALL] ──(Failure)──▶ [FAILED_DEPENDENCIES]
  │
  ▼
[OPENHANDS_EXECUTION] ──(Failure)──▶ [FAILED_EXECUTION]
  │
  ▼
[VALIDATING_BUILD] ──(Failure)──▶ [FAILED_BUILD]
  │
  ▼
[VALIDATING_TESTS] ──(Failure)──▶ [FAILED_TESTS]
  │
  ▼
[VALIDATING_LINT] ──(Failure)──▶ [FAILED_LINT]
  │
  ▼
[COMPLETED]
```

## State Definitions
- **INIT**: Received ProjectContext; preparing workspace.
- **SCAFFOLDING**: Generating folder structure, git initialization.
- **TEMPLATING**: Rendering baseline tech stack files (e.g., FastAPI, React).
- **DEPENDENCY_INSTALL**: Running package managers (`npm install`, `pip install`).
- **OPENHANDS_EXECUTION**: Agent writing custom code based on tasks.
- **VALIDATING_* **: Running quality gates.
- **COMPLETED**: The repository is fully generated and production-ready.
- **FAILED_* **: Error state; execution halts for human review.
