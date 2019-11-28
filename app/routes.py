import uuid
import logging

from flask import make_response, jsonify, request

from app import app
from app.config import Config
from app.slack.slack import send_to_slack
from app.handlers.predict_handler import run_predict
from app.handlers.anomaly_handler import publish_anomalies

cfg = Config.get_instance().cfg
logger = logging.getLogger(__name__)


@app.route('/health')
def health():
    traceId = uuid.uuid4()
    d = {'trace': traceId}
    logger.info(f'health request from {request.environ["REMOTE_ADDR"]}', extra=d)
    return 'Server is up & running'


@app.route('/model/predict', methods=['POST'])
def predict():
    traceId = uuid.uuid4()
    d = {'trace': traceId}
    # TODO create unique id and return it ASAP to caller (run predict in thread/async)
    logger.debug(f'Message was sent from {request.environ["REMOTE_ADDR"]} '
                f'with url {request.url} and payload {request.get_json()}', extra=d)

    if not request.is_json:
        return f'Request is not containing a JSON payload'

    message = request.get_json()
    if 'from_time' not in message:
        logger.debug(f'Parameter \"from_time\" is required !!!')
        return f'Parameter \"from_time\" is required!'

    if 'to_time' not in message:
        logger.debug(f'Parameter \"to_time\" is required !!!')
        return f'Parameter \"to_time\" is required! '

    from_time = message['from_time']
    to_time = message['to_time']
    logger.debug(f'Model is running with date range from: {from_time} to: {to_time}', extra=d)
    run_predict(traceId, app.isof_model, from_time, to_time)
    return f'Model is running with date range from: {from_time} to: {to_time} with id [{traceId}]'


@app.route('/model/scheduler/interval', methods=['GET'])
def get_interval():
    traceId = uuid.uuid4()
    d = {'trace': traceId}
    interval = app.scheduler.get_interval()
    logger.info(f'The scheduler run on interval of {interval}sec... '
                f'Request from {request.environ["REMOTE_ADDR"]}', extra=d)
    return f'The scheduler run on interval of {interval}sec'


@app.route('/model/scheduler/stop', methods=['GET'])
def stop_model():
    traceId = uuid.uuid4()
    d = {'trace': traceId}
    logger.info(f'The scheduler with interval of {app.scheduler.interval}sec '
                f'has been stopped by {request.environ["REMOTE_ADDR"]}', extra=d)
    app.scheduler.stop()
    return f'The scheduler has been stopped.'


@app.route('/model/scheduler/start', methods=['POST'])
def start_model():
    # TODO add start scheduler + get scheduler interval
    traceId = uuid.uuid4()
    d = {'trace': traceId}

    if request.is_json:
        message = request.get_json()
        if 'interval' in message:
            interval = message['interval']
            logger.info(f'The scheduler with interval of {interval}sec '
                f'has been started by {request.environ["REMOTE_ADDR"]}', extra=d)
            app.scheduler.set_interval(interval)

    app.scheduler.start()
    return f'The scheduler start with interval of {app.scheduler.get_interval()}sec '


if cfg.server.test_mode:
    @app.route('/elastic', methods=['POST'])
    def alert():
        logger.info(request.environ['REMOTE_ADDR'])
        publish_anomalies()
        return 'Server is up & running'


    @app.route('/slack', methods=['POST', 'GET'])
    def parse_request():
        data = request.form['payload']
        logger.info('Message: \"{}\" sent by {}'.format(data, cfg.username))
        send_to_slack(app.webhook_url, data, cfg.username, cfg.icon),
        return 'message sent to Slack'


@app.errorhandler(404)
def not_found(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def internal_error(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)
