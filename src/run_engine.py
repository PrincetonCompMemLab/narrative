import sys
from engine import *

# get input arguments
parser = argparse.ArgumentParser()
parser.add_argument("schema_files", nargs='+', type=str)
parser.add_argument("n_iterations", nargs=1, type=int,
                    help = 'n_samples from a given schema file')
parser.add_argument("n_consecutive_repeats", nargs=1, type=int,
                    help = 'n_consecutive_repeats of the same schema')

# process arguments
args = vars(parser.parse_args())
print(args)
input_fnames = args.get('schema_files')
n_iterations = args.get('n_iterations')[0]
n_repeats = args.get('n_consecutive_repeats')[0]

n_input_files = len(input_fnames)
names_concat = '_'.join(input_fnames)


# sample stories from one or more schemas
# Returns a scene (state) vector s_1:n formatted for HRR encoding
# as well as a sequence of event labels e_1:n according to the story type
#
def main(rand_seed):
    # get a handle on the output file
    output_path = mkdir(names_concat, n_iterations, n_repeats)
    f_stories = open_output_file(output_path, names_concat, n_iterations, n_repeats)
    f_QA = open_output_file(output_path, names_concat + '_QA', n_iterations, n_repeats)
    # read all schema files
    schema_info = []
    for i in range(n_input_files):
        schema_info.append(read_schema_file(input_fnames[i]))

    # write stories with alternating schema info
    scenes = [] # s_1:n
    events = [] # e_1:n
    for i in range(n_input_files * n_iterations):
        f_idx = np.mod(i, n_input_files)
        # write to the output file
        rand_seed, schema_scenes = write_stories(schema_info[f_idx],
                                  f_stories, f_QA,
                                  rand_seed, n_repeats)
        scenes.extend(schema_scenes)
        events.extend([f_idx] * len(schema_scenes))

    assert len(events) == len(scenes)
    f_stories.close()
    f_QA.close()

    return scenes, events

if __name__ == "__main__":
    # if there is only one 1 schema file, repeat & iter are the same thing
    if n_input_files == 1:
        n_iterations = n_iterations * n_repeats
        n_repeats = 1
    main(0)
