import json
from app.utils import dotdict


class Config:
    __instance = None
    with open('./data/config.json') as config:
        cfg = dotdict.dotdict(json.load(config))

    @staticmethod
    def getInstance():
        # Static access method.
        if Config.__instance is None:
            Config()
        return Config.__instance

    def __init__(self):
        # Virtually private constructor.
        if Config.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Config.__instance = self
