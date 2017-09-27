from itertools import islice
import numpy as np
import pickle
import os
import json
import sys

# CONSTANTS
SHUFFLE_CONDITIONS = ['NO_SHUF','SHUF_WORDS_IN_STATE', 'SHUF_STATES_IN_STORY']
END_STATE_MARKER = 'ENDOFSTATE'
END_STORY_MARKER = 'ENDOFSTORY'


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


def save_dict(input_dict, output_path):
    write_path = os.path.join(output_path, 'word_dict.pickle')
    print('Write to <%s>' % write_path)
    with open(write_path, 'wb') as handle:
        pickle.dump(input_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('Write to <%s>' % os.path.join(output_path, 'metadata.txt'))
    json.dump(input_dict, open(os.path.join(output_path, 'metadata.txt'),'w'))


def read_dict(dict_name, input_path):
    read_path = input_path + dict_name + '.pickle'
    print('Reading from <%s>' % read_path)
    with open(read_path, 'rb') as handle:
        output_dict = pickle.load(handle)
    return output_dict


def save_list_of_int_to_npz(list_of_int, words_dict, output_path, train_ratio):
    # get the index for the end marker
    end_story_marker_ind = words_dict[END_STORY_MARKER.lower()]
    end_state_marker_ind = words_dict[END_STATE_MARKER.lower()]
    # find a split between train and valid set
    num_stories = np.sum((np.array(list_of_int) == end_story_marker_ind))
    train_num_stories = int(np.round(num_stories * train_ratio))
    train_end_idx = nth_index(list_of_int, end_story_marker_ind, train_num_stories)+1
    # collect training and validation sets
    train = list_of_int[:train_end_idx]
    valid = list_of_int[train_end_idx - len(list_of_int):]
    # write train/valid sets to a .npz file
    path_output_file = os.path.join(output_path, 'words_we')
    print('Write to <%s.npz>' % path_output_file)
    np.savez(path_output_file, train=train, valid=valid)

    # get rid of both end markers
    train = get_rid_of(train, [end_state_marker_ind, end_story_marker_ind])
    valid = get_rid_of(valid, [end_state_marker_ind, end_story_marker_ind])
    # write these train/valid sets to another .npz file
    path_output_file = os.path.join(output_path, 'words_woe')
    print('Write to <%s.npz>' % path_output_file)
    np.savez(path_output_file, train=train, valid=valid)


def get_rid_of(mylist, things_to_remove):
    mylist[:] = [x for x in mylist if x not in things_to_remove]
    return mylist


def nth_index(iterable, value, n):
    '''
    Find the nth match between value and iterable
    :return: index of the nth match
    '''
    matches = (idx for idx, val in enumerate(iterable) if val == value)
    return next(islice(matches, n - 1, n), None)


def rchop(thestring, ending):
    if thestring.endswith(ending):
        return thestring[:-len(ending)]
    return thestring


def make_output_cond_dirs(output_path):
    condition_list = ['shuffle_none', 'shuffle_words', 'shuffle_states']
    for i in range(len(condition_list)):
        if not os.path.exists(os.path.join(output_path, condition_list[i])):
            os.makedirs(os.path.join(output_path, condition_list[i]))


