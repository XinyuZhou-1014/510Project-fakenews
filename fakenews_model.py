import numpy as np
import pickle
from feature_engineering import word_overlap_features, refuting_features, polarity_features, hand_features
from feature_engineering_extra import word2vec_pooling_features, read_vec_top
import time
import os

LABELS = ['agree', 'disagree', 'discuss', 'unrelated']

class FakeNewsModel():
    def __init__(self, model='gbdt_res_with_w2v.pickle', top=10000, wait_time=0.2):
        self.wait_time = wait_time
        self.preload(model, top)

    def preload(self, model, top):
        self.model = self.read_model(model)
        self.preload_word2vec, unused_freq_rank = read_vec_top(
            top=top, auto_generate=True)
        print("Finish preload")

    def read_model(self, filename):
        with open(filename, "rb") as f:
            clf = pickle.load(f)
        self.model = clf

    def generate_feature_for_inputs(self, h, b):
        X_overlap = word_overlap_features(h, b)
        X_refuting = refuting_features(h, b)
        X_polarity = polarity_features(h, b)
        X_hand = hand_features(h, b)
        X_w2v_pool = word2vec_pooling_features(h, b, need_clean=True, word2vec=self.preload_word2vec)
        X = np.c_[X_hand, X_polarity, X_refuting, X_overlap, X_w2v_pool]
        return X

    def get_result(self, headlines, bodies):
        X = self.generate_feature_for_inputs(headlines, bodies)
        y_pred = self.model.predict(X)
        return [LABELS[x] for x in y_pred]

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


if __name__ == "__main__":
    print("Server start.")
    print("Put file at test_input.txt (will be delete)") 
    server = FakeNewsModel()   
    server.input_output("test_input.txt", "test_output.txt", 'gbdt_res_with_w2v.pickle')