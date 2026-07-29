import datetime
from pathlib import Path

from execution.repository.filesystem import FileSystem
from execution.repository.scaffolder import ProjectScaffolder
from execution.validation.workflow import ValidationWorkflow
from models.generation_report import GenerationReport, ValidationStep
from models.project_context import ProjectContext


class RepositoryGenerator:
    """Orchestrates the generation of the repository."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def generate(self, context: ProjectContext) -> GenerationReport:
        project_dir = self.base_dir / context.project_name

        report = GenerationReport(
            project_name=context.project_name,
            repository_path=str(project_dir),
            created_at=datetime.datetime.now(datetime.UTC),
            status="PENDING",
        )

        try:
            fs = FileSystem(project_dir)
            scaffolder = ProjectScaffolder(fs)

            # Scaffold basic dirs & git
            files_created = scaffolder.scaffold(context)

            # Apply Template Engine
            from execution.templates.engine import TemplateEngine

            assets_dir = Path(__file__).parent.parent / "templates" / "assets"
            template_engine = TemplateEngine(assets_dir, fs)

            variables = {
                "project_name": context.project_name,
                "project_description": context.idea.summary
                if context.idea
                else "A generated project",
                "database_url": "postgresql://user:password@localhost:5432/dbname",
                "api_port": "8000",
            }

            rendered_files = template_engine.render_template("base", "v1", variables)
            files_created.extend(rendered_files)

            # Apply dynamic tech stack templates
            if context.architecture and context.architecture.technology_stack:
                tech_stack = context.architecture.technology_stack

                backend = tech_stack.get("backend", "").lower()
                if "fastapi" in backend:
                    backend_files = template_engine.render_template(
                        "fastapi", "v1", variables
                    )
                    files_created.extend(backend_files)

                frontend = tech_stack.get("frontend", "").lower()
                if "react" in frontend:
                    frontend_files = template_engine.render_template(
                        "react", "v1", variables
                    )
                    files_created.extend(frontend_files)

            # De-duplicate files
            report.files_created = list(set(files_created))

            # Validate
            val_report = ValidationWorkflow.run(project_dir)
            report.validation_report = val_report

            if not val_report.is_successful():
                report.status = "FAILED"
                report.error_message = "; ".join(val_report.errors)
                report.validation_steps.append(
                    ValidationStep(
                        step_name="Repository Validation",
                        status="FAILED",
                        logs="\n".join(val_report.errors),
                        exit_code=1,
                    )
                )
            else:
                report.status = "SUCCESS"
                report.validation_steps.append(
                    ValidationStep(
                        step_name="Repository Validation",
                        status="SUCCESS",
                        logs="All checks passed.",
                        exit_code=0,
                    )
                )

                # Apply Execution Adapter (Integration Prep)
                from execution.adapters.factory import AdapterFactory

                try:
                    adapter = AdapterFactory.get_adapter("openhands")
                    adapter.prepare(context, project_dir)
                except (ValueError, RuntimeError, OSError) as e:
                    report.status = "FAILED"
                    report.error_message = f"Failed to prepare adapter: {e!s}"

        except (ValueError, RuntimeError, OSError) as e:
            report.status = "FAILED"
            report.error_message = str(e)

        return report
