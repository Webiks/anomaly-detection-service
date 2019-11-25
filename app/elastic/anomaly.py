import logging
from app.config import Config
from datetime import datetime
from elasticsearch_dsl import Document, Date, Text

cfg = Config.getInstance().cfg
logger = logging.getLogger(__name__)


class Anomaly(Document):
    host = Text(analyzer='snowball')
    event_time = Date(default_timezone='UTC')
    source = Text()
    timestamp = Date(default_timezone='UTC')

    class Index:
        name = cfg.anomaly_index.name
        settings = cfg.anomaly_index.settings

    logger.debug('Index class: {}, {}' .format(Index.name, Index.settings))

    def save(self, ** kwargs):
        return super(Anomaly, self).save(** kwargs)

    def is_published(self):
        return datetime.now() > self.timestamp
