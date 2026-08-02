## 2026-08-02 - Path Traversal bypass via `startswith` in Export Validator
**Vulnerability:** Path traversal detection logic in `ExportValidator.validate_export_safety` used `.startswith()` for directory comparison (`full_path.startswith(dest_norm)`), which allows bypassing restrictions if a directory shares a prefix with the destination directory (e.g. `destination_hacked`). Additionally, the `..` check incorrectly blocked valid filenames starting with `..`.
**Learning:** Checking directory bounds using string prefix matching (`.startswith()`) is vulnerable to prefix collision path traversal.
**Prevention:** Always use `os.path.commonpath([path1, path2]) == path2` or `Path.is_relative_to` when verifying if a resolved path remains inside a destination boundary.
