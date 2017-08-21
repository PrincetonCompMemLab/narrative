import pickle
import sys
import numpy as np
import os
from utils import *

# extract letters and spaces, and transform to lower case 
# how: python proc_txt.py input_file_name

# read input args
_, input_fname = sys.argv

# constant path
input_path = '../story/'
output_path ='../story_processed/'

# read input text file
print('Input text = <%s>' % (input_path+input_fname))
input_file = open(input_path + input_fname + '.txt', 'r')
text = input_file.read()
# make output dir
output_path = os.path.join(output_path, input_fname)
if not os.path.exists(output_path):
    os.makedirs(output_path)

# processing 
text = str2cleanstr(text)
text = to_lower_case(text)
list_of_words = text2list_of_words(text)
index, X, word_to_id = list_of_words_2_one_hot(list_of_words)

print(len(list_of_words))
print(np.shape(index))
print(np.shape(X))
print(word_to_id)


index_string = list_of_int_to_int_string(index)


# write to output file
char_output_fname = input_fname + '_clean.txt'
write2file(text, char_output_fname, output_path)

# sys.exit('STOP - word level output')
word_output_fname = input_fname + '_word.txt'
write2file(index_string, word_output_fname, output_path)

word_output_npz_fname = input_fname + '_word'
save_list_of_int_to_npz(index, word_output_npz_fname, output_path, .9)

word_dict_output_fname = input_fname + '_word_dict'
save_dict(word_to_id, word_dict_output_fname, output_path)






