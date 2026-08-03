# MetaGPT Research & Architecture Analysis

> **Comprehensive Report Artifact**: [metagpt_technical_analysis.md](file:///C:/Users/Jayesh/.gemini/antigravity-ide/brain/a15b6f9e-6379-422c-baf7-9c69da14247c/metagpt_technical_analysis.md)

## Overview
MetaGPT is a multi-agent framework designed to encode human Standard Operating Procedures (SOPs) into multi-agent workflows based on Large Language Models (LLMs). It structures agent interactions using role-based tasks, schema-validated outputs, and standardized publish-subscribe message routing.

## Capabilities
- **Multi-Agent Orchestration**: Role-based team execution (`Team`, `SoftwareCompany`).
- **Structured Agent Communication**: Pub/sub environment routing (`Environment`, `MessageQueue`, `Message`).
- **Dynamic Planning & Task Decomposition**: Topological task DAG ordering and lifecycle management (`Planner`, `Plan`, `Task`).
- **Schema-Constrained Generation**: Tree-structured LLM output parsing (`ActionNode`).
- **Tool System**: Centralized registration and execution (`ToolRegistry`, `@register_tool`, `Terminal`).
- **LLM Gateway**: Multi-provider client abstraction with cost accounting and retries (`BaseLLM`, `OpenAILLM`, `CostManager`).

## References
- Full 23-Section Technical Report: [metagpt_technical_analysis.md](file:///C:/Users/Jayesh/.gemini/antigravity-ide/brain/a15b6f9e-6379-422c-baf7-9c69da14247c/metagpt_technical_analysis.md)
