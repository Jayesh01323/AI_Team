## 2024-05-18 - Path Traversal bypass via startswith/commonpath
**Vulnerability:** Path validation using `os.path.commonpath` or `startswith` can be bypassed or cause unhandled exceptions when absolute paths or paths from different drives are provided.
**Learning:** Naive path string comparisons are insufficient for robust path traversal prevention.
**Prevention:** Always use `pathlib.Path.is_relative_to()` to securely check if a path is within an allowed root directory.
