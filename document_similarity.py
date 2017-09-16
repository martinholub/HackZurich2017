import logging
import numpy as np

from scipy.spatial.distance import cdist 

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.WARNING)
import numpy as np
from nltk.tokenize import RegexpTokenizer
import nltk

np.set_printoptions(threshold=np.nan)

tokenizer = RegexpTokenizer(r'\w+')
import os
import time
import argparse
from gensim.models import Word2Vec
import pickle

W2V =  '/home/nikola/data/raw/wiki/GoogleNews-vectors-negative300.bin'

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
import string
import re

tokenizer = RegexpTokenizer(r'\w+')
porter_stemmer = PorterStemmer()
printable = set(string.printable)

w2v = Word2Vec.load_word2vec_format(W2V, binary=True)
logging.warning("Loaded Word2Vec model {} with embedding dim {}".format(W2V, w2v.vector_size))

def clean_text(txt, return_string=False):
    txt = txt.lower()  # Lower the text.
    txt = word_tokenize(txt)  # Split into words.
    txt = [w for w in txt if not w in stopwords.words('english')]  # Remove stopwords.
    txt = [w for w in txt if w.isalpha()]  # Remove numbers and punctuation.
    if return_string:
        return " ".join(txt)
    else:
        return txt
    
def get_word_vectors(doc, w2v):
    vectors = []
    for word in doc:
        try:
            vectors.append(w2v.wv[word])
        except KeyError:
            continue
    return vectors


def average_word_embedding(sentence, w2v):
    vectors = get_word_vectors(sentence, w2v)
    if len(vectors) == 0:
        return np.ones(w2v.vector_size) * np.nan
    return np.mean(vectors, 0)


def cosine_similarity_matrix(docs1, docs2, w2v, dtype=float):
    clean_sent_1 = [clean_text(doc) for doc in docs1]
    #if sentences2 is not None:
    clean_sent_2 = [clean_text(doc) for doc in docs2]
    #else:
    #    clean_sent_2 = [None] * 2
    if (len(clean_sent_1) > 0 and len(clean_sent_2) > 0):
        sent_emb_1 = np.array([average_word_embedding(c, w2v) for c in clean_sent_1], dtype=dtype)
        #if sentences2 is not None:
        sent_emb_2 = np.array([average_word_embedding(c, w2v) for c in clean_sent_2], dtype=dtype)
        sim_matrix = 1 - cdist(sent_emb_1, sent_emb_2, "cosine")
        #else:
        #    sim_matrix = 1 - cdist(sent_emb_1, sent_emb_1, "cosine")
        #    sim_matrix = np.triu(sim_matrix)
        return sim_matrix
    else:
        return np.zeros((len(sentences1), len(sentences2) if docs2 is not None else len(docs2)))
    
    
print(cosine_similarity_matrix(["Obama president usa"], ["government china", 'pop star music video'], w2v))
