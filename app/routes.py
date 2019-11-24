import logging
import argparse
import threading
from app import app
from app.config import Config
from app.slack.slack import send_to_slack
from app.elastic.elasticpy import download_json
from flask import make_response, jsonify, request


cfg = Config.getInstance().cfg
logger = logging.getLogger(__name__)
logger.info(cfg)


@app.route('/health')
def health():
    logger.info(request.environ['REMOTE_ADDR'])
    return 'Server is up & running'


@app.route('/model/run', methods=['POST'])
def run():
    logger.info(request.environ['REMOTE_ADDR'])
    start = request.form['from']
    end = request.form['to']
    logger.info('Model is running from {} to {}' .format(start, end))
    #
    return 'Model is running from {} to {}' .format(start, end)


@app.route('/model/stop', methods=['GET'])
def stop_model():
    logger.info('The model has been stopped by {}' .format(request.environ['REMOTE_ADDR']))
    app.rt.stop()
    return 'The model has been stopped.'


@app.route('/slack', methods=['POST', 'GET'])
def parse_request():
    data = request.form['payload']
    logger.info('Message: \"{}\" sent by {}' .format(data, cfg.username))
    send_to_slack(app.webhook_url, data, cfg.username, cfg.icon),
    return 'message sent to Slack'


@app.route('/elastic', methods=['GET'])
def download():
    parser = argparse.ArgumentParser(description='Download elastic search last X minutes on an index')
    parser.add_argument('--path', '-o', help='JSON output path', type=str, default="../elastic.json", required=False)
    parser.add_argument('--index', '-i', help="ElasticSearch index", type=str, default='metricbeat-*', required=False)
    parser.add_argument('--lastMinutes', '-m', help="Last minutes to get data for", dest='last_minutes', type=int, default=5, required=False)
    parser.add_argument('--host', '-a', help="ElasticSearch Host's ip/address", type=str, default='elastic.monitor.net', required=False)
    parser.add_argument('--port', '-p', help="ElasticSearch Host's port", type=int, default=9200, required=False)
    parser.add_argument('--user', '-u', help="ElasticSearch username", type=str, default='elastic', required=False)
    parser.add_argument('--password', '-pw', help="ElasticSearch username's password", type=str, default='changeme', required=False)

    args = parser.parse_args()
    print(args)
    download_json(**vars(args))
    return 'Get data from Elasticsearch'

@app.route('/elastic', methods=['POST'])
def upload():
    parser = argparse.ArgumentParser(description='Download elastic search last X minutes on an index')
    parser.add_argument('--path', '-o', help='JSON output path', type=str, default="../elastic.json", required=False)
    parser.add_argument('--index', '-i', help="ElasticSearch index", type=str, default='metricbeat-*', required=False)
    parser.add_argument('--lastMinutes', '-m', help="Last minutes to get data for", dest='last_minutes', type=int, default=5, required=False)
    parser.add_argument('--host', '-a', help="ElasticSearch Host's ip/address", type=str, default='elastic.monitor.net', required=False)
    parser.add_argument('--port', '-p', help="ElasticSearch Host's port", type=int, default=9200, required=False)
    parser.add_argument('--user', '-u', help="ElasticSearch username", type=str, default='elastic', required=False)
    parser.add_argument('--password', '-pw', help="ElasticSearch username's password", type=str, default='changeme', required=False)

    args = parser.parse_args()
    print(args)
    download_json(**vars(args))
    return 'Get data from Elasticsearch'

@app.errorhandler(404)
def not_found(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def not_found(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)
