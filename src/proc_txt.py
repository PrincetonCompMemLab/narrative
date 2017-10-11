import numpy as np
import sys
import os
from utils import *
from utils_procs import *

# extract letters and spaces, and transform to lower case 
# how: python proc_txt.py input_file_name

# read input args
# _, input_fname = 'temp', 'poetry_2'
_, input_fname = sys.argv

# constant
input_path = '../story/'
train_test_ratio = .9

def get_word_level_rep(text, output_path, train_test_ratio):
  # convert to word-level representation
  indices, _, words_dict = text_2_one_hot(text)
  index_string = list_of_int_to_int_string(indices)

  # save .npz word file and its dictionary
  save_list_of_int_to_npz(indices, words_dict, output_path, train_test_ratio)
  save_dict(words_dict, output_path)
  # write to output file - char level
  write2file(text, 'chars_we.txt', output_path)
  [text] = remove_end_markers([text])
  write2file(text, 'chars_woe.txt', output_path)


# read input text file
input_path = os.path.join(input_path,input_fname)
print('Input text from <%s>' % os.path.abspath(input_path))
input_file_path = os.path.join(input_path, input_fname + '.txt')
input_file = open(input_file_path, 'r')
text = input_file.read()

# get output dir name and makr output dirs
output_path = input_path
make_output_cond_dirs(output_path)

# remove pun markers...
text = str2cleanstr(text)
# create shuffling
text_shufw = shuffle_words_in_state(text)
text_shufs = shuffle_states_in_story(text)

# conver to lower case
[text, text_shufw, text_shufs] = to_lower_case([text, text_shufw, text_shufs])

# save word level representation
get_word_level_rep(text, os.path.join(output_path, 'shuffle_none'), train_test_ratio)
get_word_level_rep(text_shufw, os.path.join(output_path, 'shuffle_words'), train_test_ratio)
get_word_level_rep(text_shufs, os.path.join(output_path, 'shuffle_states'), train_test_ratio)