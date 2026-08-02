"""
ai-team CLI - Autonomous AI Engineering Team Command Line Interface.

Usage:
    ai-team --help
    ai-team init "<project idea>"
    ai-team test-provider
    ai-team analyze "<project idea>"
    ai-team generate "<project idea>"
    ai-team pipeline "<project idea>"
"""

import json
from pathlib import Path

import click

from core.config import PROJECTS_DIR
from core.logging import get_logger
from core.utils import sanitize_project_name

logger = get_logger(__name__)


def create_placeholder_file(filepath: Path, content: str) -> None:
    """Write a placeholder file to the project directory."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    rel_path = filepath.relative_to(PROJECTS_DIR.parent)
    click.echo(f"  Created: {rel_path}")


@click.group()
def cli():
    """Autonomous AI Engineering Team - Transform ideas into software projects."""


@cli.command()
@click.argument("idea")
def init(idea: str):
    """
    Initialize a new project from an idea.

    Creates a project folder inside projects/ and generates placeholder
    documents: requirements.md, prd.md, architecture.md, tech-stack.json.
    """
    click.echo("")
    click.echo(f'=== Initializing project from idea: "{idea}" ===')
    click.echo("")

    project_name = sanitize_project_name(idea)
    project_dir = PROJECTS_DIR / project_name

    if project_dir.exists():
        click.echo(f"ERROR: Project directory already exists: projects/{project_name}/")
        raise SystemExit(1)

    project_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Project folder: projects/{project_name}/")
    click.echo("")
    click.echo("Creating placeholder files...")
    click.echo("")

    requirements_md = f"""# Requirements

Generated from idea: "{idea}"

## Overview

This document defines the functional and non-functional requirements for the project.

## Functional Requirements

- TBD

## Non-Functional Requirements

- TBD

## Priority

- TBD

---

*Placeholder — to be implemented by Engineering Brain.*
"""
    create_placeholder_file(project_dir / "requirements.md", requirements_md)

    prd_md = f"""# Product Requirements Document (PRD)

Generated from idea: "{idea}"

## Overview

- TBD

## User Stories

- TBD

## Acceptance Criteria

- TBD

## Feature Breakdown

- TBD

---

*Placeholder — to be implemented by Engineering Brain.*
"""
    create_placeholder_file(project_dir / "prd.md", prd_md)

    architecture_md = f"""# Architecture

Generated from idea: "{idea}"

## Overview

- TBD

## System Design

- TBD

## Component Breakdown

- TBD

## Technology Recommendations

- TBD

---

*Placeholder — to be implemented by Engineering Brain.*
"""
    create_placeholder_file(project_dir / "architecture.md", architecture_md)

    tech_stack_json = json.dumps(
        {
            "project": project_name,
            "idea": idea,
            "tech_stack": {
                "backend": None,
                "frontend": None,
                "database": None,
                "language": None,
                "framework": None,
            },
            "dependencies": [],
            "status": "placeholder",
        },
        indent=2,
    )
    create_placeholder_file(project_dir / "tech-stack.json", tech_stack_json)

    click.echo("")
    click.echo(f"Project initialized: projects/{project_name}/")
    click.echo("")
    click.echo("Next steps:")
    click.echo("  Brain modules will populate these files with real content.")
    click.echo(
        "  See: brain/idea/, brain/requirements/, brain/prd/, brain/architecture/, brain/techstack/"
    )


@cli.command()
def test_provider():
    """
    Test the configured AI provider.

    Verifies the provider can return a response using the
    current configuration and API credentials.
    """
    from app.provider_service import test_provider as run_test

    click.echo("")
    click.echo("=== Testing AI Provider ===")
    click.echo("")

    try:
        result = run_test()
        click.echo(f"Provider:     {result.provider_name}")
        click.echo(f"Model:        {result.model}")
        click.echo(f"Response:     {result.text}")
        click.echo(f"Finish:       {result.finish_reason}")
        click.echo(f"Input tokens: {result.input_tokens}")
        click.echo(f"Output tokens:{result.output_tokens}")
        click.echo("")
        click.echo("SUCCESS: Provider is working correctly.")
    except Exception as exc:
        click.echo(f"ERROR: {exc!s}")
        click.echo("")
        click.echo("FAILED: Provider test did not pass.")
        raise SystemExit(1) from exc


@cli.command()
@click.argument("idea")
def analyze(idea: str):
    """
    Analyze a project idea using the Engineering Brain.

    Uses the configured AI provider to decompose the idea into
    a structured model with requirements, risks, unknowns, etc.
    """
    from app.brain_service import analyze_idea as run_analysis

    click.echo("")
    click.echo("=== Analyzing Idea ===")
    click.echo("")
    click.echo(f'Idea: "{idea}"')
    click.echo("")

    try:
        context = run_analysis(idea)
        click.echo(json.dumps(context.to_dict(), indent=2))
        click.echo("")
        click.echo("SUCCESS: Idea analysis complete.")
    except Exception as exc:
        click.echo(f"ERROR: {exc!s}")
        click.echo("")
        click.echo("FAILED: Idea analysis did not complete.")
        raise SystemExit(1) from exc


@cli.command()
@click.argument("idea")
def generate(idea: str):
    """
    Analyze an idea and generate structured requirements.

    Runs Idea Analysis -> Requirements Generation.
    Writes requirements.md to the project folder.
    """
    from app.brain_service import analyze_and_generate_requirements as run_pipeline

    click.echo("")
    click.echo("=== Generating Requirements from Idea ===")
    click.echo("")
    click.echo(f'Idea: "{idea}"')
    click.echo("")

    try:
        context = run_pipeline(idea)
        click.echo(json.dumps(context.to_dict(), indent=2))
        click.echo("")
        click.echo("SUCCESS: Requirements generated.")
        click.echo(f"  Project folder: projects/{context.project_name}/")
    except Exception as exc:
        click.echo(f"ERROR: {exc!s}")
        click.echo("")
        click.echo("FAILED: Requirements generation did not complete.")
        raise SystemExit(1) from exc


@cli.command()
@click.argument("idea")
def pipeline(idea: str):
    """
    Run the full Engineering Brain pipeline.

    Stages:
        1. Idea Analysis
        2. Requirements Generation
        3. PRD Generation
        4. ProjectSpecification Generation
        5. Architecture Generation
        6. Task Planning

    Produces requirements.md, PRD.md, prd.json, project_specification.json, architecture.json, ARCHITECTURE.md, task_plan.json, and TASKS.md on disk.
    """
    from app.brain_service import run_full_pipeline as run_all

    click.echo("")
    click.echo("=== Running Full Engineering Pipeline ===")
    click.echo("")
    click.echo(f'Idea: "{idea}"')
    click.echo("")

    try:
        context = run_all(idea)
        click.echo(json.dumps(context.to_dict(), indent=2))
        click.echo("")
        click.echo("SUCCESS: Full pipeline complete.")
        click.echo(f"  Project folder: projects/{context.project_name}/")
        click.echo("  Artifacts:")
        click.echo("    - requirements.md")
        click.echo("    - PRD.md")
        click.echo("    - prd.json")
        click.echo("    - project_specification.json")
        click.echo("    - architecture.json")
        click.echo("    - ARCHITECTURE.md")
        click.echo("    - task_plan.json")
        click.echo("    - TASKS.md")
    except Exception as exc:
        click.echo(f"ERROR: {exc!s}")
        click.echo("")
        click.echo("FAILED: Pipeline did not complete.")
        raise SystemExit(1) from exc


@cli.command()
@click.argument("idea")
def scaffold(idea: str):
    """
    Run the Engineering Brain and scaffold the repository.
    """
    from app.brain_service import run_full_pipeline
    from core.config import PROJECTS_DIR
    from execution.repository.generator import RepositoryGenerator

    click.echo("")
    click.echo("=== Running Engineering Brain & Scaffolding ===")
    click.echo("")

    try:
        click.echo("1. Running Engineering Pipeline...")
        context = run_full_pipeline(idea)

        click.echo("2. Generating Repository...")
        generator = RepositoryGenerator(base_dir=PROJECTS_DIR)
        report = generator.generate(context)

        if report.is_successful():
            click.echo(f"SUCCESS: Repository scaffolded at {report.repository_path}")
            for f in report.files_created:
                click.echo(f"  Created: {f}")
        else:
            click.echo(f"FAILED: Repository generation failed: {report.error_message}")
            raise SystemExit(1)

    except Exception as exc:
        click.echo(f"ERROR: {exc!s}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    cli()
