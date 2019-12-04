import os
import re
import datetime as dt
from joblib import dump
from math import pi

import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.ensemble import IsolationForest as IF
from sklearn.decomposition import PCA
# from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

from get_data import get_data

# TODO setting agent hostname & creating hardware_fingerprint based on that -
# in the future hardwarefingerprint need to be based on actual hardware difference
###################################################################
###################################################################
#######################   Functions    ############################
###################################################################
###################################################################


def remove_illegal_path_chars(path):
    return re.sub(r'[\\/\:*"<>\|\.%\$\^&£]', '', path)


def get_iso_date(date):
    return dt.datetime.strftime(date, '%Y-%m-%dT%H:%M:%SZ')


def get_long_input(from_time, to_time, save_to_file=True, load_from_file=True, base_path=None):
    time_range = pd.date_range(from_time, to_time, freq='1H', closed=None)
    dfs = []
    for i in range(0, len(time_range) - 1):
        start_time = time_range[i]
        end_time = time_range[i + 1]
        print(f'from {start_time} to {end_time}')
        X = get_input(get_iso_date(start_time), get_iso_date(end_time), save_to_file, load_from_file, base_path)
        if X is not None:
            dfs.append(X)
    df = pd.concat(dfs)
    return df


def get_input(from_time, to_time, save_to_file=True, load_from_file=True, base_path=None):
    file_path = f'train_{remove_illegal_path_chars(from_time)}_{remove_illegal_path_chars(to_time)}.json'
    full_path = os.path.join(base_path, file_path) if base_path else file_path
    if load_from_file and os.path.exists(full_path):
        print('Loading data from file')
        X = pd.read_json(full_path)
    else:
        print('Getting data from elasticsearch')
        X = get_data(host="elastic.monitor.net", from_time=from_time, to_time=to_time)
        if X is not None:
            X['timestamp'] = X['timestamp'].astype('int64') * 1000000
            X['timestamp'] = pd.to_datetime(X['timestamp'])
            if save_to_file:
                X.to_json(full_path)

    return X


def add_features_n_NA(data):
    data = data.fillna(0)

    data['host'] = data['host'].str.replace('comp', '')
    data['host'] = data['host'].astype(int)

    # data['timestamp'] = data['timestamp'].astype('int64') * 1000000
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['hour'] = data.timestamp.dt.hour
    data['day'] = (data['hour'] < 13) * 1
    return data


# def hardware_fingerprint(data):
#     data['hardware_fingerprint'] = np.nan
#     df_num_new['hardware_fingerprint'] = df_num_new[['hardware_fingerprint']].apply(lambda col: le.fit_transform(col))
#     data['hardware_fingerprint'] = data['system.cpu.cores_mean'].astype(str) + '_' + data[
#         'system.fsstat.total_size.total_mean'].astype(str) \
#                                    + '_' + data['system.filesystem.total_mean'].astype(str) + data[
#                                        'system.memory.total_mean'].astype(str)
#     data['hardware_fingerprint'] = data['hardware_fingerprint'].astype(int)
#     return data


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


def drop_constant(df):
    # X=pd.DataFrame()
    data = df.fillna(0, inplace=True)
    data = data.loc[:, (data != data.iloc[0]).any()]
    return data


def drop_colinearity(df, auto_corelation=0.9):
    X = df
    corr_matrix = X.corr().abs()
    # Select upper triangle of correlation matrix
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))
    # Find index of feature columns with correlation greater than 0.9
    to_drop = [column for column in upper.columns if any(upper[column] > auto_corelation)]
    # Drop features
    X.drop(X[to_drop], axis=1, inplace=True)
    return X


# model function
def all_but_timestamp(data):
    return data.loc[:, data.columns != 'timestamp']


def model_isof(data, behaviour='new', max_samples=2500, max_features=20, bootstrap=True, random_state=42,
               contamination=0.005, verbose=0):
    model = IF(behaviour=behaviour, max_samples=max_samples, max_features=max_features, bootstrap= bootstrap, random_state=random_state, contamination=contamination,
               verbose=verbose)
    model.fit(all_but_timestamp(data))
    return model


def predict(model, data):
    y_pred = model.predict(all_but_timestamp(data))
    metrics_df = pd.DataFrame()
    metrics_df['anomaly'] = y_pred
    outliers = metrics_df.loc[metrics_df['anomaly'] == -1]
    outlier_index = list(outliers.index)
    anomaly_table=data[['host', 'timestamp']].iloc[outlier_index]
    return y_pred, outlier_index, anomaly_table


def save_model(model, output_path):
    dump(model, output_path)


def save_anomalies(model, data, outlier_index, path='anomalies.csv'):
    data.iloc[model[outlier_index]].to_csv(path)


def pca_3d_components(data):
    pca = PCA(n_components=3)  # Reduce to k=3 dimensions
    scaler = preprocessing.StandardScaler()
    # normalize the metrics
    df = scaler.fit_transform(all_but_timestamp(data))
    X_PCA = pca.fit_transform(df)
    return X_PCA


def pca_3d_plot(train, test, outlier_index):
    X = pd.concat([test, train])
    data_pca = pca_3d_components(X)
    plt.clf()
    plt.close()
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel("x_composite_1")
    ax.set_ylabel("x_composite_2")
    ax.set_zlabel("x_composite_3")
    # Plot the compressed data points
    ax.scatter(data_pca[:int(len(train.index)), 0], data_pca[:int(len(train.index)), 1], zs=data_pca[:int(len(train.index)), 2], s=10, lw=1, label="Train inliers", c="green")
    ax.scatter(data_pca[int(len(train.index)):, 0], data_pca[int(len(train.index)):, 1], zs=data_pca[int(len(train.index)):, 2], s=100, lw=1, label="Test inliers", c="blue")
    # Plot x's for the ground truth outliers
    ax.scatter(data_pca[outlier_index, 0], data_pca[outlier_index, 1], data_pca[outlier_index, 2], lw=2, s=80,
               marker="x", c="red", label="Test outliers", alpha=0.5)

    ax.legend()
    plt.show()


def export_PCA(export_data, data_name='export_data_aws_comp20.csv'):
    export_data.to_csv(data_name)


# def find_normal_neighbour(data):
#     nbrs = NearestNeighbors(n_neighbors=3, algorithm='ball_tree').fit(data)
#     distances, indices = nbrs.kneighbors(data)
#     return list(indices)
#
#
# for i in len(find_normal_neighbour(train)):
#     for j in len(i):
#         print(j)
#         # if (j==1)
#         print(i)


def radar_chart(pca_data, anomaly_index, normal_index):
    mms = preprocessing.MinMaxScaler()
    df = mms.fit_transform(pca_data)
    df = pd.DataFrame(df)

    # number of variable
    categories = list(df)
    N = len(categories)

    # We are going to plot the first line of the data frame.
    # But we need to repeat the first value to close the circular graph:
    # values=df.loc[0].drop('group').values.flatten().tolist()
    # values1=df.loc[106].drop('group').values.flatten().tolist()
    values = df.loc[normal_index].values.flatten().tolist()
    values1 = df.loc[anomaly_index].values.flatten().tolist()
    values += values[:1]
    values1 += values1[:1]

    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    print(angles, float(N))
    # Initialise the spider plot
    plt.figure(figsize=(10, 20))
    ax = plt.subplot(111, polar=True)

    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], categories, color='grey', size=8)

    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([0.1, 0.3, 0.5, 0.7, 1], ["0.1", "0.3", "0.5", "0.7", "1.0"], color="grey", size=7)
    plt.ylim(0, 1)

    # Plot data
    ax.plot(angles, values, linewidth=1, linestyle='solid')
    ax.plot(angles, values1, linewidth=1, linestyle='solid')
    # Fill area
    ax.fill(angles, values, 'b', alpha=0.1)
    ax.fill(angles, values1, 'r', alpha=0.1)

    plt.show()


def generate_and_test_model():
    print('Getting train data...')
    train = get_long_input(from_time='2019-11-17T08:00:00.000Z', to_time='2019-11-18T22:00:00.000Z')
    print('Preparing data for model...')
    le = {}
    train = add_features_n_NA(train)
    convert_categorical_to_int(train, le)

    print('Training model...')
    isof = model_isof(train, contamination=0.001)
    save_model(isof, 'model_V0.clf')

    print('Predicting on train set...')
    train_pred,train_outlier,train_table=predict(isof,train)

    print('Getting test data...')
    # test = get_input(from_time='2019-11-19T10:00:00.000Z', to_time='2019-11-19T10:10:00.000Z', save_to_file=False)
    test = get_input(from_time='now-1d', to_time='now', save_to_file=False)
    test = add_features_n_NA(test)
    convert_categorical_to_int(test, le, False)
    print('Predicting on test set...')
    test_pred, test_outlier, test_table = predict(isof, test)

    test_table['host']= ('Comp_') + test_table['host'].astype(str)
    print(test.timestamp.head(10))

    print('Anomalies:')
    print(test_table)

    X=pd.concat([test, train])
    paint_test=len(test.index)
    X_PCA = pca_3d_components(X)
    pca_3d_plot(train,test, test_outlier)

    # X_PCA.components_
    # X_PCA.explained_variance_


    #
    # data_scaled = pd.DataFrame(preprocessing.scale(train), columns=train.columns)
    # data_scaled.head(10)
    # pca = PCA(n_components=3)
    # pca.fit_transform(data_scaled)
    # export_data = pd.DataFrame(pca.components_, columns=data_scaled.columns, index=['PC-1', 'PC-2', 'PC-3'])
    # # exporting PCA components
    # # from google.colab import files
    #
    #
    # print(pca.explained_variance_ratio_)

if __name__=="__main__":
    generate_and_test_model()
