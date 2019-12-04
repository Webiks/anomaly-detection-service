import argparse
import logging
import pandas as pd

import elasticsearch
import elasticsearch_dsl

from app.config import Config
from app.model.elastic_agg_to_df import build_generic_aggregations_dataframe

cfg = Config.get_instance().cfg
logger = logging.getLogger(__name__)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def get_hit_dict(hit):
    hit_dict = hit.to_dict()
    hit_dict.update(hit.meta.to_dict())
    return hit_dict


def get_display_name(value, options):
    return options['buckets']['names'][value] if value in options['buckets']['names'] else value


def build_buckets(aggs, options):
    size = options['maxRowsPerAggregation']
    for bucket in options['buckets']['order']:
        aggs = aggs.bucket(get_display_name(bucket, options), 'terms', field=bucket, size=size)
    return aggs


def build_metrics(aggs, options):
    count_fields = []
    extended_fields = {}
    iqr_fields = []
    for metric in options['metrics']:
        percentiles = []
        for stat in options['metrics'][metric]:
            if stat == 'iqr':
                iqr_field = f"{get_display_name(metric, options)}_iqr"
                iqr_fields.append(iqr_field)
                aggs.metric(iqr_field, 'percentiles',
                            field=metric, percents=[25, 75], keyed=False)
            elif stat in ["std", "count", "sum", "sum_of_squares", "variance"]:
                if metric not in extended_fields:
                    extended_fields[metric] = []
                    aggs.metric(get_display_name(metric, options), 'extended_stats', field=metric)
                extended_fields[metric].append(stat)
            elif stat == 'doc_count':
                count_fields.append(f"{get_display_name(metric, options)}_count")
            elif stat == 'average':
                aggs.metric(f"{get_display_name(metric, options)}_{stat}", 'avg', field=metric)
            elif stat == 'median':
                aggs.metric(f"{get_display_name(metric, options)}_{stat}", 'percentiles',
                            field=metric, percents=50, keyed=False)
            elif stat.startswith('percentile_'):
                percentiles.append(int(stat.split('_')[-1]))
            else:
                aggs.metric(f"{get_display_name(metric, options)}_{stat}", stat, field=metric)
        percentiles_size = len(percentiles)
        if percentiles_size == 1:
            aggs.metric(f"{get_display_name(metric, options)}_percentile_{percentiles[0]}", 'percentiles',
                        field=metric, percents=percentiles, keyed=False)
        if percentiles_size > 1:
            aggs.metric(f"{get_display_name(metric, options)}_percentile", 'percentiles',
                        field=metric, percents=percentiles, keyed=False)
    return count_fields, extended_fields, iqr_fields


def build_query(search, index, from_time, to_time, options):
    time_key = options['time']['field']
    time_interval = options['time']['interval']
    time_query = {
        time_key: {
            "format": "strict_date_optional_time",
            "gte": from_time,
            "lt": to_time
        }
    }
    search = search.index(index)
    search = search.query('range', **time_query)
    aggs = search.aggs.bucket(get_display_name(time_key, options), 'date_histogram',
                              field=time_key, interval=time_interval)
    aggs = build_buckets(aggs, options)
    count_fields, extended_fields, iqr_fields = build_metrics(aggs, options)
    return search, count_fields, extended_fields, iqr_fields


def calculate_iqr_fields(df, iqr_fields):
    remove_columns = []
    for x in iqr_fields:
        df[x] = df.apply(lambda row: row[x + "_75"] - row[x + "_25"], axis=1)
        remove_columns.append(x + "_25")
        remove_columns.append(x + "_75")
    df = df.drop(remove_columns, axis=1)
    return df


# def get_data(index='metricbeat-*', from_time='now-5m', to_time='now', host='localhost',
#              port='9200', user='elastic', password='changeme', options='./options.json'):
def get_data(index, from_time, to_time, host, port, user, password, options, traceId='N/A'):

    """
    Get aggregated data from elasticsearch
    :param index: Index to read from
    :param from_time: Query from time, e.g. "now-5m", "2019-11-17T10:00:00.000Z", etc.
    :param to_time: Query to time, e.g. "now", "2019-11-17T11:00:00.000Z", etc.
    :param host: ElasticSearch host name
    :param port: ElasticSearch port number
    :param user: ElasticSearch user
    :param password: ElasticSearch password
    :param options: Options object, contains the aggregations and metrics (see options.json)
    :param traceId: a uuid for tracing the thread
    :return: DataFrame with aggregated data
    """
    d = {'traceId': traceId}
    try:
        hosts = [{"host": host, "port": port}]
        http_auth = (user, password)

        elastic_client = elasticsearch.Elasticsearch(hosts=hosts, http_auth=http_auth)
        logger.debug(f'Elastic Client: {elastic_client}', extra=d)

        search = elasticsearch_dsl.Search(using=elastic_client)
        logger.debug(f'Elastic Search: {search.query}', extra=d)

        search, count_fields, extended_fields, iqr_fields = build_query(search, index, from_time, to_time, options)
        response = search.execute()
        logger.debug(f'Elastic Response: {response.aggregations}', extra=d)

        if len(response.aggregations.timestamp.buckets) == 0:
            return None
        df = build_generic_aggregations_dataframe(response, count_fields, extended_fields)
        if iqr_fields and len(iqr_fields) > 0:
            df = calculate_iqr_fields(df, iqr_fields)
        return df

    except elasticsearch.ElasticsearchException as es:
        logger.error(es)

    except Exception as ex:
        logger.error(ex)


def download_json(path, index, last_minutes, host, port, user, password, options):
    from_time = f"now-{last_minutes}m"
    to_time = "now"
    df = get_data(index, from_time, to_time, host, port, user, password, options)
    print(df.head(10))
    print(df.shape)
    df.to_json(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download elastic search last X minutes on an index')
    parser.add_argument('--path', '-o', help='JSON output path', type=str, default="data.json", required=False)
    parser.add_argument('--index', '-i', help="ElasticSearch index", type=str, default='metricbeat-*', required=False)
    parser.add_argument('--lastMinutes', '-m', help="Last minutes to get data for", dest='last_minutes', type=int, default=120, required=False)
    parser.add_argument('--host', '-a', help="ElasticSearch Host's ip/address", type=str, default='elastic.monitor.net', required=False)
    parser.add_argument('--port', '-p', help="ElasticSearch Host's port", type=int, default=9200, required=False)
    parser.add_argument('--user', '-u', help="ElasticSearch username", type=str, default='elastic', required=False)
    parser.add_argument('--password', '-pw', help="ElasticSearch username's password", type=str, default='changeme', required=False)
    parser.add_argument('--options', '-opt', help="Aggregations options", type=str, default="./options.json", required=False)

    args = parser.parse_args()
    print(args)
    download_json(**vars(args))
