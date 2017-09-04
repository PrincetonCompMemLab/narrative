Some resources (data and papers) can be found on the <a href = "https://github.com/PrincetonCompMemLab/narrative/wiki">here</a>

1. to generate a bunch of stories: 
  - input: a schema (e.g.: schema/poetry.txt)
  - in the terminal, cd to src, and run "python run_engine.py schema_file1 schema_file2 ... schema_filek n_iter alternating"
  - e.g.: python run_engine.py poetry fight 2 False
  - this procedure generates a file "schema_file_n_iter" under the “story/” directory

2. to clean and post-process the stories
  - input: a text file contains a bunch of stories (from step 1) under the “story/” directory
  - in the terminal, cd to src, and run "python proc_txt.py input_file"
  - e.g. python proc_txt.py poetry_10
  - this procedure generates a directory "input_file/“ under the “story_processed/” directory
