import json

Features_Dict = {
    'epoc': ['count', 'average', 'iqr', 'std', 'sum']
    , 'event.duration': ['average', 'iqr', 'percentile_90', 'std', 'sum']
    , 'metricset.period': ['average', 'median', 'percentile_90', 'std', 'sum']
    , 'system.cpu.cores': ['sum']
    , 'system.cpu.idle.pct': ['std', 'sum']
    , 'system.cpu.iowait.pct': ['percentile_25', 'sum']
    , 'system.cpu.softirq.pct': ['median', 'percentile_25', 'percentile_75', 'sum']
    , 'system.cpu.steal.pct': ['iqr', 'std', 'sum']
    , 'system.cpu.system.pct': ['iqr', 'std', 'sum']
    , 'system.cpu.total.pct': ['iqr', 'std']
    , 'system.cpu.user.pct': ['percentile_25', 'std', 'sum']
    , 'system.filesystem.available': ['average', 'std', 'sum']
    , 'system.filesystem.free': ['std']
    , 'system.filesystem.used.bytes': ['sum']
    , 'system.fsstat.count': ['average', 'sum']
    , 'system.memory.actual.free': ['iqr', 'std', 'sum']
    , 'system.memory.actual.used.bytes': ['sum']
    , 'system.memory.free': ['iqr', 'std']
    , 'system.network.in.bytes': ['average', 'percentile_25', 'sum']
    , 'system.network.in.packets': ['sum']
    , 'system.socket.summary.all.count': ['iqr', 'std']
}

buckets_order = ['@timestamp','host.name.keyword', 'city.keyword','neighborhood.keyword', 'branch', 'title.keyword']
buckets_Dict = {'@timestamp':'timestamp','host.name.keyword':'host', 'city.keyword':'city','neighborhood.keyword':'neighborhood', 'branch': 'branch', 'title.keyword':'title'}

options = { 'features': Features_Dict, 'buckets': { 'order': buckets_order, 'names': buckets_Dict } }

with open(r'C:\Users\Tsabar\PycharmProjects\monitor\options.json', 'w') as file:
    file.write(json.dumps(options)) 
    