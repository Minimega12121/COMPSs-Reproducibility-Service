import os
import sys
from rocrate.rocrate import ROCrate

from repro_methods import generate_command_line
from file_operations import move_results_created, dataset_mover_and_application_mover
from file_verifier import files_verifier
from utils import get_instument, get_objects, print_colored, TextColor, get_data_persistence_status, executor
from provenance_backend import provenance_info_collector, update_yaml


# Rules:
# (1) If path to folder is given, then the path should end with '/'
# (2) It does not works if there is any path given inside the program as it can't map the path

class ReproducibilityService:
    def __init__(self, root_folder, provenance_flag:bool):
        self.provenance_flag = provenance_flag
        self.root_folder = root_folder
        self.workflow_folder = os.path.join(root_folder, 'Workflow')

        # Get the first directory in the Workflow folder { Assuming only crate is inside the workflow folder}
        for filename in os.listdir(self.workflow_folder):
            self.crate_directory = os.path.join(self.workflow_folder, filename)
            break
        # Cannot reproduce the workflow if data persistence is False as of now
        try:
            if not get_data_persistence_status(self.crate_directory):
                raise Exception("ERROR| Data persistence is False in the crate, cannot reproduce such a workflow.")

            crate = ROCrate(self.crate_directory)
            instrument= get_instument(crate)
            objects= get_objects(crate)
            files_verifier(self.crate_directory, instrument, objects)

            if provenance_flag: #update the sorces inside the yaml file
                update_yaml(self.crate_directory)
        except Exception as e:
            print_colored(e,TextColor.RED)
            sys.exit(1)

        self.log_folder = os.path.join(root_folder, 'log')
        self.log_file = os.path.join(self.log_folder, 'reproducability.log')

    def generate_command_line(self) -> list[str]:
       return generate_command_line(self)


    def run(self):
       initial_files = set(os.listdir(os.getcwd()))
       new_command = generate_command_line(self)

       if self.provenance_flag: # add the provenance flag to the command
           new_command.insert(1, "--provenance")

       print("\nSubmitting the command to COMPSs Runtime:\n", (" ").join(new_command),"\n")
       # run the new command
       temp = dataset_mover_and_application_mover(self.crate_directory)
       executor(new_command)
       move_results_created(initial_files,temp)

if __name__ == "__main__":
    provenance_flag = provenance_info_collector()
    rs = ReproducibilityService(os.getcwd(),provenance_flag)
    rs.run()
    print_colored("Reproducibility Service has been executed successfully", TextColor.GREEN)

    if provenance_flag:
        if not os.path.exists('Result'):
            os.makedirs('Result')
        contains_crate = any(name.startswith('COMPSs_RO-Crate_') for name in os.listdir(f'Result/') if os.path.isdir(os.path.join('Result/', name)))

    if provenance_flag and contains_crate:
        print_colored("RO_CRATE has been generated successfully inside 'Result/'", TextColor.GREEN)
    else:
        print_colored("Could not generate the RO_CRATE for provenance, please see the above provenance log for more details", TextColor.RED)

    sys.exit(0)