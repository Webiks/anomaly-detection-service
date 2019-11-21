import json
import requests


# https://worspace.slack.com/services/new/incoming-webhook/
def send_to_slack(webhook_url, data, user, icon):
    if isinstance(data, str):
        data = {"text": data, "username": user, "icon_emoji": icon}
    data = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, data=data, headers=headers)
    if response.status_code != 200:
        raise ValueError('Request to slack returned an error {}, the response is:\n{}'
                         .format(response.status_code, response.text))


# if __name__ == "__main__":
#     try:
    #     webhook_url = 'https://hooks.slack.com/services/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'
    #     data = "hello from python"
    #     send_to_slack(webhook_url, data)
    #     print('sent to slack')
    # except Exception as ex:
    #     print('failed to send to slack')
    #     print(ex)