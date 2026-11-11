from receipts.registry.loader import read_event_seed
from receipts.settings import get_settings


def run_stage(stage: str, event: str) -> None:
    from receipts.pipeline.discover import run_discover
    from receipts.pipeline.extract import run_extract
    from receipts.pipeline.rank import run_rank
    from receipts.pipeline.registry_write import run_write
    from receipts.pipeline.resolve import run_resolve
    from receipts.pipeline.transcripts_stage import run_transcripts

    seed = read_event_seed(get_settings().data_dir / "events" / f"{event}.yaml")
    stages = {
        "discover": lambda: run_discover(seed),
        "transcripts": lambda: run_transcripts(event),
        "extract": lambda: run_extract(seed),
        "rank": lambda: run_rank(seed),
        "resolve": lambda: run_resolve(seed),
        "write": lambda: run_write(seed),
    }
    order = list(stages)
    for name in order if stage == "build" else [stage]:
        print(f"== {name}", flush=True)
        stages[name]()
