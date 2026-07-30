# Engineering Bug Audit

## Issue 1: Mypy duplicate module error (Source file found twice under different module names: 'repository.generator' and 'execution.repository.generator')

- **Severity**: Medium
- **File**: `execution/repository/generator.py`
- **Line(s)**: All
- **Description**: Mypy duplicate module error (Source file found twice under different module names: 'repository.generator' and 'execution.repository.generator')
- **Root cause**: Missing `__init__.py` files in package directories (`execution`, `execution/adapters`, `models`, `core`, `app`, `cli`, `brain`, `brain/stages`, `providers`, `tests`).
- **Recommended fix**: Add empty `__init__.py` files to all package directories to explicitly define them as Python modules.
- **Confidence level**: High

## Issue 2: Missing type annotation for `tech_stack` variable.

- **Severity**: Low
- **File**: `execution/adapters/scaffold.py`
- **Line(s)**: 159
- **Description**: Missing type annotation for `tech_stack` variable.
- **Root cause**: mypy enforces strict type annotations but the `tech_stack` dictionary was initialized without one.
- **Recommended fix**: Add type annotation: `tech_stack: dict[str, str | None] = ...`
- **Confidence level**: High

## Issue 3: mypy error: 'ExecutionAdapter' has no attribute 'config'.

- **Severity**: Medium
- **File**: `execution/adapters/factory.py`
- **Line(s)**: 109
- **Description**: mypy error: 'ExecutionAdapter' has no attribute 'config'.
- **Root cause**: The `ExecutionAdapter` abstract base class does not define a `config` attribute, but `AdapterFactory` attempts to set it on instances.
- **Recommended fix**: Add a `config: AdapterConfiguration | None = None` attribute to the `ExecutionAdapter` base class.
- **Confidence level**: High

## Issue 4: Missing test/dev dependencies (pytest, mypy, ruff, pydantic, fastapi, openai) in pyproject.toml.

- **Severity**: Medium
- **File**: `pyproject.toml`
- **Line(s)**: 12-14
- **Description**: Missing test/dev dependencies (pytest, mypy, ruff, pydantic, fastapi, openai) in pyproject.toml.
- **Root cause**: Test and linting tools are not specified in the project dependencies or an optional dev group, requiring manual installation.
- **Recommended fix**: Add an `[project.optional-dependencies]` section with a `dev` group containing `pytest`, `mypy`, `ruff`, etc.
- **Confidence level**: High

## Issue 5: `PipelineEngine.from_registry()` is called, but no stages are explicitly registered.

- **Severity**: High
- **File**: `app/brain_service.py`
- **Line(s)**: 16, 22, 39
- **Description**: `PipelineEngine.from_registry()` is called, but no stages are explicitly registered.
- **Root cause**: The file doesn't import the stages package. Python won't execute stage registration code in `brain/stages/__init__.py` unless it's imported.
- **Recommended fix**: Import the stages module to trigger registration: `import brain.stages`
- **Confidence level**: High

## Issue 6: Missing runtime dependencies (fastapi, openai, pydantic) in pyproject.toml.

- **Severity**: Medium
- **File**: `pyproject.toml`
- **Line(s)**: 12-14
- **Description**: Missing runtime dependencies (fastapi, openai, pydantic) in pyproject.toml.
- **Root cause**: The project imports these libraries but they are not declared in `dependencies`.
- **Recommended fix**: Add `fastapi`, `openai`, and `pydantic` to the `dependencies` list.
- **Confidence level**: High

## Issue 7: Bandit B101: Use of assert detected.

- **Severity**: Low
- **File**: `tests/`
- **Line(s)**: Multiple
- **Description**: Bandit B101: Use of assert detected.
- **Root cause**: Bandit flags `assert` statements which are standard in pytest.
- **Recommended fix**: Ignore B101 for the `tests` directory in Bandit config.
- **Confidence level**: High
