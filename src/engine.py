from csv import reader
from copy import deepcopy
import os
import argparse
import numpy as np
import re
import sys
import json



# constants
MARK_END_STATE = True
ATTACH_QUESTIONS = False
GET_FILLER_INCONSISTENT_Q = True
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

    people_introduced = set()
    people_all = set(entities['Person'])
    role_Person = []
    for role, type in roles.items():
        if type == 'Person': role_Person.append(role)
    # dump key-value binding to the file
    f_Q_next.write(json.dumps(grounding))

    # Loop through statess
    curr_state = 'BEGIN'
    while True:
        # Output state text with fillers
        # get a un-filled state
        filled, fillers = get_filled_state(curr_state, grounding, states, attributes)

        # don't write question in the 1st iteration
        # there is no next state if end
        # exisits alternative future  -> necessary -> exisits 2AFC
        if curr_state != 'BEGIN' and had_alt_future:
            distribution, _ = states[prev_state].get_distribution(grounding, attributes)
            curr_state_p = distribution.get(curr_state)
            f_Q_next.write(str(curr_state_p) + ', ' + curr_state + ', ' + filled + '\n')
        had_alt_future = False

        # collect question text
        f_Q_next.write('\n' + filled + '\n')

        if ATTACH_QUESTIONS:
            filled = attach_role_question_marker(filled, states, curr_state)
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

        # get question
        if GET_FILLER_INCONSISTENT_Q:
            alt_next_grounding, alt_future, condition, people_introduced = get_filler_inconsistent_next_state(
                fillers, people_introduced, people_all, curr_state, grounding, states, attributes
            )
        else:
            alt_future = get_alternative_future(prev_state, curr_state, states, grounding, attributes)

        # write to file if question exisits
        if alt_future != 0:
            had_alt_future = True
            if GET_FILLER_INCONSISTENT_Q:
                alt_future_filled, _ = get_filled_state(curr_state, alt_next_grounding, states, attributes)
                write_alt_next_state_q_file(f_Q_next, condition, 0, alt_future, alt_future_filled)
            else:
                alt_future_filled, _ = get_filled_state(alt_future, grounding, states, attributes)
                # get the probability of the alternative future
                distribution, condition = states[prev_state].get_distribution(grounding, attributes)
                alt_future_p = distribution.get(alt_future)
                write_alt_next_state_q_file(f_Q_next, condition, alt_future_p, alt_future, alt_future_filled)



def write_alt_next_state_q_file(f_Q_next, condition, alt_future_p, alt_future, alt_future_filled):
    '''
    write the alternative (possible or impossible) state to the question file
    :param f_Q_next: a handle on the question file
    :param condition: the condition (e.g. subj.mood == sad)
    :param alt_future_p: the probability of the alternative future state
    :param alt_future: the state name of the alternative future state
    :param alt_future_filled: the instantitated alternative future state
    :return:
    '''
    f_Q_next.write(condition + '\n')
    f_Q_next.write(str(alt_future_p) + ', ' + alt_future + ', ' + alt_future_filled + '\n')



def get_filler_inconsistent_next_state(fillers, people_introduced, people_all, curr_state, grounding, states, attributes):
    '''
    get an altnerative next state, with inconsistent filler (so it is "impossible" in this sense)
    update people_introduced
    :param fillers:
    :param people_introduced:
    :param people_all:
    :param curr_state:
    :param grounding:
    :param states:
    :param attributes:
    :return:
    '''
    # keep track of the introduced characters
    _, _, people_introduced = update_introduced_characters(fillers, people_introduced, people_all)
    # compute people who are gonna appear next
    _, next_fillers = get_filled_state(curr_state, grounding, states, attributes)
    next_characters, _, _ = update_introduced_characters(next_fillers, people_introduced, people_all)
    # make sure they are already introduced
    # otherwise it doesn't make sense to expect the subject to notice inconsistent swapping
    next_characters = people_introduced.intersection(next_characters)

    # get alternative grounding, if exists
    alt_next_grounding, alt_future, condition = generate_alternative_grounding(
        next_characters, grounding, curr_state, people_introduced
    )
    return alt_next_grounding, alt_future, condition, people_introduced




def generate_alternative_grounding(next_characters, grounding, curr_state, people_introduced):
    '''
    generate an alternative grounding by swapping role-filler binding
    e.g. exchange emcee <---> poet
    :param next_characters: the set of people who are gonna show up in the next state
    :param grounding: role-filler bindings
    :param curr_state: the name of the current state
    :param people_introduced: the set of people who are introduced so far
    :return:
    - alt_next_grounding: role-filler bindings (altered from the input grounding)
    - alt_future: the name of the alternative future state, typically the same as curr_state
    - condition: indicate what kind of inconsistency is introduced at the next state
    '''

    # default values
    alt_next_grounding = grounding
    alt_future = 0
    condition = 0
    #
    next_num_introduced_characters = len(next_characters)
    if next_num_introduced_characters > 0:
        # if the next state has >=  2 characters
        if next_num_introduced_characters > 1:
            # get the k characters in the next state
            next_k_characters = list(next_characters)
            k = len(next_k_characters)
            # get their roles
            next_k_roles = []
            for this_char in next_k_characters:
                next_k_roles.append(get_role_of_filler(this_char, grounding))
            # permute the next k characters
            next_k_characters_shuffled = deepcopy(next_k_characters)
            while True:
                np.random.shuffle(next_k_characters_shuffled)
                if next_k_characters_shuffled != next_k_characters: break
            # generate a new grounding
            alt_next_grounding = deepcopy(grounding)
            for i in range(k):
                alt_next_grounding[next_k_roles[i]] = next_k_characters_shuffled[i]
            # handle specs
            condition = 'Permute_fillers'
            alt_future = curr_state

        elif next_num_introduced_characters == 1 and len(people_introduced) > 1:
            # sample an another character
            the_next_character_str = next(iter(next_characters))
            alternative_characters = people_introduced.difference(next_characters)
            alternative_character_str = np.random.choice(list(alternative_characters))
            # find the role of the alternative character
            alternative_character_role = get_role_of_filler(alternative_character_str, grounding)
            the_next_character_role = get_role_of_filler(the_next_character_str, grounding)
            # create a temp grounding that swaps the role
            alt_next_grounding = deepcopy(grounding)
            alt_next_grounding[the_next_character_role] = alternative_character_str
            # handle specs
            condition = 'Alternative_fillers'
            alt_future = curr_state

    return alt_next_grounding, alt_future, condition



def get_role_of_filler(target_filler, grounding):
    '''
    given a role-filler binding, find the role of an input filler
    :param target_filler: an input filler
    :param grounding: a role-filler binding function, assume 1-1
    :return: the role of the input filler
    '''
    for role, filler in grounding.items():
        if filler == target_filler: return role


def update_introduced_characters(temp_fillers, people_introduced, people_all):
    '''
    keep track of the introduced roles, in order to determine filler inconsistent next state is possible
    :param temp_fillers:
    :param people_introduced:
    :param people_all:
    :return:
    '''
    cur_characters = people_all.intersection(set(temp_fillers))
    cur_num_characters = len(cur_characters)
    if cur_num_characters != 0 and cur_characters not in people_introduced:
        people_introduced = people_introduced.union(cur_characters)
    return cur_characters, cur_num_characters, people_introduced


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
    if n == 1 or curr_state == 'END': return 0
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
    return filled, text_split


def attach_role_question_marker(filled_sentence_text, states, curr_state):
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
