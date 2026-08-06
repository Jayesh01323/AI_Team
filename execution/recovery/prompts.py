"""
Prompts and templates for Self-Healing Error Recovery Engine.

Constructs remediation instructions for AI coding agents based on validation failure feedback.
"""

from execution.validation.pipeline import ValidationResult


def format_recovery_prompt(
    original_instruction: str,
    validation_results: list[ValidationResult],
    attempt: int,
    max_retries: int,
    error_log: str | None = None,
) -> str:
    """Formats a corrective remediation prompt for an execution retry.

    Includes exact validator failures, error messages, stack traces, and instructions.
    """
    failing_validators = [r for r in validation_results if not r.success]

    lines = [
        f"=== RECOVERY ATTEMPT {attempt}/{max_retries} ===",
        "Your previous code generation turn failed quality gate checks.",
        "",
        "ORIGINAL INSTRUCTION:",
        original_instruction.strip(),
        "",
        "VALIDATION FAILURES:",
    ]

    if failing_validators:
        for val in failing_validators:
            lines.append(f"[{val.validator_name}] Failed")
            for err in val.errors:
                lines.append(f"  - {err.strip()}")
            if val.output:
                lines.append("  Output log:")
                for output_line in val.output.strip().splitlines()[:20]:
                    lines.append(f"    | {output_line}")
            lines.append("")
    else:
        lines.append("  - General execution validation failure")
        lines.append("")

    if error_log:
        lines.append("EXECUTION ERROR LOG:")
        lines.append(error_log.strip())
        lines.append("")

    lines.extend([
        "REMEDIATION DIRECTIVES:",
        "1. Analyze the validation errors and stack traces above.",
        "2. Fix all syntax, linting, formatting, or test issues.",
        "3. Ensure all modified files pass clean build and test checks.",
        "4. Do not introduce breaking changes or undo working features.",
    ])

    return "\n".join(lines)
