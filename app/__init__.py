import os
import sys
import logging
from joblib import load
from flask import Flask
from dotenv import load_dotenv
from app.config import Config
from app.cron.scheduler import Scheduler
from app.handlers.predict_handler import run_predict, run_dry
from logging.handlers import RotatingFileHandler

cfg = Config.getInstance().cfg

logger = logging.getLogger(__name__)
logger.setLevel(cfg.logger.logLevel)

fh = RotatingFileHandler(cfg.logger.filename, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
fh.setLevel(cfg.logger.logLevel)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(cfg.logger.logLevel)

formatter = logging.Formatter(cfg.logger.logFormat)
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

logger.info(cfg)
app = Flask(__name__)

load_dotenv()
app.webhook_url = os.getenv("WEBHOOKURL")

app.rt = Scheduler(cfg.cron.setInterval, run_dry, "Elastic")

app.isfr_model = load(cfg.model.pathname)

from app import routes


