import numpy as np
from joblib import load


def load_model(path):
    clf = load(path)
    return clf


def predict(clf):
    rng = np.random.RandomState(42)
    X = 0.3 * rng.randn(100, 2)
    X = 0.3 * rng.randn(20, 2)
    X_test = np.r_[X + 2, X - 2]
    y_pred_test = clf.predict(X_test)
    return y_pred_test


if __name__ == "__main__":
    print('Loading model from disk...')
    model = load_model('./isolation-forest-demo.clf')
    print('Loading previously predicted data for comparison...')
    y_pred_org = load('./y_pred.dat')
    print('Predicting same data on loaded model...')
    y_pred_new = predict(model)
    print('Comparing predictions...')
    is_same = False
    comparision = y_pred_org == y_pred_new
    if comparision is not False:
        is_same = len([x for x in comparision if not x]) == 0
    print('Data is the same: {}'.format(is_same))
