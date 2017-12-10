from tqdm import tqdm
from feature_engineering import get_tokenized_lemmas, clean, remove_stopwords, gen_or_load_feats
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation 
from sklearn.metrics.pairwise import cosine_similarity
from google_vec_get_top import read_vec_top

def pre_clean_tokenize(headlines, bodies, is_clean=True, is_token=True, remove_stop=True):
    cleaned_headlines, cleaned_bodies = [], []
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
    print("Think: do you need clean?")
    assert isinstance(need_clean, bool) 
    if need_clean is True:
        headlines, bodies = pre_clean_tokenize(headlines, bodies)

    if word2vec is None:
        word2vec, freq_rank = read_vec_top(auto_generate=True)

    X = []
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


def word2vec_pool_similarity(head_pool, body_pool):
    return cosine_similarity(head_pool, body_pool)


def get_count_vectorizer(headlines, bodies, need_clean=True):
    print("Think: do you need clean?")
    assert isinstance(need_clean, bool) 
    if need_clean is True:
        headlines, bodies = pre_clean_tokenize(headlines, bodies)

    cnt_vector_learner = CountVectorizer()
    cnt_vector_learner.fit(headlines + bodies)
    cnt_vector_headlines = cnt_vector_learner.transform(headlines)
    cnt_vector_bodies = cnt_vector_learner.transform(bodies)
    return cnt_vector_headlines, cnt_vector_bodies


def adapt_lda(headlines, bodies, need_clean=True):
    cnt_vector_headlines, cnt_vector_bodies = get_count_vectorizer(headlines, bodies)
    lda_learner = LatentDirichletAllocation(n_topics=25, use_idf=False, term_freq=True)
    lda_learner.fit(cnt_vector_headlines + cnt_vector_bodies)

    lda_headlines = lda_learner.transform(headlines)
    lda_bodies = lda_learner.transform(bodies)

    X = list(map(cosine_similarity, list(zip(lda_headlines, lda_bodies))))
    return X

# TODO: for LDA, we may need to input all corpus including train and test to train, 
# since it is an unsupervised method  

# revised in mac


