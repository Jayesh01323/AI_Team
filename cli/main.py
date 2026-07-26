"""
ai-team CLI - Autonomous AI Engineering Team Command Line Interface.

Usage:
    ai-team --help
    ai-team init "<project idea>"
    ai-team test-provider
    ai-team analyze "<project idea>"
"""

import json
import click
from pathlib import Path
import re

from core.config import PROJECTS_DIR
from core.logging import get_logger

logger = get_logger(__name__)


def sanitize_project_name(idea: str) -> str:
    """Convert an idea string into a sanitized directory name."""
    name = idea.lower().strip()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = name.strip("-")
    return name[:64]


def create_placeholder_file(filepath: Path, content: str) -> None:
    """Write a placeholder file to the project directory."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    rel_path = filepath.relative_to(PROJECTS_DIR.parent)
    click.echo(f"  Created: {rel_path}")


@click.group()
def cli():
    """Autonomous AI Engineering Team - Transform ideas into software projects."""
    pass


@cli.command()
@click.argument("idea")
def init(idea: str):
    """
    Initialize a new project from an idea.

    Creates a project folder inside projects/ and generates placeholder
    documents: requirements.md, prd.md, architecture.md, tech-stack.json.
    """
    click.echo("")
    click.echo("=== Initializing project from idea: \"%s\" ===" % idea)
    click.echo("")

    project_name = sanitize_project_name(idea)
    project_dir = PROJECTS_DIR / project_name

    if project_dir.exists():
        click.echo("ERROR: Project directory already exists: projects/%s/" % project_name)
        raise SystemExit(1)

    project_dir.mkdir(parents=True, exist_ok=True)

    click.echo("Project folder: projects/%s/" % project_name)
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
    click.echo("Project initialized: projects/%s/" % project_name)
    click.echo("")
    click.echo("Next steps:")
    click.echo("  Brain modules will populate these files with real content.")
    click.echo("  See: brain/idea/, brain/requirements/, brain/prd/, brain/architecture/, brain/techstack/")


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
        click.echo("Provider:     %s" % result.provider_name)
        click.echo("Model:        %s" % result.model)
        click.echo("Response:     %s" % result.text)
        click.echo("Finish:       %s" % result.finish_reason)
        click.echo("Input tokens: %s" % result.input_tokens)
        click.echo("Output tokens:%s" % result.output_tokens)
        click.echo("")
        click.echo("SUCCESS: Provider is working correctly.")
    except Exception as exc:
        click.echo("ERROR: %s" % str(exc))
        click.echo("")
        click.echo("FAILED: Provider test did not pass.")
        raise SystemExit(1)


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
    click.echo("Idea: \"%s\"" % idea)
    click.echo("")

    try:
        context = run_analysis(idea)
        click.echo(json.dumps(context.to_dict(), indent=2))
        click.echo("")
        click.echo("SUCCESS: Idea analysis complete.")
    except Exception as exc:
        click.echo("ERROR: %s" % str(exc))
        click.echo("")
        click.echo("FAILED: Idea analysis did not complete.")
        raise SystemExit(1)


if __name__ == "__main__":
    cli()