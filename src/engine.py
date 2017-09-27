from csv import reader
from copy import deepcopy
import os
import argparse
import numpy as np
import re
import sys

# constants
MARK_END_STATE = True
ATTACH_QUESTIONS = False
FILE_FORMAT = '.txt'
END_STATE_MARKER = 'ENDOFSTATE'
END_STORY_MARKER = 'ENDOFSTORY'
OUTPUT_ROOT = '../story'
INPUT_PATH  = '../schema'

# helper functions 
class Transition:
    """Represents a single set of transitions, with a condition"""
    def __init__(self, trans_cond, probs, trans_states):
        self.trans_cond = trans_cond
        self.probs = probs
        self.trans_states = trans_states

    def matches_cond(self, grounding, attributes):
        if self.trans_cond == 'Default':
            return True
        
        cond_split = self.trans_cond.replace('.', ' ').split(' ')
        cond_fill = attributes[grounding[cond_split[0]]][cond_split[1]]
        if not cond_fill.isnumeric():
            cond_fill = "\"" + cond_fill + "\""
        cond_split[0] = cond_fill
        cond_split[1] = ''
        return eval(''.join(cond_split))

    def get_trans_states(self):
        return self.trans_states

    def get_trans_cond(self):
        return self.trans_cond

    def get_probs(self):
        return self.probs

class State:
    """Represents a state with text and a list of possible transition sets"""
    def __init__(self, text, trans_list, roles_list):
        self.text = text
        self.trans_list = trans_list
        self.roles_list = roles_list

    def __get_trans_list_idx(self, grounding, attributes):
        '''
        figure out the correct index of the transitional distributions to use
        :param grounding:
        :param attributes:
        :return:
        '''
        i = 0
        while not self.trans_list[i].matches_cond(grounding, attributes):
            i += 1
        return i

    def sample_next(self, grounding, attributes):
        i = self.__get_trans_list_idx(grounding, attributes)
        probs = self.trans_list[i].probs
        trans_states = self.trans_list[i].trans_states
        next_state = np.random.choice(trans_states, p=probs)
        return next_state

    def get_distribution(self, grounding, attributes):
        '''
        get the distribution of the next states
        :param grounding:
        :param attributes:
        :return:
        '''
        i = self.__get_trans_list_idx(grounding, attributes)
        probs = self.trans_list[i].probs
        trans_states = self.trans_list[i].trans_states
        distribution = dict(zip(trans_states, probs))
        trans_cond = self.trans_list[i].get_trans_cond()
        return distribution, trans_cond

    def get_num_next_states(self,grounding, attributes):
        i = self.__get_trans_list_idx(grounding, attributes)
        return len(self.trans_list[i].trans_states)

    def get_roles(self):
        # this function is a helper for getting possible questions for this state
        return self.roles_list



def read_schema_file(input_fname):
    print('Schema = %s' %
        os.path.abspath(os.path.join(INPUT_PATH, input_fname)) + FILE_FORMAT)
    attributes = dict()
    entities = dict()
    roles = dict()
    states = dict()
    f = open(os.path.join(INPUT_PATH, input_fname) + FILE_FORMAT)

    # Read entities and their attributes
    #   each entity has a list of fillers - e.g. Person: ['Olivia', 'Mariko', ...]
    #   each filler has a dict of features - e.g. Mariko : {'Mood': 'nervous', ...}
    assert f.readline().strip() == "Entities", "Spec file must start with Entities"
    f.readline()  # Dashed line
    while True:
        nextline = f.readline().strip()
        if nextline == 'Roles':
            break
        ent_spec = nextline.split(':')
        ent_name = ent_spec[0]
        ent_attr = [x.strip() for x in ent_spec[1].split(',')]
        entities[ent_name] = []

        inst_line = f.readline().strip()
        while inst_line:
            # Use csv reader here, to ignore commas inside quotes
            instance = [x for x in reader([inst_line], skipinitialspace=True)][0]
            assert len(instance) == len(ent_attr), \
                "Instance %s does not match entity spec" % instance[0]
            entities[ent_name].append(instance[0])
            attributes[instance[0]] = dict()
            for i, a in enumerate(ent_attr):
                attributes[instance[0]][a] = instance[i]
            inst_line = f.readline().strip()

    # Read roles
    #   the role of high-level entity - e.g. Friend: Person
    f.readline() # Dashed line
    role_line = f.readline().strip()
    while role_line:
        role = [x.strip() for x in role_line.split(':')]
        roles[role[0]] = role[1]
        role_line = f.readline().strip()

    # Read States and transitions
    #   state
    #   transition
    assert f.readline().strip() == "States", "States must follow Roles"
    f.readline() # Dashed line
    while True:
        state_name = f.readline().strip()
        text = f.readline().strip()

        # gather all roles that can be queried, for QA
        roles_list = []
        roles_list_with_field = re.findall(r'\[(.*?)\]', text)
        for role in roles_list_with_field:
            roles_list.append(os.path.splitext(role)[0])
        roles_list = set(roles_list)

        if state_name == "END":
            states[state_name] = State(text, [], roles_list)
            break

        # gather the next states with edge weights (if not end)
        trans_list = []
        trans_line = f.readline().strip()
        while trans_line:
            trans_split = trans_line.split(':')
            trans_cond = trans_split[0]
            probs = []
            trans_states = []
            assert len(trans_split) == 2, "Transition should have one colon - %s" % trans_line
            for x in trans_split[1].split(','):
                [p,s] = x.strip().split(' ')
                probs.append(p)
                trans_states.append(s)
            probs = np.array(probs).astype(np.float)
            trans_list.append(Transition(trans_cond, probs, trans_states))
            trans_line = f.readline().strip()

        # grab all info to represent the state
        states[state_name] = State(text, trans_list, roles_list)

    f.close()
    return (attributes, entities, roles, states)


def mkdir(names_concat, n_iterations, n_repeats):
    output_subpath = ('%s_%s_%s' % (names_concat, str(n_iterations), str(n_repeats)))
    # make output directory if not exists
    if not os.path.exists(OUTPUT_ROOT):
        os.makedirs(OUTPUT_ROOT)
        print('mkdir: %s', OUTPUT_ROOT)

    final_output_path = os.path.join(OUTPUT_ROOT, output_subpath)
    if not os.path.exists(final_output_path):
        os.makedirs(final_output_path)
        print('- mkdir: %s', final_output_path)
    return final_output_path


def open_output_file(output_path, input_fname, n_iterations, n_repeats):
    n_iterations = str(n_iterations)
    n_repeats = str(n_repeats)

    # get a handle on the output file
    output_fname = os.path.join(output_path, input_fname
                                + '_' + n_iterations + '_' + n_repeats + FILE_FORMAT)
    f_output = open(output_fname, 'w')
    print('Output = %s' % (os.path.abspath(output_fname)))
    return f_output


def write_stories(schema_info, f_stories, f_Q_next, rand_seed, n_repeats):
    # Generate stories
    for i in range(n_repeats):
        np.random.seed(rand_seed)
        write_one_story(schema_info, f_stories, f_Q_next)
        # increment the seed, so that every story uses a different seed value
        # but different runs of run_engine.py use the same sequence of seed
        rand_seed += 1
    return rand_seed


def write_one_story(schema_info, f_stories, f_Q_next):

    (attributes, entities, roles, states) = schema_info
    grounding = get_grounding(entities, roles)

    # Loop through statess
    curr_state = 'BEGIN'
    while True:

        # Output state text with fillers
        # get a un-filled state
        filled = get_filled_state(curr_state, grounding, states, attributes)

        if curr_state != 'BEGIN' and curr_state != 'END' and had_alt_future:
            distribution, _ = states[prev_state].get_distribution(grounding, attributes)
            curr_state_p = distribution.get(curr_state)
            f_Q_next.write(str(curr_state_p) + ', ' + curr_state + ', ' + filled + '\n')
        had_alt_future = False

        # collect question text
        f_Q_next.write('\n' + filled + '\n')

        if ATTACH_QUESTIONS:
            filled = attach_question(filled, states, curr_state)
        if MARK_END_STATE:
            filled += (' ' + END_STATE_MARKER)

        # write text to file
        f_stories.write(filled + " ")

        # stopping criterion
        if curr_state == 'END':
            if MARK_END_STATE:
                f_stories.write(END_STORY_MARKER)
            f_stories.write(' \n\n')
            f_Q_next.write(' \n\n')
            break

        # update: sample next state
        prev_state = curr_state
        curr_state = states[curr_state].sample_next(grounding, attributes)

        # sample a possible alternative future state
        # TODO can also sampel an impossible state
        alt_future = get_alternative_future(prev_state, curr_state, states, grounding, attributes)
        # write to file if exisits
        if alt_future != 0:
            had_alt_future = True
            alt_future_filled = get_filled_state(alt_future, grounding, states, attributes)
            # get the probability of the alternative future
            distribution, condition = states[prev_state].get_distribution(grounding, attributes)
            alt_future_p = distribution.get(alt_future)
            # write to q_next file
            f_Q_next.write(condition + '\n')
            f_Q_next.write(str(alt_future_p) + ', ' +  alt_future + ', ' + alt_future_filled + '\n')


def get_alternative_future(prev_state, curr_state, states, grounding, attributes):
    '''
    given the previous state and the current state, find an alternative current state
    :param prev_state:
    :param curr_state:
    :param states:
    :param grounding:
    :param attributes:
    :return: an alternative current state (0 if no alternative)
    '''
    n = states[prev_state].get_num_next_states(grounding, attributes)
    if n == 1:
        return 0
    altnative_future_state = curr_state
    while altnative_future_state == curr_state:
        altnative_future_state = states[prev_state].sample_next(grounding, attributes)
    return altnative_future_state


def get_grounding(entities, roles):
    grounding = dict()
    avail_entities = deepcopy(entities)
    for role in sorted(roles.keys()):
        grounding[role] = np.random.choice(avail_entities[roles[role]])
        avail_entities[roles[role]].remove(grounding[role])
    return grounding

def get_filled_state(curr_state, curr_grounding, all_states, all_attributes):
    '''
    generate a text sentence representation of a state with filled groundings
    :param curr_state:
    :param curr_grounding:
    :param all_states:
    :param all_attributes:
    :return:
    '''
    text_split = all_states[curr_state].text.replace(']', '[').split('[')
    for i in range(1, len(text_split), 2):
        slot = text_split[i].split('.')
        text_split[i] = all_attributes[curr_grounding[slot[0]]][slot[1]]
    # get a filled state
    filled = ''.join(text_split)
    if filled[0] == "\"":
        filled = filled[0] + filled[1].upper() + filled[2:]
    else:
        filled = filled[0].upper() + filled[1:]
    return filled


def attach_question(filled_sentence_text, states, curr_state):
    roles_list = states[curr_state].get_roles()
    for role in roles_list:
        question_text = ' Q' + role
        filled_sentence_text += question_text
    return filled_sentence_text

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
