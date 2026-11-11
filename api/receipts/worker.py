import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from receipts.settings import check_settings, get_settings
from receipts.verify.engine import run_verify

log = logging.getLogger("receipts.worker")


def verify_job() -> None:
    log.info(run_verify())


def main() -> None:
    settings = get_settings()
    check_settings(settings)
    logging.basicConfig(level=settings.log_level)
    scheduler = BlockingScheduler(timezone="UTC")
    if settings.scheduler_enabled:
        scheduler.add_job(
            verify_job, CronTrigger.from_crontab(settings.verify_cron, timezone="UTC")
        )
    log.info(
        "worker started, scheduler_enabled=%s cron=%s",
        settings.scheduler_enabled,
        settings.verify_cron,
    )
    scheduler.start()


if __name__ == "__main__":
    main()
