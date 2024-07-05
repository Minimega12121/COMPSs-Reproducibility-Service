# COMPSs-Reproducibility-Service

How to use:
- Copy the workflow to reproduce into the Workflow folder (should be one at a time)
- Run the __main__.py file
- The Results/intermediate_files produced by the experiment if any is stored inside the `./Result`

How to enable provenance generation:
- The program will ask if you want to generate the provenance or not, at the start
- Say yes(y) and fill the ro-crate-info.yaml file with your information
- Currently only data persistance false provenance is generated
- name,description,source,and source_main_file will be automatically filled by the RS Service
- The provenance crate produced will be inside `Result/`after execution

How to reproduce using new_dataset:
- The program will ask if you want to use new_dataset or old at the start
- Say yes(y) and the it will output the old dataset directory structure as a reference.
- Copy the new_dataset inside the `new_dataset/` created in the directory
- WARNING| MAKE SURE THE NEW DATASET FOLLOWS THE SAME DIRECTORY STRUCTURE AS THE OLD DATASET
- If there is any logical difference between the old and new dataset in context of the program, it might fail.

The experiment to be reproduced should follow the following:

- (1) If path to folder is given in the `compss_submission_command_line`, then the path should end with '/'
- (2) It does not works if there is any path given inside the program as it can't map the path
- (3) It does not work with any advance worflow that required third-part dependecies to be installed.
- (4) The crate to be reproduced should have `Data Persistance:True` for reproducibility

Some example workflows are given inside the: `Works/` directory

