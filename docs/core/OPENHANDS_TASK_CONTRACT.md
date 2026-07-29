# OPENHANDS_TASK_CONTRACT.md

# Autonomous AI Engineering Team
## OpenHands Integration Contract

Version: 1.0
Status: LOCKED

---

## 1. Task Request (AI Engineering Team -> OpenHands)
The JSON payload sent to OpenHands to execute a specific implementation task.

```json
{
  "task_id": "uuid-v4",
  "project_name": "saas-resume-analyzer",
  "workspace_dir": "/projects/saas-resume-analyzer",
  "task_instruction": "Implement POST /api/v1/auth/signup with email validation and password hashing.",
  "acceptance_criteria": [
    "Email validation exists",
    "Password hashed via bcrypt"
  ],
  "context": {
    "tech_stack": "fastapi",
    "architecture_notes": "Use dependency injection for the database session."
  },
  "max_retries": 3
}
```

## 2. Task Result (OpenHands -> AI Engineering Team)
The JSON payload returned by OpenHands upon task completion or failure.

```json
{
  "task_id": "uuid-v4",
  "status": "SUCCESS", // or "FAILED"
  "files_modified": [
    "backend/app/api/routes/auth.py",
    "backend/app/services/auth_service.py"
  ],
  "agent_trajectory_summary": "Created route handler, injected DB session, implemented bcrypt hashing.",
  "error_log": null,
  "exit_code": 0
}
```

## 3. Contract Rules
- OpenHands MUST NOT modify files outside `workspace_dir`.
- OpenHands MUST return a `TaskResult` adhering to this schema.
- If `exit_code != 0`, the AI Engineering Team will trigger a retry (up to `max_retries`).
