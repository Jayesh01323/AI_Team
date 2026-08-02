from typing import Any

from .validation_models import RepairPlan, ValidationReport


class ValidationExporter:
    @staticmethod
    def export_report_dict(report: ValidationReport) -> dict[str, Any]:
        return report.model_dump()

    @staticmethod
    def export_report_json(report: ValidationReport) -> str:
        return report.model_dump_json(indent=2)

    @staticmethod
    def report_summary(report: ValidationReport) -> str:
        stats = report.statistics
        return (f"ValidationReport: Valid={report.is_valid}, "
                f"Issues={stats.total_issues} "
                f"(Errors={stats.errors}, Warnings={stats.warnings}, Infos={stats.infos})")

    @staticmethod
    def export_plan_dict(plan: RepairPlan) -> dict[str, Any]:
        return plan.model_dump()

    @staticmethod
    def export_plan_json(plan: RepairPlan) -> str:
        return plan.model_dump_json(indent=2)

    @staticmethod
    def plan_summary(plan: RepairPlan) -> str:
        stats = plan.statistics
        return (f"RepairPlan: Actions={stats.total_actions}")
