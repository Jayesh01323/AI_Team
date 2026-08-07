## 2026-08-05 - [SEC-002: Path-Traversal Bug in `_validate_path`]
**Vulnerability:** Found a path traversal vulnerability in `brain/project_generator/export_validator.py`. The `startswith` method was used to validate if a path is inside another path, which can be bypassed if a sibling directory has the same prefix (e.g. `test` vs `test_workspace`).
**Learning:** `startswith` checks are not sufficient for path traversal checks. For strings like `/tmp/test_workspace`, it starts with `/tmp/test`.
**Prevention:** Use `os.path.commonpath([full_path, root]) == root` to strictly check if the path is a subdirectory.
