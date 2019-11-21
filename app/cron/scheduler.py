import time
import logging
from timeloop import Timeloop
from datetime import timedelta

logger = logging.getLogger(__name__)
# run a task in a set interval
tl = Timeloop()


def start_cron(period):
    @tl.job(interval=timedelta(seconds=period))
    def sample_job_every_2s():
        data = (str(period) + " sec job current time : {}").format(time.ctime())
        logger.info(data)
        # integrate the app you want to run

    tl.start()  # block=True


def stop_cron():
    tl.stop()
