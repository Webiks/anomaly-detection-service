import json
import os
from dotenv import load_dotenv
from flask import Flask

app = Flask(__name__)

load_dotenv()
app.webhook_url = os.getenv("WEBHOOKURL")

with open('config.json') as config:
    cfg = json.load(config)
app.port = cfg['port']
app.icon = cfg['icon']
app.user = cfg['username']

from app import routes
