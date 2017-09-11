resources can be found on the <a href = "https://github.com/PrincetonCompMemLab/narrative/wiki">wiki page</a>

1. to generate a bunch of stories: 
in the terminal, cd to `\src`, and run the cmd with the following format 
```
python run_engine.py [schema_file_1] [schema_file_2] ... [schema_file_k] [n_iter] [alternating]"
```
where, `schema_file_i` is a txt schema file, `n_iter` is the number of stories and `alternating` is a boolean value that indicates if the generated stories will alternate across the k schemas. For example, the following command generate 4 stories alternating between poetry and fight.
```
python run_engine.py poetry fight 2 True
```
After running the cmd, you will see a file called `schema_file_n_iter.txt` under the `story/` directory

2. to clean and post-process the stories
having generated a text file contains a bunch of stories (from step 1) under the `story/` directory, in the terminal, cd to `\src`, and run the cmd with the following format 
```
python proc_txt.py input_file
```
where `input_file` is the stories file you got from step 1. For example, the following cmd is valid:
```
python proc_txt.py poetry_10
```
This procedure generates a directory `input_file/` under the `story_processed/` directory
