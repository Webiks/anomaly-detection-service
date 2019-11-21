import os
import sys
import logging
from flask import Flask
from dotenv import load_dotenv
from app.config import Config
from app.cron.scheduler import start_cron

cfg = Config().cfg

logger = logging.getLogger(__name__)
logger.setLevel(cfg.logger.logLevel)

fh = logging.FileHandler(cfg.logger.filename)
fh.setLevel(cfg.logger.logLevel)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(cfg.logger.logLevel)

formatter = logging.Formatter(cfg.logger.logFormat)
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

app = Flask(__name__)
load_dotenv()
app.webhook_url = os.getenv("WEBHOOKURL")

start_cron(cfg.cron.setInterval)



from app import routes


