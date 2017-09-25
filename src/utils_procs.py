from sklearn.preprocessing import OneHotEncoder
from random import shuffle
from utils import *
import numpy as np
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


def to_lower_case(list_of_string):
    print('Convert text to lower case...')
    list_of_string_lower = []
    for string in list_of_string:
      list_of_string_lower.append(string.lower())
    return list_of_string_lower


def text2list_of_words(text):
    print('Convert text to a list of words...')
    return re.sub("[^\w]", " ", text).split()


def text_2_one_hot(text):
    list_of_words = text2list_of_words(text)
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
    #create a dictionary that maps word to id of word...
    # while ensure the end markers are at the end of the dict
    set_all_tokens = sorted(set(all_tokens))
    num_all_tokens = len(set_all_tokens)
    set_all_tokens.remove(END_STATE_MARKER.lower())
    set_all_tokens.remove(END_STORY_MARKER.lower())
    words_dict = {token: idx for idx, token in enumerate(set_all_tokens)}
    words_dict[END_STATE_MARKER.lower()] = max(words_dict.values()) + 1
    words_dict[END_STORY_MARKER.lower()] = max(words_dict.values()) + 1
    assert len(words_dict) == num_all_tokens
    # convert token lists to token-id lists
    token_ids = [[words_dict[token] for token in tokens_doc] for tokens_doc in tokens_docs]
    # convert list of token-id lists to one-hot representation
    vec = OneHotEncoder(n_values=len(words_dict))
    X = vec.fit_transform(token_ids)
    # reformat the output
    token_ids = list_of_singular_list_to_list_of_val(token_ids)
    X = X.toarray()
    (doc_len, n_tokens) = np.shape(X)
    print('\t Doc length = %d, Num token = %d' % (doc_len, n_tokens))
    return token_ids, X, words_dict


def list_of_int_to_int_string(list_of_int):
    print('Converting list of integers to a string of integers...')
    int_string = ''
    for i in list_of_int:
        int_string += str(list_of_int[i])
        int_string += ' '
    return int_string


def shuffle_words_in_state(text, scramble_type = 'reverse'):
    print('Shuffle the words (within each state) in the story ...')
    # split the input story to sentences, w.r.t END_STATE_MARKER
    states_list = text.split(END_STATE_MARKER)
    shuf_states_list = []
    # for each sentence...
    for i in range(len(states_list)):
        if states_list[i]!='':
            # split into words and shuffle the words
            cur_state_split = states_list[i].split()
            # if the prev state is the end of story
            if cur_state_split[0] == END_STORY_MARKER:
                # pop end_story -> shuffle -> add it back
                cur_state_split.pop(0)
                cur_state_split = scramble_list(cur_state_split)

                cur_state_split.insert(0, END_STORY_MARKER)
            else:
                cur_state_split = scramble_list(cur_state_split)
            # recombine to a sentence
            shuf_cur_state = ' '.join(cur_state_split)
            shuf_cur_state += (' ' + END_STATE_MARKER + ' ')
            # add to the shuffed sentence list
            shuf_states_list.append(shuf_cur_state)

    # recombine to a story
    shuffled_story = ''.join(shuf_states_list)
    shuffled_story = rchop(shuffled_story, END_STATE_MARKER + ' ')
    assert(len(shuffled_story) == len(text))
    return shuffled_story


def shuffle_states_in_story(text):
    '''
    stories - state level scrambling
    :param text: a bunch of stories
    :return: a bunch of state-scrambled stories
    '''
    print('Shuffle the states within each story ...')
    # get the list of stories
    stories_list = text.split(END_STORY_MARKER)
    if ' ' in stories_list: stories_list.remove(' ')
    if '' in stories_list:  stories_list.remove('')

    # shuffle states within story_i, for all i
    n_stories = len(stories_list)
    shuf_storys_list = []
    for i in range(n_stories):
        scrambled_story = scramble_states_in_one_story(stories_list[i])
        scrambled_story += END_STORY_MARKER + ' '
        shuf_storys_list.append(scrambled_story)
    # recombind all stories
    output = ''.join(shuf_storys_list)
    # convert all space-like characters to single spaces
    re.sub('\s+', ' ', output).strip()

    return output


def scramble_states_in_one_story(story_text, scramble_type = 'reverse'):
    '''
    turn a story to a state-shuffled story
    :param story_text: any story, represented by a string of text
    :return: a state-shuffled story
    '''
    states_list = story_text.split(END_STATE_MARKER+' ')
    if ' ' in states_list:  states_list.remove(' ')
    if '' in states_list:  states_list.remove('')

    # scramble the states!
    states_list = scramble_list(states_list, scramble_type)

    # recombine the story
    scrambled_story = ''
    for i in range(len(states_list)):
        scrambled_story += states_list[i] + END_STATE_MARKER
        if i != len(states_list): scrambled_story += ' '
    return scrambled_story


def scramble_list(list, scramble_type = 'reverse'):
    '''
    scramble a list according to scramble_type
    :param list:
    :param scramble_type:
    :return:
    '''
    if scramble_type == 'shuffle':
        shuffle(list)
    elif scramble_type == 'reverse':
        list = list[::-1]
    else:
        raise ValueError('unrecognizable scramble_type!!!')
    return list


def remove_end_markers(text_list):

  def remove_end_markers_sup(text):
    text = text.replace(' '+END_STATE_MARKER, '')
    text = text.replace(' '+END_STORY_MARKER, '')
    text = text.replace(' '+END_STATE_MARKER.lower(), '')
    text = text.replace(' '+END_STORY_MARKER.lower(), '')
    return text

  text_list_without_end = []
  for text in text_list:
    text_list_without_end.append(remove_end_markers_sup(text))
  return text_list_without_end