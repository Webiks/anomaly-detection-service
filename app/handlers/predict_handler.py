import uuid
import json
import logging
import threading

from app.config import Config
from app.slack.slack import send_to_slack
from app.model.model_predict import get_data, predict
from app.handlers.anomaly_handler import publish_anomalies


cfg = Config.get_instance().cfg
logger = logging.getLogger(__name__)
d = {}

try:
    options = json.load(open(cfg.data_args.options_path))
except Exception as e:
    logger.error(e, expert=d)



def run_in_thread(traceId, model, from_time, to_time):
    d = {'trace': traceId}
    logger.debug(f'A new thread was spawned... Model is running from: {from_time} to: {to_time}', extra=d)
    logger.info(f'Retrieving DataFrame... Model is running from: {from_time} to: {to_time}', extra=d)
    data = get_data(traceId, cfg.data_args.index, from_time, to_time, cfg.elasticsearch.host,
                    cfg.elasticsearch.port, cfg.elasticsearch.username, cfg.elasticsearch.password, options)
    if data is None:
        logger.warning(f'There are no data to analyze...  ', extra=d)
    else:
        logger.info(f'Predicting on DataFrame...', extra=d)
        pred, outlier, anomalies = predict(model, data)

        size = anomalies.size
        anomalies = anomalies.sort_values(by=['host', 'timestamp'], ascending=[True, False])

        logger.info(f'publishing prediction...', extra=d)
        logger.debug(f'Save anomalies into elastic:  {anomalies}', extra=d)
        publish_anomalies(traceId, anomalies)

        msg = str(size) + cfg.slack.message  # TODO get message from config
        index = msg.find(' |')
        msg = msg[:index] + cfg.slack.link2kibana + msg[index:]
        logger.debug(f'Sending message to Slack from user: {cfg.slack.username} and text: {msg}', extra=d)
        send_to_slack(cfg.slack.webhook, msg, cfg.slack.username, cfg.slack.icon)

    logger.debug(f'Thread is done', extra=d)


def run_predict(traceId, model, from_time, to_time):
    if traceId is None:
        traceId = uuid.uuid4()
    d = {'trace': traceId}

    logger.info(f'A new thread is spawning...', extra=d)
    t = threading.Thread(target=run_in_thread, args=(traceId, model, from_time, to_time,))
    t.start()




