#This is just the basic skeleton the actual program may have different types of imports
import json
import os
import subprocess
import logging

from repro_methods import generate_command_line
from command_executor import executor
from result_mover import move_results_created, dataset_mover_and_application_mover

# Rules:
# (1) If path to folder is given, then the path should end with '/'
# (2) It does not works if there is any path given inside the program as it can't map the path

class ReproducibilityService:
    def __init__(self, root_folder):
        self.root_folder = root_folder
        self.workflow_folder = os.path.join(root_folder, 'Workflow')
        
        # Get the first directory in the Workflow folder { Assuming only crate is inside the workflow folder}
        for filename in os.listdir(self.workflow_folder):
            self.crate_directory = os.path.join(self.workflow_folder, filename)
            break
            
       
        self.log_folder = os.path.join(root_folder, 'log')
        self.log_file = os.path.join(self.log_folder, 'reproducability.log')

    def generate_command_line(self) -> list[str]:
       return generate_command_line(self)

 
    def run(self):
       initial_files = set(os.listdir(os.getcwd()))
       new_command = generate_command_line(self)
       print("Running the command: ", new_command)
       # run the new command
       temp = dataset_mover_and_application_mover(self.crate_directory)
       executor(new_command)
       move_results_created(initial_files,temp)

      
         

if __name__ == "__main__":
    rs = ReproducibilityService(os.getcwd())
    rs.run()
   