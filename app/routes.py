import uuid
import logging

from flask import make_response, jsonify, request, abort

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
    extra = {'trace': traceId}
    logger.debug(f'health request from {request.environ["REMOTE_ADDR"]}', extra)
    return 'Server is up & running'


@app.route('/model/predict', methods=['POST'])
def predict():
    traceId = uuid.uuid4()
    d = {'trace': traceId}
    logger.debug(f'Message was sent from {request.environ["REMOTE_ADDR"]} '
                f'with url {request.url} and payload {request.get_json()}', extra=d)

    if not request.is_json:
        abort(400, f'Request is not containing a JSON payload')

    message = request.get_json()
    if 'from_time' not in message:
        logger.debug(f'Parameter \"from_time\" is required !!!', extra=d)
        abort(400, f'Parameter \"from_time\" is required!')

    if 'to_time' not in message:
        logger.debug(f'Parameter \"to_time\" is required !!!', extra=d)
        abort(400, f'Parameter \"to_time\" is required! ')

    from_time = message['from_time']
    to_time = message['to_time']
    logger.debug(f'Model is running with date range from: {from_time} to: {to_time}', extra=d)
    run_predict(traceId, app.isof_model, from_time, to_time)
    return f'Model is running with date range from: {from_time} to: {to_time} with id [{traceId}]'


@app.route('/model/scheduler/interval', methods=['GET'])
def get_interval():
    traceId = uuid.uuid4()
    d = {'trace': traceId}
    interval = app.scheduler.interval
    logger.debug(f'The scheduler run on interval of {interval}sec... '
                f'Request from {request.environ["REMOTE_ADDR"]}', extra=d)
    return f'The scheduler run on interval of {interval}sec'


@app.route('/model/scheduler/stop', methods=['GET'])
def stop_model():
    traceId = uuid.uuid4()
    d = {'trace': traceId}
    logger.debug(f'The scheduler with interval of {app.scheduler.interval}sec '
                f'has been stopped by {request.environ["REMOTE_ADDR"]}', extra=d)
    app.scheduler.stop()
    return f'The scheduler has been stopped.'


@app.route('/model/scheduler/start', methods=['POST'])
def start_model():
    traceId = uuid.uuid4()
    d = {'trace': traceId}

    interval = app.scheduler.interval
    if request.is_json:
        message = request.get_json()
        if 'interval' in message:
            interval = message['interval']

    logger.debug(f'The scheduler with interval of {interval}sec '
                 f'has been started by {request.environ["REMOTE_ADDR"]}', extra=d)
    app.scheduler.stop()
    app.scheduler.start(interval)
    return f'The scheduler start with interval of {app.scheduler.interval}sec'


if cfg.server.test_mode:
    @app.route('/test/elastic', methods=['POST'])
    def test_elastic():
        logger.debug(request.environ['REMOTE_ADDR'], extra=d)
        publish_anomalies()
        return 'Server is up & running'


    @app.route('/test/slack', methods=['POST', 'GET'])
    def test_slack():
        data = request.form['payload']
        logger.debug(f'Message: \"{data}\" sent by {cfg.slack.username}', extra=d)
        send_to_slack(cfg.slack.webhook, data, cfg.slack.username, cfg.slack.icon),
        return 'message sent to Slack'


@app.errorhandler(400)
def bad_request(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Bad Request'}), 400)

@app.errorhandler(404)
def not_found(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def internal_error(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)
