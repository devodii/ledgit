import logging
import time

from receipts.settings import check_settings, get_settings

log = logging.getLogger("receipts.worker")


def main() -> None:
    settings = get_settings()
    check_settings(settings)
    logging.basicConfig(level=settings.log_level)
    log.info("worker started, scheduler_enabled=%s", settings.scheduler_enabled)
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
