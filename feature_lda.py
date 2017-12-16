from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation 
from feature_word2vec import pre_clean_tokenize, cos_sim
import pickle
import os
import numpy as np


def count_vectorizer_load_and_transform(test_corpus,
                                        model_file="pretrained_models/count_vec_model.pkl"):

    with open(model_file, "rb") as f:
        cnt_vector_learner = pickle.load(f)
        cnt_vector_corpus = cnt_vector_learner.transform(test_corpus)
    return cnt_vector_corpus


def count_vectorizer_train_and_save(train_corpus, need_clean=True, overlap=True,
                                    model_file="pretrained_models/count_vec_model.pkl"):
    # when transform, this will ignore unseen words
    if os.path.exists(model_file) and overlap is False:
        print("Model %s exists, will load." %model_file)
        return count_vectorizer_load_and_transform(train_corpus, model_file)
    else:
        cnt_vector_learner = CountVectorizer(stop_words="english") 
        cnt_vector_learner.fit(train_corpus)
        with open(model_file, "wb") as f:
            pickle.dump(cnt_vector_learner, f)

        cnt_vector_corpus = cnt_vector_learner.transform(train_corpus)
        return cnt_vector_corpus


def lda_train_and_save(headlines, bodies, overlap=True,
                       n_components=25, verbose=1, max_iter=20, 
                       model_file="pretrained_models/lda_model.pkl"):
    
    if overlap is False and os.path.exists(model_file):
        print("Model %s exists, will not overlap." %model_file)
        return

    # clean for count_vector
    cleaned_headlines, cleaned_bodies = pre_clean_tokenize(headlines, bodies, is_token=False)
    train_corpus = np.concatenate((cleaned_headlines, cleaned_bodies), axis=0) 
    cnt_vector_corpus = count_vectorizer_train_and_save(
        train_corpus, overlap=overlap)
    lda_learner = LatentDirichletAllocation(n_components=n_components, 
                                            verbose=verbose, 
                                            max_iter=max_iter,
                                            learning_method='batch')
    
    print("start training LDA")
    lda_learner.fit(cnt_vector_corpus)
    with open(model_file, "wb") as f:
        pickle.dump(lda_learner, f)
    print("finish training LDA")


def lda_load_and_transform(headlines, bodies, 
                           model_file="pretrained_models/lda_model.pkl"):
    if (not os.path.exists(model_file)):
        print("No model %s. Check path or generate with full corpus first.")

    cnt_vector_headlines = count_vectorizer_load_and_transform(headlines)  # default model file
    cnt_vector_bodies = count_vectorizer_load_and_transform(bodies)  # default model file

    with open(model_file, "rb") as f:
        lda_learner = pickle.load(f)

    lda_headlines = lda_learner.transform(cnt_vector_headlines)
    lda_bodies = lda_learner.transform(cnt_vector_bodies)

    cosine_similarity = list(map(cos_sim, list(zip(lda_headlines, lda_bodies))))
    cosine_similarity = np.reshape(cosine_similarity, (-1, 1))
    X = np.concatenate((lda_headlines, lda_bodies, cosine_similarity), axis=1)
    return X



