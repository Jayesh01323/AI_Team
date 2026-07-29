import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class StructuredProviderLogEntry:
    timestamp: str
    provider: str
    model: str
    task_id: str
    execution_id: str
    status: str
    duration_ms: float
    error: str | None = None
    correlation_id: str | None = None


class ProviderStructuredLogger:
    def __init__(self, log_path: Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        provider: str,
        model: str,
        task_id: str,
        execution_id: str,
        status: str,
        duration_ms: float,
        error: str | None = None,
        correlation_id: str | None = None,
    ) -> StructuredProviderLogEntry:
        """Writes a structured log entry as a JSON Line (.jsonl)."""
        entry = StructuredProviderLogEntry(
            timestamp=datetime.now(UTC).isoformat(),
            provider=provider,
            model=model,
            task_id=task_id,
            execution_id=execution_id,
            status=status,
            duration_ms=round(duration_ms, 2),
            error=error,
            correlation_id=correlation_id,
        )

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

        return entry

    def read_entries(self) -> list[dict[str, Any]]:
        """Reads and parses all JSON Lines log entries from the log file."""
        if not self.log_path.exists():
            return []
        entries = []
        with open(self.log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries
