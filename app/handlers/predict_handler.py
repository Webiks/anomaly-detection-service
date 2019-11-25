import logging
from app.config import Config
from app.model.get_data import get_data
from app.model.monitor_model import predict
import threading
import uuid
import time
import pickle

cfg = Config.getInstance().cfg
logger = logging.getLogger(__name__)


def run_dry(name):
    logger.info('ran dry with name: {}' .format(name))


def run_predict():
    logger.info('Getting test data...')
    data = get_data(cfg.data_args.index, cfg.data_args.from_time, cfg.data_args.to_time, cfg.elasticsearch.host,
                    cfg.elasticsearch.port, cfg.elastic_auth.un, cfg.elastic_auth.pw, cfg.data_args.option_path)

    logger.info('Predicting on test set...')
    pred, outlier, anomalies = predict(app.isof_model, data)
    logger.info(pred)
    logger.info(outlier)
    logger.info(anomalies)



