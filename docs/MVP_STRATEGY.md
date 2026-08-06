# MVP Strategy - 30-Day Execution Plan

Version: 2.0
Status: ACTIVE
Date: 2026-07-26

---

# Executive Summary

**Objective**: Deliver a usable MVP in 20-30 days that the founder can personally use to build real software projects.

**Success Criteria**: Founder provides an idea (e.g., "Build a SaaS resume analyzer") → Platform produces requirements, PRD, architecture, tech stack, folder structure, task breakdown, repository, initial production-ready code, and a runnable local project.

**Core Principle**: Build only competitive advantage. Reuse mature OSS. Defer everything else.

**Key Strategy Changes (v2.0)**:
- **Milestone-based progress**: Every week ends with a working, testable capability — not a list of completed tasks.
- **CLI-first approach**: Start with a command-line interface and Engineering Brain skeleton. No web dashboard until Week 4, and only if strictly required.
- **OpenHands as uncertain dependency**: Research and prototype in parallel rather than assuming two-day integration.
- **No scope increase**: Deadline remains 20-30 days. Long-term architecture (MASTER_SPEC.md, ARCHITECTURE.md) is preserved.

---

# Feature Classification

## Build Now (Competitive Advantage)

### Engineering Brain
- Idea Analyzer
- Requirement Generator
- PRD Generator
- Architecture Generator
- Tech Stack Selector
- Task Planner

### Product Workflow
- Idea → Requirements → PRD → Architecture → Planning → Implementation
- State machine for project lifecycle
- Approval gates (configurable)

### CLI Interface
- Project creation via command line
- Idea input via stdin/argument/file
- Progress output to terminal
- Results saved to disk

### Integration Layer
- LangGraph integration
- AI provider abstraction (OpenAI, Claude, etc.)
- OpenHands research & prototype (parallel track)

### Project Orchestration
- Task coordination
- Agent routing
- Error handling
- Retry logic

### Project DNA
- Project memory storage
- Engineering decision tracking
- Context preservation

### Quality Workflow
- Basic validation (build, tests pass)
- Documentation generation

## Reuse Existing OSS

### OpenHands (Research Track — see Risk 1)
- Code generation
- File operations
- Repository creation
- Dependency installation
- Build execution
- Test execution

### LangGraph
- Workflow orchestration
- State management
- Agent coordination


- Engineering role definitions
- Agent communication patterns

### Infrastructure
- Python CLI framework (Click/Typer)
- FastAPI (backend, deferred to Week 4 if dashboard needed)
- React + TypeScript (frontend, deferred to Week 4 if dashboard needed)
- PostgreSQL or SQLite (database, start with file-based)
- Docker (containerization, Week 4)

## Defer to Future (Post-MVP)

### Web Dashboard
- Project creation interface
- Idea input
- Progress tracking
- Output viewing
- Workflow viewer
- Agent monitor
- Task board
- Logs viewer
- Approval center
- Settings

### Advanced Memory
- Knowledge graph
- Long-term memory
- Version history
- Complex context retrieval

### Advanced Agents
- Specialized QA Engineer
- Security Engineer
- Performance Engineer
- DevOps Engineer (beyond basic deployment)

### Advanced Validation
- Security scanning
- Performance profiling
- Architecture validation
- Lint/type checking (basic only in MVP)

### Advanced Integrations
- GitHub integration
- GitLab integration
- Multiple AI providers (start with one)
- Local models

### Project Management
- Milestones
- Sprint tracking
- Progress analytics

## Remove (Out of Scope for MVP)

### Phase 5-8 Features
- Self-healing engineering
- Continuous engineering
- Enterprise platform
- AI company operating system

### Non-Essential Agents
- Multiple specialized engineers (use general-purpose engineers)
- Complex agent hierarchies

### Advanced Features
- Multi-project management
- Team collaboration
- Enterprise authentication
- Advanced monitoring

---

# 30-Day Roadmap — Milestone Based

Every week ends with a **working, testable capability** that can be demonstrated and validated. Milestones are cumulative — each builds on the last.

---

## Week 1: CLI + Engineering Brain Skeleton (Days 1-7)

### Milestone
A CLI tool that accepts an idea and produces requirements, PRD, and architecture documents saved to disk. No web UI. No database dependency. The Engineering Brain runs as a standalone Python module.

### Working Capability at End of Week 1
```
$ ai-team init "Build a SaaS resume analyzer"
→ Generates: requirements.md, prd.md, architecture.md, tech-stack.json
→ All outputs saved to ./projects/<name>/
```

### Daily Plan

**Day 1: CLI Skeleton + Project Structure**
- Initialize Git repository
- Create minimal folder structure (brain/, cli/, projects/, docs/)
- Set up Python CLI framework (Click/Typer)
- Implement `ai-team init <idea>` command skeleton
- Create Engineering Brain module skeleton
- No FastAPI. No React. No database.
- **Validation**: `ai-team --help` works, `ai-team init "test"` creates a project folder

**Day 2: AI Provider Layer**
- Implement OpenAI integration
- Implement Claude integration (fallback)
- Create AI provider abstraction
- Add API key configuration via environment variables
- Test basic LLM calls from CLI
- **Validation**: CLI can send a prompt to LLM and print response

**Day 3: Idea Analyzer**
- Build idea parsing module
- Implement requirement extraction
- Create clarification engine
- Add basic validation
- Test with sample ideas via CLI
- **Validation**: `ai-team analyze "Build a SaaS resume analyzer"` outputs structured requirements

**Day 4: Requirement Generator**
- Build requirement generation module
- Implement functional requirements extraction
- Implement non-functional requirements
- Add requirement prioritization
- Integrate with CLI output
- **Validation**: Full requirements document generated and saved to project folder

**Day 5: PRD Generator**
- Build PRD generation module
- Implement user story generation
- Implement acceptance criteria
- Add feature breakdown
- Integrate with CLI pipeline
- **Validation**: PRD document generated with user stories and acceptance criteria

**Day 6: Architecture Generator**
- Build architecture generation module
- Implement system design
- Implement component breakdown
- Add technology recommendations
- **Validation**: Architecture document with system design and component breakdown

**Day 7: Tech Stack Selector + Pipeline Integration**
- Build tech stack selector
- Implement decision logic
- Add dependency recommendations
- Wire up end-to-end CLI pipeline: Idea → Requirements → PRD → Architecture → Tech Stack
- **Validation**: `ai-team init "Build a SaaS resume analyzer"` produces all four documents

### Week 1 Success Criteria (Milestone)
- [x] CLI tool exists and is runnable
- [x] Input: "Build a SaaS resume analyzer"
- [x] Output: requirements.md, prd.md, architecture.md, tech-stack.json
- [x] All outputs saved to project folder on disk
- [x] No web dashboard, no database, no Docker required

---

## Week 2: Planning Engine + Project DNA + OpenHands Research (Days 8-14)

### Milestone
The CLI can now plan the full implementation (tasks, dependencies, folder structure) and store all engineering decisions in Project DNA. OpenHands integration is researched and prototyped in parallel — if it works, it's adopted; if not, a fallback execution path is defined.

### Working Capability at End of Week 2
```
$ ai-team plan "Build a SaaS resume analyzer"
→ Generates: task-plan.json, folder-structure.yaml, project-dna/
$ ai-team research openhands --report
→ Outputs: integration-report.md (feasibility, risks, prototype results)
```

### Daily Plan

**Day 8: Task Planner**
- Build task planning module
- Implement task breakdown
- Add dependency tracking
- Create task prioritization
- Integrate with CLI: `ai-team plan <project>`
- **Validation**: Task plan with dependencies and priorities generated

**Day 9: Project DNA System**
- Build Project DNA storage (file-based, JSON/YAML)
- Implement decision tracking
- Add context preservation
- Create retrieval mechanism
- Integrate with CLI pipeline
- **Validation**: Engineering decisions are stored and retrievable

**Day 10: Workflow Engine (Simplified)**
- Implement basic state machine
- Create workflow orchestration
- Add stage transitions
- Implement approval gates (manual for MVP)
- Integrate with CLI
- **Validation**: Workflow progresses through stages with state persistence

**Day 11: OpenHands Research Sprint (Parallel Track A)**
- Research OpenHands SDK and API capabilities
- Set up OpenHands sandbox/test environment
- Test basic operations: file creation, repo init
- Document findings, risks, limitations
- **Validation**: Research report with working/not-working assessment

**Day 12: OpenHands Prototype (Parallel Track A) + Fallback Planning (Track B)**
- If OpenHands viable: Build prototype integration
- If OpenHands not viable: Define fallback execution strategy
  - Template-based code generation
  - Direct file system operations
  - Shell command execution
- **Validation**: Clear go/no-go decision on OpenHands with documented fallback

**Day 13: Folder Structure Generator + Repository Setup**
- Build folder structure generator from architecture
- Implement repository initialization
- Add .gitignore generation
- Add README generation
- **Validation**: Complete folder structure and repo skeleton generated

**Day 14: End-to-End Planning Pipeline**
- Connect all Week 1 + Week 2 components
- Test full workflow: Idea → Requirements → PRD → Architecture → Planning → Folder Structure
- Fix integration issues
- Document CLI commands and API contracts
- **Validation**: Complete end-to-end planning pipeline works via CLI

### Week 2 Success Criteria (Milestone)
- [x] CLI can produce complete project plan with tasks and folder structure
- [x] Project DNA stores all engineering decisions
- [x] OpenHands research complete with go/no-go decision
- [x] Fallback execution path defined if OpenHands is not viable
- [x] No web dashboard — everything works via CLI

---

## Week 3: Execution & Validation (Days 15-21)

### Milestone
The system generates working code, installs dependencies, runs builds, and validates output. Execution uses either OpenHands (if viable) or the fallback mechanism. The result is a runnable project on disk.

### Working Capability at End of Week 3
```
$ ai-team build "Build a SaaS resume analyzer"
→ Generates: complete project in ./projects/resume-analyzer/
→ Backend code, frontend code, tests, documentation
→ Project builds successfully, tests pass
```

### Daily Plan

**Day 15: Code Generator — Backend (Template-Based)**
- Implement backend code generation using templates
- Generate API routes, models, database schema
- Support Python/FastAPI as default stack
- **Validation**: Backend code generated and structurally valid

**Day 16: Code Generator — Frontend (Template-Based)**
- Implement frontend code generation using templates
- Generate React components, TypeScript types, basic routing
- **Validation**: Frontend code generated and structurally valid

**Day 17: Dependency Installer**
- Implement requirements.txt generation
- Implement package.json generation
- Add dependency installation logic
- Handle installation errors gracefully
- **Validation**: Dependencies install successfully

**Day 18: Build Runner**
- Implement build execution
- Add error handling and output capture
- Implement retry logic for transient failures
- **Validation**: Project builds successfully

**Day 19: Test Generator**
- Implement basic test generation
- Generate unit tests for backend
- Generate unit tests for frontend
- **Validation**: Tests are generated and executable

**Day 20: Quality Validation**
- Implement build validation gate
- Implement test validation gate
- Add basic documentation check
- **Validation**: Quality gates pass for generated project

**Day 21: End-to-End Execution Pipeline**
- Connect all components
- Test full workflow: Idea → Working Project
- Fix integration issues
- Test with 2 different project ideas
- **Validation**: Complete project generated, builds, and tests pass

### Week 3 Success Criteria (Milestone)
- [x] Input: "Build a SaaS resume analyzer"
- [x] Output: Complete repository with backend, frontend, tests, documentation
- [x] Project builds successfully
- [x] Tests pass
- [x] All operations work via CLI

---

## Week 4: Polish, Web Dashboard (If Required) & Deployment (Days 22-28)

### Milestone
The MVP is polished, documented, and deployable. A minimal web dashboard is added **only if the CLI alone is insufficient** for the founder's workflow. The product is ready for real use.

### Working Capability at End of Week 4
```
# CLI path (always works)
$ ai-team full "Build a SaaS resume analyzer"
→ Complete project generated and validated

# Web dashboard (only if required)
$ ai-team dashboard --start
→ Opens browser at localhost:3000
→ Project creation, progress tracking, output viewing
```

### Daily Plan

**Day 22: Error Handling & Resilience**
- Improve error recovery across all modules
- Add retry logic with exponential backoff
- Implement graceful degradation
- Add error logging to files
- **Validation**: Error scenarios handled gracefully

**Day 23: CLI Polish**
- Improve CLI output formatting
- Add progress indicators (spinner/progress bar)
- Implement colored output for success/error states
- Add `--help` documentation for all commands
- **Validation**: CLI is user-friendly and self-documenting

**Day 24: Web Dashboard (Conditional)**
- **Only if CLI is insufficient** for founder's workflow
- Build minimal FastAPI backend (single endpoint)
- Build minimal React frontend (single page)
- Project creation form, progress display, output viewer
- **If not needed**: Skip and use this day for additional testing/polish
- **Validation**: Dashboard can create projects and show outputs

**Day 25: Docker Setup**
- Create Dockerfile for the application
- Create docker-compose.yml
- Test local deployment
- Document deployment steps
- **Validation**: Application runs in Docker

**Day 26: Documentation**
- Write user guide (CLI commands, examples)
- Document API (if dashboard was built)
- Add troubleshooting guide
- Update README
- **Validation**: Documentation is complete and accurate

**Day 27: End-to-End Testing**
- Test with 3 different project ideas
- Fix bugs found during testing
- Validate all outputs
- Stress test with edge cases
- **Validation**: All 3 project types succeed end-to-end

**Day 28: MVP Release Preparation**
- Final polish
- Create release notes
- Prepare demo script
- Document known issues and limitations
- **MVP Complete**

### Week 4 Success Criteria (Milestone)
- [x] Product works end-to-end for multiple project types
- [x] CLI is polished and user-friendly
- [x] Web dashboard exists only if strictly required
- [x] Product is deployable via Docker
- [x] Documentation is complete
- [x] Founder can use it to build real projects

---

# Milestone Summary

| Week | Milestone | Working Capability |
|------|-----------|-------------------|
| 1 | CLI + Engineering Brain Skeleton | `ai-team init "idea"` → requirements, PRD, architecture |
| 2 | Planning Engine + OpenHands Research | `ai-team plan` → tasks, folder structure, Project DNA |
| 3 | Execution & Validation | `ai-team build` → working project with tests |
| 4 | Polish & Conditional Dashboard | `ai-team full` → production-ready, deployable project |

---

# OpenHands Integration Strategy

## Problem
The original plan assumed OpenHands could be integrated in 2 days (Days 11-12). This is an **uncertain dependency** — OpenHands may have API limitations, compatibility issues, or require significant adaptation.

## Strategy: Parallel Research Track

### Track A: OpenHands Research & Prototype (Days 11-12)
- Dedicated research sprint at the start of Week 2
- Test OpenHands SDK capabilities against real requirements
- Document limitations, bugs, and integration complexity
- Build a minimal prototype to validate the approach

### Decision Point (End of Day 12)
- **Go**: OpenHands works for our use case → Integrate as execution engine
- **No-Go**: OpenHands is not viable → Use fallback execution path

### Track B: Fallback Execution Path
- Template-based code generation (Handlebars/Jinja2)
- Direct file system operations (os, shutil)
- Shell command execution (subprocess)
- This path is always available and does not block the timeline

### Risk Mitigation
- Both tracks are developed in parallel during Week 2
- The fallback path is simpler and guaranteed to work
- OpenHands can be added post-MVP if not ready in time
- No timeline dependency on OpenHands integration

---

# Risks and Mitigation

## Risk 1: OpenHands Integration Complexity
**Probability**: High
**Impact**: High
**Mitigation**:
- Parallel research track (Days 11-12) before committing
- Clear go/no-go decision point
- Fallback execution path always available
- OpenHands can be deferred to post-MVP
- **No timeline dependency on OpenHands**

## Risk 2: LLM API Costs
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Use efficient prompting
- Cache responses where possible
- Start with one provider (OpenAI)
- Monitor costs daily
- Set usage limits

## Risk 3: Code Generation Quality
**Probability**: High
**Impact**: High
**Mitigation**:
- Use templates for common patterns
- Implement validation
- Allow manual editing
- Focus on MVP-quality code, not production-perfect
- Iterate based on testing

## Risk 4: Timeline Slippage
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Milestone-based tracking (not task-based)
- Cut non-essential features immediately
- Web dashboard is conditional — skip if not needed
- Reuse more OSS if needed
- Extend to Day 30 if necessary

## Risk 5: Integration Issues
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Test integrations early
- Have clear API contracts
- Implement error handling
- Use integration tests

## Risk 6: Scope Creep
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Strict feature classification
- Founder approval for any new features
- Milestone review against MVP criteria
- Defer everything not essential

---

# Architecture Compliance

This plan maintains the core architecture from ARCHITECTURE.md while simplifying for MVP:

**Preserved**:
- Layered architecture (Brain → Workflow → Execution)
- Engineering Brain responsibilities (idea analysis, requirements, PRD, architecture, planning)
- Workflow orchestration (state machine, stage transitions)
- Project DNA concept (decision tracking, context preservation)
- Quality gates (simplified: build + tests)
- LangGraph integration path (workflow engine)


**Simplified for MVP**:
- CLI-first instead of web-first (dashboard deferred)
- Single agent type (general-purpose engineer)
- Basic memory (file-based, no knowledge graph)
- Manual approval gates
- Basic validation only (build + tests)
- Template-based code generation (with OpenHands as optional upgrade)

**Deferred**:
- Web dashboard (Week 4, conditional)
- Advanced memory systems
- Specialized agents
- Complex monitoring
- Advanced validation
- OpenHands (if not viable in research phase)

---

# Success Metrics

## Week 1 — CLI + Engineering Brain
- [ ] CLI tool accepts idea and produces requirements, PRD, architecture
- [ ] All outputs saved to project folder
- [ ] No web dashboard, no database required

## Week 2 — Planning + Research
- [ ] Complete planning pipeline via CLI
- [ ] Project DNA stores engineering decisions
- [ ] OpenHands research complete with go/no-go decision
- [ ] Fallback execution path defined

## Week 3 — Execution
- [ ] Generates working code via templates
- [ ] Projects build successfully
- [ ] Tests pass
- [ ] End-to-end pipeline works for 2+ project types

## Week 4 — Polish & Release
- [ ] Product deployable via Docker
- [ ] Documentation complete
- [ ] Web dashboard exists only if strictly required
- [ ] Founder can use it to build real projects

## Final MVP
- [ ] Founder provides idea → Working project
- [ ] 3 different project types tested
- [ ] Usable for real software development
- [ ] Deadline: 20-30 days

---

# Next Steps

1. Founder approval of this revised strategy
2. Begin Day 1: CLI Skeleton + Project Structure
3. Milestone-based progress tracking (weekly demos)
4. Weekly review and adjustment
5. MVP completion by Day 28-30

---

# Appendix: Key Changes from v1.0

| Area | v1.0 | v2.0 |
|------|------|------|
| Progress model | Task-based (daily tasks) | Milestone-based (weekly working capabilities) |
| Interface | FastAPI + React (Day 1) | CLI-first (Day 1), dashboard deferred to Week 4 |
| Engineering Brain | Part of full stack | Standalone Python module, skeleton first |
| OpenHands | Assumed 2-day integration | Parallel research track, fallback path |
| Database | PostgreSQL (Day 1) | File-based storage, database deferred |
| Dashboard | Week 2 (Day 13) | Week 4, conditional |
| Risk management | Single path | Parallel tracks with decision points |

---

END OF MVP STRATEGY