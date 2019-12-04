import json
import yaml
import logging.config

from app.utils import dotdict
from app.utils.env_to_json import override


class TraceIdFilter(logging.Filter):
    def filter(self, rec):
        if 'trace' not in rec.__dict__:
            rec.trace = 'N/A'
        return True


class Config:
    __instance = None

    @staticmethod
    def get_instance():
        # Static access method.
        if Config.__instance is None:
            Config()
        return Config.__instance

    def __init__(self):
        # Virtually private constructor.
        if Config.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            try:
                Config.__instance = self
                with open('./data/config.json') as json_file:
                    self.config = override(json.load(json_file))
                    self.cfg = dotdict.dotdict(self.config)

                with open(self.cfg.logging.yaml, 'r') as yml:
                    conf = yaml.safe_load(yml.read())
                    logging.config.dictConfig(conf)
            except Exception as ex:
                raise Exception(f'Can\"t load one or more configuration files')
