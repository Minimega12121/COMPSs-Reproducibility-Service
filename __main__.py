#This is just the basic skeleton the actual program may have different types of imports
import json
import os
import subprocess
import logging

from repro_methods import generate_command_line
from command_executor import executor

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
       new_command = generate_command_line(self)
       # run the new command
       executor(new_command)
         

if __name__ == "__main__":
    rs = ReproducibilityService(os.getcwd())
    rs.run()
