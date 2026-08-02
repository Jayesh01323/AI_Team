
from .validation_models import (
    RepairAction,
    RepairActionType,
    RepairPlan,
    RepairStatistics,
    Severity,
    ValidationIssue,
    ValidationReport,
)


class RepairPlanner:
    def __init__(self):
        # Priority mapping for deterministic ordering (lower is higher priority)
        self.priority_map = {
            RepairActionType.CREATE_FILE: 10,
            RepairActionType.UPDATE_METADATA: 20,
            RepairActionType.RENAME_FILE: 30,
            RepairActionType.MOVE_FILE: 40,
            RepairActionType.REMOVE_DUPLICATE: 50,
            RepairActionType.FIX_PLACEHOLDER: 60,
            RepairActionType.REGENERATE_FILE: 70,
            RepairActionType.DELETE_FILE: 80,
        }
        self.severity_map = {
            Severity.ERROR: 10,
            Severity.WARNING: 20,
            Severity.INFO: 30,
        }

    def plan_repairs(self, report: ValidationReport) -> RepairPlan:
        actions: list[RepairAction] = []
        action_stats: dict[str, int] = {t.value: 0 for t in RepairActionType}
        severity_stats: dict[str, int] = {s.value: 0 for s in Severity}

        for issue in report.issues:
            action = self._create_action_for_issue(issue)
            if action:
                actions.append(action)
                action_stats[action.type.value] += 1
                severity_stats[action.severity.value] += 1

        # Deterministic sorting: 1. priority, 2. severity, 3. action_type, 4. target, 5. id
        actions.sort(key=lambda x: (
            x.deterministic_priority,
            self.severity_map.get(x.severity, 100),
            x.type.value,
            x.target,
            x.id
        ))

        stats = RepairStatistics(
            total_actions=len(actions),
            actions_by_type=action_stats,
            actions_by_severity=severity_stats
        )

        return RepairPlan(
            actions=actions,
            statistics=stats
        )

    def _create_action_for_issue(self, issue: ValidationIssue) -> RepairAction:
        action_type = None
        priority = 100
        
        if issue.type in ("duplicate_file", "duplicate_directory"):
            action_type = RepairActionType.REMOVE_DUPLICATE
        elif issue.type in ("missing_metadata", "invalid_generated_from", "missing_checksum", "invalid_checksum", "invalid_template_id"):
            action_type = RepairActionType.UPDATE_METADATA
        elif issue.type == "empty_file":
            action_type = RepairActionType.REGENERATE_FILE
        elif issue.type == "unresolved_placeholder":
            action_type = RepairActionType.FIX_PLACEHOLDER
        elif issue.type == "invalid_filename":
            action_type = RepairActionType.RENAME_FILE
        elif issue.type == "unknown_component":
            action_type = RepairActionType.UPDATE_METADATA
            
        if not action_type:
            # Fallback action
            action_type = RepairActionType.REGENERATE_FILE
            
        priority = self.priority_map.get(action_type, 100)

        return RepairAction(
            id=f"repair_{issue.id}",
            type=action_type,
            reason=f"Fixing {issue.type}: {issue.message}",
            severity=issue.severity,
            target=issue.target,
            deterministic_priority=priority,
            dependencies=[issue.id],
            issue_id=issue.id,
            metadata=issue.metadata
        )
