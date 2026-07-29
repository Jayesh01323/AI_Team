# 🚀 AI Engineering Team

**Autonomous AI Engineering Team CLI**

Transform a software idea into structured engineering artifacts through a modular AI pipeline, then execute code generation via a multi-provider execution engine.

## Overview

The AI Engineering Team is a CLI-first platform designed to act as an autonomous software engineering brain. It takes raw project ideas and runs them through a simulated engineering pipeline to generate comprehensive project documentation, system architectures, and task plans. Milestone 3 adds a production-ready **Execution Engine** that dispatches tasks to AI coding agents.

## Features

- **CLI-first architecture**: Easy to run and integrate.
- **AI Provider abstraction**: Supports OpenAI, Anthropic, and Gemini for the engineering brain.
- **Stage-based workflow**: Modular pipeline for idea analysis, requirements, PRD, architecture, and task planning.
- **Strongly typed domain models**: Ensures structured and reliable AI outputs.
- **Artifact Management**: Centralized management of generated artifacts in markdown and JSON.
- **Execution Engine**: End-to-end task lifecycle orchestration with workspace management and validation.
- **Multi-Provider Adapter Framework**: Pluggable adapters for OpenHands, Claude Code, OpenAI Codex, Devin, Cursor, VS Code Copilot, and Antigravity.
- **Validation Pipeline**: Post-execution code quality checks via Ruff and Pytest.
- **Structured Logging**: JSONL-based provider execution telemetry with correlation ID propagation.
- **Health Checks**: Pre-execution provider readiness verification.
- **Capability Validation**: Ensures providers support required task capabilities before execution.
- **Contract Schema**: Versioned task contracts for standardized provider communication.
- **Architecture Boundary Enforcement**: Automated AST-based tests verify layering rules.

## Architecture

The platform is built with a modular, extensible architecture:

```text
CLI
    │
Application Layer
    │
Pipeline Engine
    │
Stage Registry
    │
LLM Stage
    │
Prompt Templates
    │
Provider Factory
    │
AI Provider
    │
Generation Result
    │
Domain Models
    │
Artifact Manager
```

### Execution Engine Architecture (Milestone 3)

```text
ExecutionEngine
    │
    ├── WorkspaceManager ─── Isolated workspace per execution
    │
    ├── AdapterFactory ───── Provider-agnostic adapter loading
    │       │
    │       └── ProviderRegistry ─── Registered adapters + capabilities
    │
    ├── ExecutionAdapter ──── Abstract interface (prepare, execute, collect, cleanup)
    │       │
    │       ├── OpenHandsAdapter ─── Live implementation
    │       ├── ClaudeAdapter ────── Scaffold (ProviderNotImplementedError)
    │       ├── CodexAdapter ─────── Scaffold
    │       ├── DevinAdapter ─────── Scaffold
    │       ├── CursorAdapter ────── Scaffold
    │       ├── VSCodeAdapter ────── Scaffold
    │       └── AntigravityAdapter ─ Scaffold
    │
    └── ValidationEngine ─── Post-execution code quality checks
            │
            ├── RuffValidator ────── Linting
            ├── RuffFormatValidator ─ Format checking
            └── PytestValidator ──── Test execution
```

## Pipeline

The core engineering pipeline executes in the following sequence:

```text
Idea
    ↓
Idea Analyzer
    ↓
Requirements Generator
    ↓
PRD Generator
    ↓
Project Specification Generator
    ↓
Architecture Generator
    ↓
Task Planner
```

## Installation

Ensure you have Python 3.11+ installed.

1. Clone the repository.
2. Install the package locally:
   ```bash
   pip install -e .
   ```
3. Set your AI provider API key:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

## Quick Start

Initialize a new project idea:
```bash
ai-team init "A SaaS platform for analyzing resumes"
```

Run the full engineering pipeline:
```bash
ai-team pipeline "A SaaS platform for analyzing resumes"
```

## CLI Commands

- `ai-team init "<idea>"`: Initialize a new project with placeholder files.
- `ai-team analyze "<idea>"`: Analyze a project idea.
- `ai-team generate "<idea>"`: Generate structured requirements from an idea.
- `ai-team pipeline "<idea>"`: Run the full engineering pipeline.
- `ai-team scaffold "<idea>"`: Run the engineering pipeline and scaffold the physical repository.
- `ai-team test-provider`: Test the configured AI provider.

## Roadmap & Current Status

- **Milestone 1 (Engineering Brain)**: ✅ Complete
- **Milestone 2 (Repository Generator)**: ✅ Complete
- **Milestone 3 (Code Generation)**: ✅ Complete
  - Execution Engine with workspace management
  - Multi-provider adapter framework (7 providers)
  - Validation pipeline (Ruff, Pytest)
  - Structured logging with correlation IDs
  - Health checks and capability validation
  - Contract schema with versioning
  - Architecture boundary enforcement via AST tests
  - 124 automated tests (all passing)

## Release Notes

- [v0.1.0 Release Notes](docs/releases/v0.1.0.md)
- [CHANGELOG](CHANGELOG.md)

## License

MIT License