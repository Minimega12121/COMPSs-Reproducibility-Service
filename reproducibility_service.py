import os
import sys
import signal
from rocrate.rocrate import ROCrate

from repro_methods import generate_command_line
from file_operations import move_results_created, dataset_mover_and_application_mover, cleanup,create_new_execution_directory, remote_dataset_mover
from file_verifier import files_verifier
from utils import get_instument,get_objects_dict,print_colored, TextColor, get_data_persistence_status, executor, get_yes_or_no
from new_dataset_backend import new_dataset_info_collector
from provenance_backend import provenance_info_collector, update_yaml, provenance_checker
from get_workflow import get_workflow, get_more_flags, get_change_values
from remote_dataset import remote_dataset

EXECUTION_PATH = None
SERVICE_PATH = None
CLEAN_UP_FILES = set()

# remote_dataset and new_dataset are put inside the crate, ro-crate-info.yaml is in the cwd,
# files are copied and removed from cwd(), APP-REQ pasted inside the execution path
# log created inside EXECUTIPN_PATH/log

def interrupt_handler(signal, frame): # signal handler for cleaning up in case of an interrupt
    print_colored("Reproducibility Service has been interrupted.", TextColor.RED)
    if len(CLEAN_UP_FILES)>0:
        try:
            print("Cleaning up intermediate files...")
            cleanup(CLEAN_UP_FILES)
        except Exception as e:
            print_colored(e, TextColor.RED)
            print_colored("Failed to clean up the execution directory.", TextColor.RED)

    print_colored("Exiting the program.", TextColor.RED)
    sys.exit(0)

signal.signal(signal.SIGINT, interrupt_handler) # register the signal handler


class ReproducibilityService:
    def __init__(self, provenance_flag:bool, new_dataset_flag:bool):
        self.provenance_flag = provenance_flag
        self.new_dataset_flag = new_dataset_flag
        self.root_folder = SERVICE_PATH
        self.workflow_folder = os.path.join(EXECUTION_PATH, 'Workflow')
        self.remote_dataset_flag = False

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
                (self.remote_dataset_flag, remote_dataset_dict) = remote_dataset(crate, self.crate_directory)
                files_verifier(self.crate_directory, instrument, objects, remote_dataset_dict)
            if provenance_flag: #update the sorces inside the yaml file
                update_yaml(self.crate_directory)

        except Exception as e:
            print_colored(e,TextColor.RED)
            sys.exit(1)

        self.log_folder = os.path.join(EXECUTION_PATH, 'log')

    def run(self):
        try:
            initial_files = set(os.listdir(os.getcwd()))
            new_command = generate_command_line(self)

            if self.provenance_flag: # add the provenance flag to the command
                new_command.insert(1, "--provenance")
            # for debugging: new_command.insert(1, "-d")
            # run the new command
            global CLEAN_UP_FILES
            CLEAN_UP_FILES = dataset_mover_and_application_mover(self.crate_directory)
            if self.remote_dataset_flag:
                CLEAN_UP_FILES = CLEAN_UP_FILES.union(remote_dataset_mover(self.crate_directory))

            new_command = get_more_flags(new_command) # ask user for more flags he/she wants to add to the final compss command
            
            new_command = get_change_values(new_command)

            result = executor(new_command,EXECUTION_PATH)
            move_results_created(initial_files,CLEAN_UP_FILES, EXECUTION_PATH)
            return result

        except Exception as e:
            print_colored(e, TextColor.RED)
            print("Cleaning up intermediate files...")
            cleanup(CLEAN_UP_FILES)
            return False


if __name__ == "__main__":

    SERVICE_PATH= os.path.dirname(os.path.abspath(__file__))
    print("Service path is:",SERVICE_PATH)
    EXECUTION_PATH = create_new_execution_directory(SERVICE_PATH)
    print("Execution path is:",EXECUTION_PATH)

    try:
        get_workflow(EXECUTION_PATH)
    except Exception as e:
        print_colored(e,TextColor.RED)
        sys.exit(1)

    new_dataset_flag = get_yes_or_no("Do you want to reproduce the crate on a new dataset?")
    provenance_flag = provenance_info_collector(EXECUTION_PATH)

    rs = ReproducibilityService(provenance_flag, new_dataset_flag)
    result = rs.run()
    if result:
        print_colored("Reproducibility Service has been executed successfully", TextColor.GREEN)
    else:
        print_colored("Reproducibility Service has been failed", TextColor.RED)

    if provenance_flag:
       provenance_checker(EXECUTION_PATH)

    sys.exit(0)
# remote_dataset_example: https://workflowhub.eu/workflows/1072/ro_crate?version=1