from app.config import Config  # Must be first
import uuid
import copy
import logging

from flask import Flask

from app.cron.scheduler import Scheduler
from app.model.model_predict import load_model
from app.handlers.predict_handler import run_predict

traceId = uuid.uuid4()
d = {'trace': traceId}
cfg = Config.get_instance().cfg
logger = logging.getLogger(__name__)
# logger = logging.LoggerAdapter(logger, extra)

config = copy.deepcopy(cfg)
config.elasticsearch.password = cfg.secret
config.slack.webhook = cfg.secret
logger.info(f'Config: {config}', extra=d)

app = Flask(__name__)
app.isof_model = load_model(cfg.model.pathname)
if app.isof_model is not None:
    logger.info(f'Scheduler is starting with interval: {cfg.scheduler.interval}sec, ', extra=d)
    logger.debug(f'Scheduler is starting with interval: {cfg.scheduler.interval}sec, '
                 f'running predictions with model: \"{cfg.model.name}\" (path: {cfg.model.pathname}) '
                 f'and date ranges from: {cfg.data_args.from_time} to: {cfg.data_args.to_time}', extra=d)
    app.scheduler = Scheduler(cfg.scheduler.interval, run_predict,
                              None, app.isof_model, cfg.data_args.from_time, cfg.data_args.to_time)

    from app import routes
else:
    logger.fatal(f'There is no model available at this time...application terminate', extra=d)
    exit(0)
