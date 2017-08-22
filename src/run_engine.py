from csv import reader
from copy import deepcopy
import os
import numpy as np
import argparse
import sys
from engine import *

# get input arguments
parser = argparse.ArgumentParser()
parser.add_argument("schema_files", nargs='+', type=str)
parser.add_argument("n_iterations", nargs=1, type=int,
                    help = 'n_samples from a given schema file')
parser.add_argument("alternating", nargs=1, type=str2bool, default=False,
                    help='if true, gen stories alternatingly between k input schema files')

# process arguments
args = vars(parser.parse_args())
print(args)
input_fnames = args.get('schema_files')
n_iterations = args.get('n_iterations')
n_iterations = n_iterations[0]
alternating = args.get('alternating')
alternating = alternating[0]
n_input_files = len(input_fnames)
name_cat = '_'.join(input_fnames)


# sample stories from schema
def main():
    rand_seed = 0
    if not alternating:
        if n_input_files == 1:
        # get a handle on the output file
            f_out = open_output_file(input_fnames[0], n_iterations)
        elif n_input_files > 1:
            f_out = open_output_file(name_cat + '_block', n_iterations)
        else:
            raise ValueError('n_input_files must >= 1')
        # write stories block-wise
        for i in range(n_input_files):
            input_fname = input_fnames[i]
            # read schema file
            schema_info = read_schema_file(input_fname)
            # write to the output file
            write_stories(schema_info, n_iterations, f_out)
    else:
        if alternating and n_input_files < 2:
            raise AssertionError('Need at least 2 files to alternate!')
        # get a handle on the output file
        f_out = open_output_file(name_cat+'_alt', n_iterations)
        # read all schema files
        schema_info = []
        for i in range(n_input_files):
            schema_info.append(read_schema_file(input_fnames[i]))
        # write stories with alternating schema info
        for i in range(n_input_files * n_iterations):
            f_idx = np.mod(i, n_input_files)
            # write to the output file
            write_stories(schema_info[f_idx], 1, f_out, rand_seed)
            rand_seed += 1

    # close the output
    f_out.close()

if __name__ == "__main__":
    main()