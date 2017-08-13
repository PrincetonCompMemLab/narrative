import string
import sys
import numpy as np
from utils import *

# extract letters and spaces, and transform to lower case 
# how: python clean_txt.py input_file_name

# read input file
_, input_fname = sys.argv
input_path = '../story/'
output_path ='../story_processed/'
print('Input text = <%s>' % (input_path+input_fname))
input_file = open(input_path + input_fname + '.txt', 'r')
text = input_file.read()

# processing 
text = str2cleanstr(text)
text = to_lower_case(text)
# list_of_words = text2list_of_words(text)
# index, X = list_of_words_2_one_hot(list_of_words)

# write to output file 
output_fname = input_fname + '_clean.txt'
output_file = open(output_path + output_fname, 'w')
print('Write to <%s>' % (output_path+output_fname))
output_file.write(text)
output_file.close()
