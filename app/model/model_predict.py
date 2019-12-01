import os
import re
import logging

import pandas as pd

from joblib import load
from sklearn import preprocessing
from app.model.get_data import get_data as get_elastic_data

d = {}
# model function
le = {}
host_name_prefix = 'comp'
logger = logging.getLogger(__name__)


def load_model(path):
    try:
        clf = load(path)
        return clf
    except Exception as e:
        logger.error(e, expert=d)


def remove_illegal_path_chars(path):
    return re.sub(r'[\\/\:*"<>\|\.%\$\^&£]', '', path)


def get_input(traceId, index, from_time, to_time, host, port, user, password,
              options, save_to_file=True, load_from_file=True, base_path=None):
    d = {'trace': traceId}
    file_path = f'train_{remove_illegal_path_chars(from_time)}_{remove_illegal_path_chars(to_time)}.json'
    full_path = os.path.join(base_path, file_path) if base_path else file_path
    if load_from_file and os.path.exists(full_path):
        logger.info(f' Loading data from file...', extra=d)
        X = pd.read_json(full_path)
    else:
        logger.info(f'Getting data from elasticsearch...', extra=d)
        logger.debug(f'Getting data from elasticsearch with index: {index} from_time: {from_time} '
                     f'to_time: {to_time} host: {host} port: {port} '
                     f'user: {user} password: ******** and options {options}', extra=d)
        X = get_elastic_data(index, from_time, to_time, host, port, user, password, options)
        if X is not None:
            X['timestamp'] = X['timestamp'].astype('int64') * 1000000
            if save_to_file:
                X.to_json(full_path)

    return X


def all_but_timestamp(data):
    return data.loc[:, data.columns != 'timestamp']


def add_features_n_NA(data):
    data = data.fillna(0)

    data['host'] = data['host'].str.replace(host_name_prefix, '')
    data['host'] = data['host'].astype(int)

    # data['timestamp'] = data['timestamp'].astype('int64') * 1000000
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['hour'] = data.timestamp.dt.hour
    data['day'] = (data['hour'] < 13) * 1
    return data


def fit_label_encoder(le, col):
    label_encoder = preprocessing.LabelEncoder()
    labels = label_encoder.fit_transform(col)
    le[col.name] = label_encoder
    return labels


def convert_categorical_to_int(data, le, train_le=True):
    categorical_feature_mask = data.dtypes == object
    categorical_cols = data.columns[categorical_feature_mask].tolist()
    data[categorical_cols] = data[categorical_cols].apply(
        lambda col: fit_label_encoder(le, col) if train_le else le[col.name].transform(col))
    data[categorical_cols] = data[categorical_cols].astype(int)


def get_data(traceId, index, from_time, to_time, host, port, user, password, options):
    d = {'trace': traceId}
    logger.debug(f'Get data with index: {index} from: {from_time} to: {to_time} '
                 f'host: {host} port: {port} user: {user} password: ******** and options: {options}', extra=d)
    data = get_input(traceId, index, from_time, to_time, host, port, user,
                     password, options, save_to_file=False, load_from_file=False)
    if data is not None:
        data = add_features_n_NA(data)
        convert_categorical_to_int(data, le, True)  # TODO solve categorical indexing mismatch with training (ok for demo)
    return data


def predict(model, data):
    y_pred = model.predict(all_but_timestamp(data))
    metrics_df = pd.DataFrame()
    metrics_df['anomaly'] = y_pred
    outliers = metrics_df.loc[metrics_df['anomaly'] == -1]
    outlier_index = list(outliers.index)
    anomaly_table=data[['host', 'timestamp']].iloc[outlier_index]
    anomaly_table['host'] = host_name_prefix + anomaly_table['host'].astype(str)
    return y_pred, outlier_index, anomaly_table
