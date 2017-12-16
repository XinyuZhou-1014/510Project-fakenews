import numpy as np
import os

from baseline.feature_engineering import refuting_features, polarity_features
from baseline.feature_engineering import hand_features, gen_or_load_feats
from baseline.feature_engineering import word_overlap_features
from baseline.utils.dataset import DataSet
from baseline.utils.score import report_score, LABELS
from baseline.utils.system import check_version

import lightgbm as lgb
from feature_word2vec import word2vec_pooling_features
from feature_lda import lda_train_and_save, lda_load_and_transform


# setup lightGBM
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


def get_hby_from_dataset(dataset):
    # h: headlines, b: bodies, y: index_of_labels
    h, b, y = [],[],[]

    for stance in dataset.stances:
        y.append(LABELS.index(stance['Stance']))
        h.append(stance['Headline'])
        b.append(dataset.articles[stance['Body ID']])
    return {"h": h, "b": b, "y": y}


def generate_features(dataset,name):
    data = get_hby_from_dataset(dataset)
    h, b, y = data["h"], data["b"], data["y"]

    X_overlap = gen_or_load_feats(word_overlap_features, h, b, "features/overlap."+name+".npy")
    X_refuting = gen_or_load_feats(refuting_features, h, b, "features/refuting."+name+".npy")
    X_polarity = gen_or_load_feats(polarity_features, h, b, "features/polarity."+name+".npy")
    X_hand = gen_or_load_feats(hand_features, h, b, "features/hand."+name+".npy")
    X_word2vec = gen_or_load_feats(word2vec_pooling_features, h, b, "features/word2vec."+name+".npy")
    X_lda = lda_load_and_transform(h, b)

    X = np.c_[X_hand, X_polarity, X_refuting, X_overlap, X_word2vec, X_lda]
    return X,y


def pretrain_lda(train_dataset, test_dataset, overlap=False, 
                 model_file="pretrained_models/count_vec_model.pkl"):
    if os.path.exists(model_file) and (not overlap):
        print("LDA model ready")
        return  # already have the model, do nothing

    # else, pre train lda model
    train_data_hby = get_hby_from_dataset(train_dataset)
    test_data_hby = get_hby_from_dataset(test_dataset)
    all_headlines = np.concatenate((train_data_hby["h"], test_data_hby["h"]), axis=0)
    all_bodies = np.concatenate((train_data_hby["b"], test_data_hby["b"]), axis=0)
    lda_train_and_save(all_headlines, all_bodies, overlap=overlap)


if __name__ == "__main__":
    # if run directly, train on train_data and test on test_data to get score
    check_version()

    #Load datasets
    train_dataset = DataSet()
    test_dataset = DataSet("competition_test")

    # generate features
    X_train, y_train = generate_features(train_dataset, "train")
    X_test, y_test = generate_features(test_dataset, "test")

    # train LDA model
    pretrain_lda(train_dataset, test_dataset)

    # train lightGBM
    lgb_model = lgb.train(params, lgb.Dataset(X_train, y_train))
    
    # make prediction
    predicted = [LABELS[int(np.argmax(a))] for a in lgb_model.predict(X_test)]
    actual = [LABELS[int(a)] for a in y_test]

    print("Scores on the test set")
    report_score(actual, predicted)