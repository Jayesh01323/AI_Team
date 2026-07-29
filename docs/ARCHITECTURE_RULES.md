# Architecture Rules & Dependency Boundaries Guide

This document is the authoritative architectural guide for the **AI Engineering Team Execution Engine**. It defines the layering model, allowed and forbidden dependencies between modules, justification for boundary rules, and how automated tests enforce compliance.

---

## 1. Overview & Core Philosophy

The Execution Engine architecture follows a strict, unidirectional dependency model. Core domain abstractions (`models`) and infrastructure interfaces (`core`) sit at the base of the dependency tree, while higher-level orchestrators (`ExecutionEngine`), validation pipelines (`ValidationEngine`), and provider adapters (`ExecutionAdapter`) operate in isolated layers.

### Key Principles:
1. **Provider Agnosticism:** `ExecutionEngine` orchestrates executions without depending directly on concrete AI providers (e.g. OpenHands, Claude, Codex, Devin, Antigravity). Concrete providers register via `ProviderRegistry`.
2. **Layer Independence:** Domain models (`models.*`) are pure data structures and must never depend on execution logic, adapters, or filesystem tools.
3. **Validator Isolation:** Post-execution validators (`execution/validation/*`) check generated code without depending on provider implementations or engine orchestration.
4. **Adapter Decoupling:** Provider adapters (`execution/adapters/*`) implement the standardized `ExecutionAdapter` interface without importing `ExecutionEngine`.

---

## 2. Layer Responsibilities & Dependency Rules

| Layer | Responsibility | Allowed Dependencies | Forbidden Dependencies |
| :--- | :--- | :--- | :--- |
| **Core Utilities (`core.*`)** | Custom exceptions, logging, common HTTP utilities. | Standard library | `models.*`, `execution.*` |
| **Domain Models (`models.*`)** | Pure data representations (e.g. `ExecutionTask`, `ExecutionContext`, `ExecutionJob`, `ExecutionReport`). | `core.*`, Standard library | `execution.adapters.*`, `execution.engine`, `execution.workspace`, `execution.validation` |
| **Validation (`execution/validation/*`)** | Post-execution code quality & test checks (Ruff, Pytest). | `core.*`, `models.*`, Standard library | `execution.adapters.*`, `execution.engine` |
| **Provider Adapters (`execution/adapters/*`)** | Provider-specific contract generation, logging, execution mapping. | `core.*`, `models.*`, `execution.adapters.base` | `execution.engine` |
| **Execution Engine (`execution/engine.py`)** | End-to-end task lifecycle orchestration, workspace management, validation dispatch. | `core.*`, `models.*`, `execution.workspace`, `execution.adapters.factory`, `execution.validation.pipeline` | `execution.adapters.openhands`, `execution.adapters.claude`, `execution.adapters.codex`, `execution.adapters.devin`, `execution.adapters.antigravity` |

---

## 3. Examples of Correct vs. Forbidden Imports

### A. Domain Models (`models/execution.py`)
- ✅ **CORRECT:**
  ```python
  from core.exceptions import ProviderError
  from dataclasses import dataclass, field
  ```
- ❌ **FORBIDDEN:**
  ```python
  from execution.adapters.openhands import OpenHandsAdapter  # Violates domain isolation
  from execution.engine import ExecutionEngine  # Violates layer separation
  ```

### B. Execution Engine (`execution/engine.py`)
- ✅ **CORRECT:**
  ```python
  from execution.adapters.factory import AdapterFactory, ProviderRegistry
  from execution.validation.pipeline import ValidationEngine
  ```
- ❌ **FORBIDDEN:**
  ```python
  from execution.adapters.openhands import OpenHandsAdapter  # Breaks provider agnosticism
  from execution.adapters.claude import (
      ClaudeAdapter,
  )  # Tight coupling to specific provider
  ```

### C. Provider Adapters (`execution/adapters/openhands.py`)
- ✅ **CORRECT:**
  ```python
  from execution.adapters.base import ExecutionAdapter
  from execution.adapters.contract import load_and_validate_contract
  from models.execution import AdapterConfiguration, ExecutionResult
  ```
- ❌ **FORBIDDEN:**
  ```python
  from execution.engine import ExecutionEngine  # Reverse dependency on engine
  ```

### D. Validation Pipeline (`execution/validation/pipeline.py`)
- ✅ **CORRECT:**
  ```python
  from pathlib import Path
  from dataclasses import dataclass
  ```
- ❌ **FORBIDDEN:**
  ```python
  from execution.adapters.openhands import (
      OpenHandsAdapter,
  )  # Validator coupled to adapter
  from execution.engine import ExecutionEngine  # Validator coupled to orchestrator
  ```

---

## 4. Why These Rules Exist

- **Maintainability:** Preventing reverse or cross-layer dependencies allows developers to modify a provider adapter or validator without breaking the core engine or models.
- **Extensibility:** New AI coding providers (e.g. Claude, Devin, OpenHands) can be added simply by subclassing `ExecutionAdapter` and registering with `ProviderRegistry` without modifying `ExecutionEngine`.
- **Testability:** Components can be tested in complete isolation using unit test doubles without bootstrapping the entire engine or real API providers.
- **Circular Import Elimination:** Enforcing a strict DAG (Directed Acyclic Graph) of imports prevents runtime `ImportError` cycles.

---

## 5. Automated Architectural Enforcement

Architectural rules are defined in [`architecture_rules.py`](file:///c:/Users/Jayesh/OneDrive/Desktop/AI-Engineering-Team/architecture_rules.py) and automatically enforced by unit tests in [`tests/test_architecture.py`](file:///c:/Users/Jayesh/OneDrive/Desktop/AI-Engineering-Team/tests/test_architecture.py).

### How Tests Enforce Rules:
1. **AST Parsing:** `tests/test_architecture.py` parses Python source code files into Abstract Syntax Trees (AST).
2. **Rule Inspection:** Iterates through `ARCHITECTURE_RULES` to extract all `import` and `from ... import ...` statements.
3. **Violation Failure:** The test suite immediately fails if any module imports a forbidden dependency specified in `architecture_rules.py`.
4. **Circular Import Verification:** Validates that importing all system modules completes cleanly without import cycles.
