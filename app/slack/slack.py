import json
import logging
import requests

from app.config import Config

cfg = Config.get_instance().cfg
logger = logging.getLogger(__name__)


def send_to_slack(webhook, data, user, icon):
    if isinstance(data, str):
        data = {"text": data, "username": user, "icon_emoji": icon}
    data = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook, data=data, headers=headers)
    if response.status_code != 200:
        raise ValueError('Request to slack returned an error {}, the response is:\n{}'
                         .format(response.status_code, response.text))
