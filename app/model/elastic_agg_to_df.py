import pandas as pd
import json
from elasticsearch_dsl.utils import AttrDict, AttrList

keys_to_ignore = ['key', 'key_as_string', 'doc_count', 'doc_count_error_upper_bound']


def process_row(time, row):
    host = row['key']
    row_data = {'time': time, 'host': host}
    keys = [x for x in row if x not in keys_to_ignore]
    if len(keys) == 1 and 'buckets' in row[keys[0]]:
        print(f'found bucket key: {keys[0]}')
        row_data
    for key in keys:
        for value in row[key]:
            if isinstance(row[key][value], AttrDict): continue
            if isinstance(row[key][value], AttrList):
                for item in row[key][value]:
                    row_data[f"{key}_{item['key']}"] = item['value']
            else:
                row_data[key + '_' + value] = row[key][value]
    return row_data


def process_time_bucket(time_bucket, hosts_key):
    time = time_bucket['key']
    bucket_data = time_bucket[hosts_key]['buckets']
    rows = [process_row(time, x) for x in bucket_data]
    return rows


def build_aggregation_dataframe(x, time_key='2', hosts_key='3'):
    time_buckets = x['aggregations'][time_key]['buckets']
    rows = [process_time_bucket(x, hosts_key) for x in time_buckets]
    flat_rows = [y for x in rows for y in x]
    df = pd.DataFrame(flat_rows)
    return df


def get_bucket(row):
    keys = [x for x in row if x not in keys_to_ignore]
    is_bucket = len(keys) == 1 and 'buckets' in row[keys[0]]
    bucket_key = keys[0] if is_bucket else None
    return is_bucket, bucket_key


def format_key(key):
    if isinstance(key, float):
        key = int(key)
    return key


def process_generic_row(rows, node, bucket_key=None, row_data=None, count_fields=None, extended_fields=None):
    if row_data is None:
        row_data = {}
    if bucket_key:
        row_data[bucket_key] = node['key']
    keys = [x for x in node if x not in keys_to_ignore]
    for key in keys:
        key_extended_fields = []
        is_extended = extended_fields and key in extended_fields
        if is_extended:
            key_extended_fields = extended_fields[key]
        for value in node[key]:
            value_name = value
            if value_name == "std_deviation":
                value_name = "std"
            if is_extended and value_name not in key_extended_fields: continue
            if isinstance(node[key][value], AttrDict) or isinstance(node[key][value], dict): continue
            if isinstance(node[key][value], AttrList) or isinstance(node[key][value], list):
                if len(node[key][value]) == 1:
                    item = node[key][value][0]
                    row_data[key] = item['value']
                else:
                    for item in node[key][value]:
                        row_data[f"{key}_{format_key(item['key'])}"] = item['value']
            else:
                row_data[key + '_' + value_name] = node[key][value]
    if count_fields:
        for field in count_fields:
            row_data[field] = node['doc_count']
    rows.append(row_data)


def build_generic_bucket(rows, list, bucket_key, row_data=None, count_fields=None, extended_fields=None):
    for node in list:
        node_row_data = {} if row_data is None else row_data.copy()
        node_row_data[bucket_key] = node['key']
        is_bucket, inner_bucket_key = get_bucket(node)
        if is_bucket:
            build_generic_bucket(rows, node[inner_bucket_key]['buckets'],
                                 inner_bucket_key, node_row_data, count_fields, extended_fields)
        else:
            process_generic_row(rows, node, inner_bucket_key, node_row_data, count_fields, extended_fields)


def build_generic_aggregations_dataframe(x, count_fields, extended_fields):
    rows = []
    node = x['aggregations']
    is_bucket, bucket_key = get_bucket(node)
    build_generic_bucket(rows, node[bucket_key]['buckets'], bucket_key,
                         count_fields=count_fields, extended_fields=extended_fields)
    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    x = json.load(open(r'C:\Users\Tsabar\Documents\projects\anomaly sapir\try\try_elastic.json'))
    # df = build_aggregation_dataframe(x)
    # time_temp=pd.to_datetime(df['time']*1000000)
    print(build_generic_aggregations_dataframe(x))
