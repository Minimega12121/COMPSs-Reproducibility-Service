#This is just the basic skeleton the actual program may have different types of imports
import json
import os
import subprocess
import logging

from repro_methods import parse_metadata

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

    def parse_metadata(self):
        parse_metadata(self)

    def generate_automate_sh(self):
        # Generate automate.sh script with CLI commands from app-req.txt
        pass

    def generate_dockerfile(self):
        # Generate Dockerfile with automate.sh as RUN command
        pass

    def build_docker_image(self):
        # Build Docker image using the generated Dockerfile
        pass  
    def run(self):
        # Execute the reproducibility process
        logging.basicConfig(filename=self.log_file, level=logging.INFO)
        try:
            self.parse_metadata()
            # self.generate_automate_sh()
            # self.generate_dockerfile()
            # self.build_docker_image()
            logging.info('Reproducibility process completed successfully.')
        except Exception as e:
            logging.error(f'Error during reproducibility process: {str(e)}')
# Checks whether current program runs as the main program or if it's being imported as a module to another script
if __name__ == "__main__":
    # Create the object while passing the path to root directory
    rs = ReproducibilityService(os.getcwd())
    # Run the reproducibility process
    rs.run()
