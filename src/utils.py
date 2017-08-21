from sklearn.preprocessing import OneHotEncoder
from random import shuffle 
import numpy as np
import pickle
import string
import itertools
import re
import os
import sys
import json

END_STATE_MARKER = 'ENDOFSTATE'

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

    # helper function
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
    (doc_len, n_tokens) = np.shape(X)
    print('\t Doc length = %d, Num token = %d' % (doc_len, n_tokens))
    return token_ids, X, word_to_id

def list_of_int_to_int_string(list_of_int):
    print('Converting list of integers to a string of integers...')
    int_string = ''
    for i in list_of_int:
        int_string += str(list_of_int[i])
        int_string += ' '
    return int_string


def shuffle_text(text):
    print('Shuffle the words (within each state) in the story ...')
    # split the input story to sentences, w.r.t END_STATE_MARKER
    states_list = text.split(END_STATE_MARKER)
    shuf_states_list = [] 
    # for each sentence... 
    for i in range(len(states_list)): 
        if states_list[i] != ' ':
            # split into words and shuffle the words 
            cur_state_split = states_list[i].split()
            shuffle(cur_state_split) 
            # recombine to a sentence 
            shuf_cur_state = ' '.join(cur_state_split)
            shuf_cur_state += (' ' + END_STATE_MARKER + ' ')
            # add to the shuffed sentence list 
            shuf_states_list.append(shuf_cur_state)
    # recombine to a story     
    shuffled_story = ''.join(shuf_states_list)
    assert(len(shuffled_story) == len(text))
    return shuffled_story



def write2file(input_text, output_fname, output_path):
    '''
    write a string to a file
    :param input_text: a string
    :param output_fname: file name
    :param output_path: output directory
    :return:
    '''

    print('Write to <%s>' % (os.path.join(output_path, output_fname)))
    output_file = open(os.path.join(output_path, output_fname), 'w')
    output_file.write(input_text)
    output_file.close()


def save_dict(input_dict, dict_name, output_path):
    dict_name = dict_name + '_word_dict.pickle'
    write_path = os.path.join(output_path, dict_name)
    print('Write to <%s>' % write_path)
    with open(write_path, 'wb') as handle:
        pickle.dump(input_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('Write to <%s>' % os.path.join(output_path, 'metadata.txt'))
    json.dump(input_dict, open(os.path.join(output_path, 'metadata.txt'),'w'))
    
    
    
    # testing
    # temp_dict = read_dict(dict_name, input_path=output_path)
    # assert(temp_dict == input_dict)

def read_dict(dict_name, input_path):
    read_path = input_path + dict_name + '.pickle'
    print('Reading from <%s>' % read_path)
    with open(read_path, 'rb') as handle:
        output_dict = pickle.load(handle)
    return output_dict



def save_list_of_int_to_npz(list_of_int, fname, output_path, train_ratio):
    fname = fname + '_word'
    # count n_tokens
    num_tokens = len(list_of_int)
    # split training and validation sets
    train_size = int(num_tokens * train_ratio)
    valid_size = int(num_tokens * (1 - train_ratio))
    train = list_of_int[: train_size]
    valid = list_of_int[: -valid_size]

    # write it to a .npz file
    path_output_file = os.path.join(output_path, fname)
    print('Write to <%s.npz>' % path_output_file)
    np.savez(path_output_file, train=train, valid=valid)

    # check output file
    # npzfile = np.load(path_output_file + '.npz')
    # print(npzfile.files)
    # temp = npzfile['train']
    # print(type(temp[1]))
    # print(temp)




'''
pending... don't use these 
'''
#
# def string2list_of_ascii(string):
#   '''
#   preprocessing to a list of ascii values
#    - code space as 0
#    - code chars as ascii val - 96 (so range = 1-27)
#   '''
#   list_of_ascii = []
#   for i in range(len(string)):
#     if ord(string[i]) == 32:
#       list_of_ascii.append(0)
#     else:
#       list_of_ascii.append(ord(string[i].lower()) - 96)
#   return list_of_ascii
#
#
# def get_doc_counts(data_path):
#   '''
#   :param: data_path: points to a english text file
#   :return: the number of characters, words and lines of a document
#   '''
#   num_chars = num_words = num_lines = 0
#   with open(data_path, 'r') as in_file:
#     for line in in_file:
#       num_lines += 1
#       num_words += len(line.split())
#       num_chars += len(line)
#   print 'num_chars = %d, num_words = %d, num_lines = %d' \
#         % (num_chars, num_words, num_lines)
#   return num_chars, num_words, num_lines
#
# def text_to_npz():
#     _, fname = sys.argv
#     # spec the path
#     # path = '/Users/Qihong/Dropbox/github/hmrnn/data/schema_both/'
#     # fname = 'both_out_clean'
#     path = '../story_processed/'
#     path_input_file = path + fname + '.txt'
#     path_output_file = path + fname + '.npz'
#
#     # count n_tokens
#     file = open(path_input_file, 'r')
#     num_chars, _, _ = get_doc_counts(path_input_file)
#     # split training and validation sets
#     train_ratio = .9
#     train_size = int(num_chars * train_ratio)
#     valid_size = int(num_chars * (1 - train_ratio))
#
#     # load the text file
#     file = open(path_input_file, 'r')
#
#     # read the training seq
#     train = file.read(train_size)
#     # jump to where it was left
#     file.seek(file.tell())
#     # read the valid seq
#     valid = file.read(valid_size)
#
#     # train = string2list_of_ascii(train)
#     # valid = string2list_of_ascii(valid)
#
#     # write it to a .npz file
#     np.savez(path_output_file, train=train, valid=valid)
#
#     # # check file
#     # npzfile = np.load(path_output_file)
#     # print npzfile.files
#     # temp = npzfile['train']
#     # print type(temp[1])