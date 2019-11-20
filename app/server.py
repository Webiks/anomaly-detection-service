import os
import json
import argparse
from dotenv import load_dotenv
from app.slack.slack import send_to_slack
from app.elastic.elasticpy import download_json
from flask import Flask, make_response, jsonify, request

load_dotenv()
webhook_url = os.getenv("WEBHOOKURL")

with open('config.json') as config:
    cfg = json.load(config)
port = cfg['port']
icon = cfg['icon']
user = cfg['username']

app = Flask(__name__)


@app.route('/health')
def health():
    return 'Server is up & running'


@app.route('/slack', methods=['POST', 'GET'])
def parse_request():
    data = request.form['payload']
    send_to_slack(webhook_url, data, user, icon)
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
    return make_response(jsonify({'error': 'Not found'}), 404)


app.run(host='0.0.0.0', port=port, debug=True)
