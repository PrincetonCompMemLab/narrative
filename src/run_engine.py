#import sys  # not used
import argparse
from engine import main

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

if __name__ == "__main__":
    # set the constants for the stories
    stories_kwargs = dict(
        mark_end_state=False,  # attach end_of_state, end_of_story marker
        attach_questions=False,  # attach question marker at the end of the state (e.g. Q_subject)
        gen_symbolic_states=False,  # GEN_SYMBOLIC_STATES = False
        attach_role_marker=False,  # ATTACH_ROLE_MARKER = False
        attach_role_maker_before=['Pronoun', 'Name', 'Pronoun_possessive', 'Pronoun_object'],
    )

    # if there is only one 1 schema file, repeat & iter are the same thing
    if n_input_files == 1:
        n_iterations = n_iterations * n_repeats
        n_repeats = 1

    main(0, input_fnames, n_input_files, names_concat, n_iterations, n_repeats, write_to_files=True, stories_kwargs=stories_kwargs)
