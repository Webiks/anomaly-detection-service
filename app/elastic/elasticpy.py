import json
import argparse
from elasticsearch import Elasticsearch


def download_json(path, index, last_minutes, host, port, user, password):
    hosts = [{"host": host, "port": port}]
    http_auth = (user, password)
    elastic_client = Elasticsearch(hosts=hosts, http_auth=http_auth)

    query = {
        "query": {
            "range": {
                "@timestamp": {
                    "gte": "now-{0}m".format(last_minutes),
                    "lt": "now"
                }
            }
        },
        "size": 0
    }

    response = elastic_client.search(
        index=index,
        body=query
    )
    total = response["hits"]["total"]["value"]
    print("Total hits: {0}, downloading...".format(total))

    query["size"] = total
    response = elastic_client.search(
        index=index,
        body=query
    )
    with open(path, 'w') as f:
        json.dump(response, f)
    print('done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download elastic search last X minutes on an index')
    parser.add_argument('--path', '-o', help='JSON output path', type=str, default="elastic.json", required=False)
    parser.add_argument('--index', '-i', help="ElasticSearch index", type=str, default='metricbeat-*', required=False)
    parser.add_argument('--lastMinutes', '-m', help="Last minutes to get data for", dest='last_minutes', type=int, default=5, required=False)
    parser.add_argument('--host', '-a', help="ElasticSearch Host's ip/address", type=str, default='elastic.monitor.net', required=False)
    parser.add_argument('--port', '-p', help="ElasticSearch Host's port", type=int, default=9200, required=False)
    parser.add_argument('--user', '-u', help="ElasticSearch username", type=str, default='elastic', required=False)
    parser.add_argument('--password', '-pw', help="ElasticSearch username's password", type=str, default='changeme', required=False)

    args = parser.parse_args()
    print(args)
    download_json(**vars(args))