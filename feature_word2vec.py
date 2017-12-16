import numpy as np
from tqdm import tqdm

from baseline.feature_engineering import get_tokenized_lemmas, clean, remove_stopwords, gen_or_load_feats
from google_vec_trim import read_vec_top


def pre_clean_tokenize(headlines, bodies, is_clean=True, is_token=True, remove_stop=True):
    cleaned_headlines, cleaned_bodies = [], []
    print("pre cleaning" )
    for i, (headline, body) in tqdm(enumerate(zip(headlines, bodies))):
        clean_headline = headline
        clean_body = body
        if is_clean:
            # clean sentence
            clean_headline = clean(clean_headline)
            clean_body = clean(clean_body)
        if remove_stop:
            # remove stop words
            clean_headline = " ".join(remove_stopwords(clean_headline.split()))
            clean_body = " ".join(remove_stopwords(clean_body.split()))
        if is_token:
            # separate sentence into list of words
            clean_headline = get_tokenized_lemmas(clean_headline)
            clean_body = get_tokenized_lemmas(clean_body)

        cleaned_headlines.append(clean_headline) 
        cleaned_bodies.append(clean_body)
    return cleaned_headlines, cleaned_bodies
    # two list of tokens that cleaned, removed stop words and change to normal version (e.g. dogs->dog, etc) 


def word2vec_helper(list_words, word2vec):
    return list(map(lambda word: word2vec[word], list_words))


def word2vec_pooling_features(headlines, bodies, need_clean=True, pooling="mean", word2vec=None):
    # print("Think: do you need clean?")
    assert isinstance(need_clean, bool) 
    if need_clean is True:
        headlines, bodies = pre_clean_tokenize(headlines, bodies)

    if word2vec is None:
        word2vec, freq_rank = read_vec_top(auto_generate=True)

    X = []
    print("generating feature by word2vec")
    for i, (headline, body) in tqdm(enumerate(zip(headlines, bodies))):
        headline = word2vec_helper(headline, word2vec)
        body = word2vec_helper(body, word2vec)
        if pooling == "mean":
            head_pool = sum(headline) / len(headline)
            body_pool = sum(body) / len(body)
        else:
            raise ValueError("Not support pooling method %s" % pooling)
        X.append(head_pool + body_pool)  # TODO: change to concat
    return X


def cos_sim(a, b=None):
    if b is None:
        # unpack
        a, b = a
    return np.dot(a, b)/(np.linalg.norm(a) * np.linalg.norm(b))


def word2vec_pool_similarity(head_pool, body_pool):
    return cos_sim(head_pool, body_pool)
