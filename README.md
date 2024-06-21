# COMPSs-Reproducibility-Service

How to use:
- Copy the workflow to reproduce into the Workflow folder
- Run the __main__.py file
- The Results/intermediate_files produced by the experiment if any is stored inside the `./Result`

The experiment to be reproduced should follow the following:

- (1) If path to folder is given in the `compss_submission_command_line`, then the path should end with '/'
- (2) It does not works if there is any path given inside the program as it can't map the path
- (3) It does not work with any advance worflow that required third-part dependecies to be installed.

Some example workflows are given inside the: `Works/` directory 

