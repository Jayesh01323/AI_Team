## 2025-02-28 - [SEC-003 Symlink Copytree Risk]
**Vulnerability:** Symlink path traversal via `shutil.copytree(symlinks=True)` and `shutil.copy2` preserving and/or copying symlinks that point outside the repository.
**Learning:** In Python, standard library file duplication mechanisms like `shutil.copytree` or `shutil.copy2` can lead to path traversal vulnerabilities if malicious symlinks are placed inside the source directory. This is especially risky in environments duplicating untrusted files.
**Prevention:** Explicitly validate all symlinks using `is_symlink()` and ensure they resolve to a path within the intended bounds using `resolve().is_relative_to(base_dir.resolve())` before copying.
