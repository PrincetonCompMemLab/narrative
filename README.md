resources can be found on the <a href = "https://github.com/PrincetonCompMemLab/narrative/wiki">wiki page</a>

1. to generate a bunch of stories: 
  - input: a schema (e.g.: schema/poetry.txt)
  - in the terminal, cd to src, and run "python run_engine.py schema_file1 schema_file2 ... schema_filek n_iter alternating"
  - e.g.: python run_engine.py poetry fight 2 False
  - this procedure generates a file "schema_file_n_iter" under the story directory

2. to clean the stories file 
  - input: a text file contains a bunch of stories (from step 1) under the story directory
  - in the terminal, cd to src, and run "python clean_txt.py input_file"
  - e.g. python clean_txt.py poetry_10
  - this procedure generates a file "input_file_clean" under story_processed directory
