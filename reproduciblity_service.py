import os
import sys
import time
from rocrate.rocrate import ROCrate

from repro_methods import generate_command_line
from file_operations import move_results_created, dataset_mover_and_application_mover, remote_dataset_mover
from file_verifier import files_verifier
from utils import get_instument, get_objects,get_objects_dict,print_colored, TextColor, get_data_persistence_status, executor, get_yes_or_no
from new_dataset_backend import new_dataset_info_collector
from provenance_backend import provenance_info_collector, update_yaml, provenance_checker
from get_workflow import get_workflow
from remote_dataset import remote_dataset


# User-guidelines:
# (1) If path to folder is given, then the path should end with '/'
# (2) It does not works if there is any path given inside the program as it can't map the path

class ReproducibilityService:
    def __init__(self, root_folder, provenance_flag:bool, new_dataset_flag:bool):
        self.provenance_flag = provenance_flag
        self.new_dataset_flag = new_dataset_flag
        self.root_folder = root_folder
        self.workflow_folder = os.path.join(root_folder, 'Workflow')

        if len(os.listdir(self.workflow_folder)) == 0:
            print_colored("ERROR| No crate found in the workflow folder.", TextColor.RED)
            sys.exit(1)

        # Get the first directory in the Workflow folder {Assuming only crate is inside the workflow folder}
        self.crate_directory = os.path.join(self.workflow_folder, os.listdir(self.workflow_folder)[0])

        try:
            if not get_data_persistence_status(self.crate_directory):
                raise FileNotFoundError("ERROR| Data persistence is False in the crate, cannot reproduce such a workflow.")


            if new_dataset_flag:
                new_dataset_info_collector(self.crate_directory)
            else: # verify the metadata only if the old dataset is used
                print("Reproducing the crate on the old dataset.")
                crate = ROCrate(self.crate_directory)
                instrument= get_instument(crate)
                objects= get_objects_dict(crate)
                # download the remote data-set if it exists and return true if it exists
                (self.remote_dataset_flag, remote_dataset_dict) = remote_dataset(crate)
                files_verifier(self.crate_directory, instrument, objects, remote_dataset_dict)
            if provenance_flag: #update the sorces inside the yaml file
                update_yaml(self.crate_directory)

        except Exception as e:
            print_colored(e,TextColor.RED)
            sys.exit(1)

        self.log_folder = os.path.join(root_folder, 'log')
        self.log_file = os.path.join(self.log_folder, 'reproducability.log')

    def run(self):
       initial_files = set(os.listdir(os.getcwd()))
       new_command = generate_command_line(self)

       if self.provenance_flag: # add the provenance flag to the command
           new_command.insert(1, "--provenance")
       # for debugging: new_command.insert(1, "-d")
       # run the new command
       temp = dataset_mover_and_application_mover(self.crate_directory)
       if self.remote_dataset_flag:
           temp = temp.union(remote_dataset_mover(os.getcwd()))
       result = executor(new_command)
       move_results_created(initial_files,temp)
       return result

if __name__ == "__main__":

    try:
        get_workflow()
    except Exception as e:
        print_colored(e,TextColor.RED)
        sys.exit(1)

    new_dataset_flag = get_yes_or_no("Do you want to reproduce the crate on a new dataset?")
    provenance_flag = provenance_info_collector()

    rs = ReproducibilityService(os.getcwd(),provenance_flag, new_dataset_flag)
    result = rs.run()
    if result:
        print_colored("Reproducibility Service has been executed successfully", TextColor.GREEN)
    else:
        print_colored("Reproducibility Service has been failed", TextColor.RED)

    if provenance_flag:
       provenance_checker()

    sys.exit(0)
