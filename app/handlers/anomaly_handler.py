import logging
from app.config import Config
from datetime import datetime
from app.elastic.anomaly import Anomaly
from elasticsearch_dsl import connections

cfg = Config.getInstance().cfg
logger = logging.getLogger(__name__)

hosts = [cfg.elasticsearch]
logger.debug('Host: {}' .format(hosts))

http_auth = (cfg.elastic_auth.un, cfg.elastic_auth.pw)
logger.debug('http_auth: {}' .format(http_auth))

connections.create_connection(hosts=hosts, http_auth=http_auth)


predicts = {
    'host': 'Comp_20',
    'time': datetime.now(),
    'source': 'anomaly defecation model'
}


def publish_anomaly():

    Anomaly.init()

    logger.debug(predicts)
    anomaly = Anomaly(host=predicts.get('host'),
                      event_time=predicts.get('time'), source=predicts.get('source'), timestamp=datetime.now())
    anomaly.save()

    # anomaly = Anomaly.get(id=142)
    # logger.info(anomaly.is_published())
    # logger.debug(anomaly)
    #
    # # Display cluster health
    # logger.debug(connections.get_connection().cluster.health())
