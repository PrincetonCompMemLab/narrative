from sklearn.preprocessing import OneHotEncoder
import numpy as np
import string
import itertools
import re
import sys

def str2cleanstr(string):
    print('Removing punctuation marks from text...')
    cleaned_txt = ''
    for character in string:
        if character.isalpha() or character is ' ':
            cleaned_txt += character
    return cleaned_txt

def to_lower_case(string):
    print('Convert text to lower case...')
    return string.lower()

def text2list_of_words(text):
    print('Convert text to a list of words...')
    return re.sub("[^\w]", " ", text).split()

def list_of_words_2_one_hot(list_of_words):
    def list_of_singular_list_to_list_of_val(input_list):
        out_list = []
        for i in range(len(input_list)):
            cache = input_list[i]
            assert (len(cache) == 1)
            out_list.append(cache[0])
        return out_list
    # dependencies:
    # - from sklearn.preprocessing import OneHotEncoder
    # - import itertools
    print('Convert list of words to word-level one-hot vector representation...')
    tokens_docs = [doc.split(" ") for doc in list_of_words]
    # convert list of of token-lists to one flat list of tokens
    all_tokens = itertools.chain.from_iterable(tokens_docs)
    #create a dictionary that maps word to id of word
    word_to_id = {token: idx for idx, token in enumerate(set(all_tokens))}
    # convert token lists to token-id lists
    token_ids = [[word_to_id[token] for token in tokens_doc] for tokens_doc in tokens_docs]
    # convert list of token-id lists to one-hot representation
    vec = OneHotEncoder(n_values=len(word_to_id))
    X = vec.fit_transform(token_ids)
    # reformat the output
    token_ids = list_of_singular_list_to_list_of_val(token_ids)
    X = X.toarray()
    return token_ids, X





