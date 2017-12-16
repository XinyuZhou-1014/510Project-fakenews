import numpy as np
import lightgbm as lgb
from baseline.utils.system import check_version
from baseline.utils.dataset import DataSet
from train_engine import generate_features, pretrain_lda


# setup lightGBM
model_file = "lgbm_res"
params = {
    'task': 'train',
    'boosting_type': 'gbdt',
    'objective': 'multiclass',
    'metric': 'multi_logloss',
    'num_class': 4,
    'is_training_metric': True,
    'num_leaves': 31,
    'feature_fraction': 0.9,
    'num_trees': 200,
    'verbose': 1
}


if __name__ == "__main__":
    # if run directly, train on train_data and test on test_data to get score
    check_version()  # only support Python 3

    #Load datasets
    train_dataset = DataSet()
    test_dataset = DataSet("competition_test")

    pretrain_lda(train_dataset, test_dataset)

    # generate features
    X_train, y_train = generate_features(train_dataset, "train")
    X_test, y_test = generate_features(test_dataset, "test")

    # concat train and test to train model with full data
    X_all = np.concatenate((X_train, X_test), axis=0)
    y_all = np.concatenate((y_train, y_test), axis=0)

    # train lightGBM and save
    lgb_model = lgb.train(params, lgb.Dataset(X_all, y_all))
    lgb_model.save_model('fakenews_models/%s.txt' % model_file)
    print("model saved at fakenews_models/%s.txt" % model_file)