## Resources 

Some related papers and data sets can be found <a href = "https://github.com/PrincetonCompMemLab/narrative/wiki">here</a>
<br><br>

## Slides from Sep 2017 Princeton meeting:  

History, current status, and future of coffee shop world (7:30-8:15pm)
- Alex - The coffee shop story generator - [slides](https://github.com/ProjectSEM/Organization/blob/master/slides/sep_2017/storygeneration_MURI.pdf) 
- Andre - Behavioral experiments - [slides](https://github.com/ProjectSEM/Organization/blob/master/slides/sep_2017/andre_MURI_d1.pdf) 
- Qihong - Neural networks for schema learning - [slides](https://github.com/ProjectSEM/Organization/blob/master/slides/sep_2017/0917-MURI_Lu.pdf) 
<br><br>

## The coffee shop world "engine" 

The "engine" takes a schema and generates a bunch of stories! Concretely, a schema is a graph {V,E} representing some states and transitions. Each state is a sentence that can be binded with some role fillers. For example, 
<br>

**1. Generate stories** `run_engine.py`

Currently, we have two schema: "poetry reading" and "fight". Here's an exmaple of poetry reading: 

*Mariko walked into the coffee shop on poetry night. She found an empty chair next to Sarah. "Oh hi there Mariko!" said Sarah. "I am glad you could make it Sarah!" Mariko replied. Olivia, who was the emcee for tonight, walked to the front of the room and introduced the first poet, Julian. Julian stepped up to the microphone and read the poem that he had written: "I wandered lonely as a cloud that floats on high over vales and hills, when all at once I saw a crowd, A host, of golden daffodils." The crowd snapped their fingers politely. Mariko had also written a poem, but decided that she was not in the mood to share it today. After all the poets had performed, Mariko and Sarah said their goodbyes and walked toward the door. Mariko made a mental note to come back again next week.*

**how to use**

In the terminal, cd to `\src`, and run the cmd with the following format 
```
python run_engine.py [schema_file_1] [schema_file_2] ... [schema_file_k] [niter] [nrepeats]"
```
where, `schema_file_i` is a txt schema file, `n_iter` is the number of stories and `alternating` is a boolean value that indicates if the generated stories will alternate across the k schemas. For example, the following command generate 8 stories (alternating between 2 poetry stories and 2 fight stories for 2 iterations).
```
python run_engine.py poetry fight 2 2
```
After running the cmd, you will see a file called `schemaFiles_niter_nrepeats.txt` under the `story/` directory

**Functionalties to be added**: 
- [ ] plot the graph of the schema (markov model)
- [ ] add "higher order schema"
<br><br><br>

**2. post-processing** `proc_txt.py`

**how to use**

Having generated a text file contains a bunch of stories (from step 1) under the `story/` directory, in the terminal, cd to `\src`, and run the cmd with the following format 
```
python proc_txt.py input_file
```
where `input_file` is the stories file you got from step 1. For example, the following cmd is valid:
```
python proc_txt.py poetry_fight_2_2
```
This procedure generates a directory `input_file/` under the `story_processed/` directory


**Functionalities**: 
- [x] separate training vs. test set and save to .npz file 
- [x] remove punctuations marks
- [x] transform characters to lower case
- [x] insert state/story boundaries
- [x] convert character representations to word representations
- [x] alternate between k schema
- [x] shuffle/reverse the order of words within each state 
- [x] shuffle/reverse the order of sentences within each story
    - [ ] shuffle/reverse every k-words segment (Amy)

Let me know if you have more suggestions - qlu@princeton.edu
