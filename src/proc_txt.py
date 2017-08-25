import numpy as np
import sys
import os
from utils import *

# extract letters and spaces, and transform to lower case 
# how: python proc_txt.py input_file_name

# read input args
# _, input_fname = 'temp', 'poetry_2'
_, input_fname = sys.argv

# constant
SHUFFLE_STATES = False
input_path = '../story/'
output_path ='../story_processed/'
train_test_ratio = .9

# read input text file
print('Input text = <%s>' %
      os.path.abspath(os.path.join(input_path,input_fname)))
input_file = open(input_path + input_fname + '.txt', 'r')
text = input_file.read()
# make output dir
output_path = os.path.join(output_path, input_fname)
if SHUFFLE_STATES:
    output_path += '_shuf'
if not os.path.exists(output_path):
    os.makedirs(output_path)

# post-processing
text = str2cleanstr(text)
if SHUFFLE_STATES:
    text = shuffle_text(text)
text = to_lower_case(text)
# convert to word-level representation
list_of_words = text2list_of_words(text)
index, X, word_to_id = list_of_words_2_one_hot(list_of_words)
index_string = list_of_int_to_int_string(index)

print('')
# write to output file - char level 
char_output_fname = input_fname + '_clean.txt'
write2file(text, char_output_fname, output_path)

# sys.exit('STOP - word level output')
# word_output_fname = input_fname + '_word.txt'
# write2file(index_string, word_output_fname, output_path)
write2file(index_string, 'words.txt', output_path)
# save .npz word file and its dictionary 
save_list_of_int_to_npz(index, input_fname, output_path, train_test_ratio)
save_dict(word_to_id, input_fname, output_path)

