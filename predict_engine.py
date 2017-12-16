import numpy as np
from baseline.feature_engineering import refuting_features, polarity_features
from baseline.feature_engineering import hand_features, gen_or_load_feats
from baseline.feature_engineering import word_overlap_features
from baseline.utils.score import LABELS

from google_vec_trim import read_vec_top
from feature_word2vec import word2vec_pooling_features
from feature_lda import lda_load_and_transform
import time
import os
import lightgbm as lgb


class FakeNewsModel():
    def __init__(self, model_file, top=10000, wait_time=0.2):
        self.wait_time = wait_time
        self.preload(model_file, top)

    def preload(self, model_file, top):
        self.model = self.read_model(model_file)
        self.preload_word2vec, unused_freq_rank = read_vec_top(
            top=top, auto_generate=True)
        print("Finish preload")

    def read_model(self, model_file):
        lgb_model = lgb.Booster(model_file=model_file)
        self.model = lgb_model

    def generate_feature_for_inputs(self, h, b):
        X_overlap = word_overlap_features(h, b)
        X_refuting = refuting_features(h, b)
        X_polarity = polarity_features(h, b)
        X_hand = hand_features(h, b)
        X_w2v_pool = word2vec_pooling_features(h, b, need_clean=True, word2vec=self.preload_word2vec)
        X_lda = lda_load_and_transform(h, b)
        X = np.c_[X_hand, X_polarity, X_refuting, X_overlap, X_w2v_pool, X_lda]
        return X

    def get_result(self, headlines, bodies):
        X = self.generate_feature_for_inputs(headlines, bodies)
        y_pred = self.model.predict(X)
        res = []
        for pred in y_pred:
            string = "%s: %7.4f, %s: %7.4f, %s: %7.4f, %s: %7.4f" % (
                LABELS[0], pred[0], 
                LABELS[1], pred[1], 
                LABELS[2], pred[2], 
                LABELS[3], pred[3]
            )
            res.append(string)
        return res

    def simple_text_parser(self, input_file_path):
        '''
        simple text parser
        assume there are even lines in total, 
        each odd line is headline and the following line is body
        '''
        with open(input_file_path, "r") as f:
            text = f.readlines()
        try:
            assert len(text) % 2 == 0
        except AssertionError: 
            print("Warning: simple text parser only support format like this:")
            print("Even lines in total,")
            print("each odd line is headline and the following line is body.")
            print("The input has odd lines, so ignore the last line.")
            text = text[:-1]

        h = [text[2*i] for i in range(len(text) // 2)]
        b = [text[2*i+1] for i in range(len(text) // 2)]
        return h, b

    def input_output(self, input_file_path, output_file_path, model_name=None):
        if model_name is not None:
            self.read_model(model_name)
        while True:
            while not (os.path.exists(input_file_path)):
                time.sleep(self.wait_time)

            t = time.time()
            headlines, bodies = self.simple_text_parser(input_file_path)
            res = self.get_result(headlines, bodies)
            with open(output_file_path, "w") as f:
                f.write("\n".join(res))

            os.remove(input_file_path)
            tt = time.time()
            print("Finish one output (%.4fs)." % (tt - t))
            t = tt