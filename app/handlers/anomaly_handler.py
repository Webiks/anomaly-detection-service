import logging

from datetime import datetime

from app.config import Config
from app.elastic.anomaly import Anomaly
from elasticsearch_dsl import connections
from elasticsearch.helpers import bulk

cfg = Config.get_instance().cfg
logger = logging.getLogger(__name__)

hosts = [cfg.elasticsearch]
http_auth = (cfg.elasticsearch.username, cfg.elasticsearch.password)
connections.create_connection(hosts=hosts, http_auth=http_auth)


def publish_anomalies(traceId, anomalies):
    d = {'trace': traceId}
    try:
        connection = connections.get_connection()
        documents = [Anomaly(host=row.host, event_time=row.timestamp, source=cfg.model.name,
                             timestamp=datetime.utcnow()).to_dict(True) for index, row in anomalies.iterrows()]

        logger.debug(f'Bulk inset of documents {documents}', extra=d)

        if len(documents) > 0:
            bulk(connection, documents)

    except Exception as e:
        logger.error(e, extra=d)

