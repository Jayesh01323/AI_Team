# ARCHITECTURE.md

# Autonomous AI Engineering Team
## System Architecture

Version: 1.0
Status: 🔒 LOCKED

---

# Purpose

This document defines the complete technical architecture of the Autonomous AI Engineering Team.

MASTER_SPEC.md defines WHAT.

ARCHITECTURE.md defines HOW.

---

# High-Level Architecture

                    Human Founder
                           │
                           ▼
                  React Dashboard (UI)
                           │
                           ▼
                  FastAPI API Gateway
                           │
      ┌────────────────────┼────────────────────┐
      ▼                    ▼                    ▼
 Engineering Brain    Workflow Engine     Memory System
      │                    │                    │
      └────────────────────┼────────────────────┘
                           ▼
                  Agent Runtime Layer
                           │
      ┌────────────────────┼────────────────────┐
      ▼                    ▼                    ▼
    OpenHands          LangGraph           MetaGPT
                           │
                           ▼
                  Generated Project

---

# System Layers

Layer 1

Presentation

React

Dashboard

Authentication

Settings

Monitoring

---

Layer 2

Backend

FastAPI

REST API

WebSocket

Authentication

Configuration

---

Layer 3

Engineering Brain

Idea Analysis

Requirement Generation

Research

PRD

Architecture

Planning

Decision Engine

---

Layer 4

Workflow Engine

Task Creation

Scheduling

Execution

Review

State Machine

Agent Routing

---

Layer 5

Agent Runtime

Engineering Manager

Product Manager

Architect

Backend Engineer

Frontend Engineer

Database Engineer

QA

DevOps

Documentation

---

Layer 6

Memory

Project Memory

Decision Memory

Knowledge Graph

Context

Version History

Project DNA

---

Layer 7

Execution

Repository

Files

Code

Tests

Documentation

Deployment

---

# Service Responsibilities

## API Gateway

Responsible for

Authentication

REST APIs

Rate Limiting

Request Routing

---

## Engineering Brain

Responsible for

Thinking

Decision Making

Planning

Risk Analysis

Never writes production code.

---

## Workflow Engine

Responsible for

Task Flow

Execution Order

Agent Communication

Retries

Approvals

---

## Agent Runtime

Responsible for

Executing engineering tasks.

---

## Memory

Responsible for

Long-term knowledge.

---

## Execution Engine

Responsible for

Generating

Files

Folders

Repositories

Code

Tests

Documentation

---

## Validation Engine

Responsible for

Build

Testing

Lint

Security

Performance

Documentation

Quality Gates

---

# Data Flow

Idea

↓

Idea Analysis

↓

Requirements

↓

Research

↓

PRD

↓

Architecture

↓

Planning

↓

Task Creation

↓

Agent Execution

↓

Validation

↓

Documentation

↓

Deployment

↓

Complete

---

# Repository Structure

backend/

frontend/

agents/

brain/

workflow/

memory/

execution/

validation/

projects/

docs/

tests/

scripts/

docker/

.github/

README.md

MASTER_SPEC.md

ARCHITECTURE.md

ROADMAP.md

PROJECT_DNA.md

DECISIONS.md

---

# Engineering Team

Engineering Manager

↓

Product Manager

↓

Architect

↓

Engineering Lead

↓

Backend

Frontend

Database

↓

QA

↓

DevOps

↓

Documentation

---

# Agent Communication

Human

↓

Engineering Manager

↓

Specialized Agents

↓

Engineering Manager

↓

Human

No direct communication between Human and worker agents.

---

# State Machine

Created

↓

Planning

↓

Assigned

↓

Running

↓

Review

↓

Approved

↓

Completed

Failure

↓

Retry

↓

Escalation

↓

Human Review

---

# Memory Architecture

Short-Term Memory

Current Task

Current Conversation

Current Files

↓

Project Memory

Requirements

Architecture

Code

Tests

↓

Knowledge Graph

Relationships

↓

Project DNA

Permanent Memory

---

# Quality Pipeline

Generate

↓

Build

↓

Lint

↓

Type Check

↓

Unit Tests

↓

Integration Tests

↓

Documentation Check

↓

Security Scan

↓

Performance Review

↓

Ready

---

# External Integrations

OpenHands

LangGraph

MetaGPT

GitHub

Docker

OpenRouter

Gemini

Claude

OpenAI

Local Models

---

# Database

PostgreSQL

Stores

Users

Projects

Tasks

Agents

Memories

Workflows

Project DNA

Logs

---

# Security

Authentication

Authorization

Secrets

Encrypted Storage

Audit Logs

Approval Gates

---

# Scalability

Stateless Backend

Horizontal Scaling

Queue-Based Execution

Parallel Agents

Distributed Memory

---

# Error Recovery

Failure Detection

Automatic Retry

Self-Healing

Escalation

Rollback

Recovery

---

# Engineering Principles

Single Responsibility

Modularity

Scalability

Maintainability

Observability

Testability

Reusability

Architecture First

---

END OF ARCHITECTURE.md
