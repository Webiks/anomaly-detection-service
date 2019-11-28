import logging
from app.config import Config
from datetime import datetime
from elasticsearch_dsl import Document, Date, Text

cfg = Config.get_instance().cfg
logger = logging.getLogger(__name__)


class Anomaly(Document):
    d = {}
    host = Text(analyzer='snowball')
    event_time = Date(default_timezone='UTC')
    source = Text()
    timestamp = Date(default_timezone='UTC')

    class Index:
        name = cfg.anomaly_index.name
        settings = cfg.anomaly_index.settings

    logger.debug(f'Index class: {Index.name}, {Index.settings}', extra=d)

    def save(self, ** kwargs):
        return super(Anomaly, self).save(** kwargs)

    def is_published(self):
        return datetime.now() > self.timestamp
