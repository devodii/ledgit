import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from receipts.models.pipeline import StageReport
from receipts.settings import get_settings


def reports_dir(event: str) -> Path:
    path = get_settings().data_dir / "reports" / event
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_report(
    stage: str,
    event: str,
    counts_in: int,
    counts_out: int,
    drops: dict[str, int],
    notes: list[str] | None = None,
) -> StageReport:
    report = StageReport(
        stage=stage,
        event=event,
        counts_in=counts_in,
        counts_out=counts_out,
        drops=dict(sorted(drops.items())),
        notes=notes or [],
        finished_at=datetime.now(UTC),
    )
    (reports_dir(event) / f"{stage}.json").write_text(report.model_dump_json(indent=2))
    return report


def stage_cache(name: str) -> Path:
    path = get_settings().cache_dir / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())
