import os
import sys
import signal
from rocrate.rocrate import ROCrate

from reproducibility_methods import generate_command_line
from file_operations import move_results_created, dataset_mover_and_application_mover, cleanup,create_new_execution_directory, remote_dataset_mover
from file_verifier import files_verifier
from utils import get_instument,get_objects_dict,print_colored, TextColor, get_data_persistence_status, executor, get_yes_or_no, check_compss_version, get_compss_crate_version
from utils import check_slurm_cluster, get_previous_flags
from new_dataset_backend import new_dataset_info_collector
from provenance_backend import provenance_info_collector, update_yaml, provenance_checker
from get_workflow import get_workflow, get_more_flags, get_change_values
from remote_dataset import remote_dataset
from data_persistance_false import data_persistance_false_verifier, run_dpf

SUB_DIRECTORY_PATH:str = None
SERVICE_PATH:str = None
CLEAN_UP_FILES = set()
COMPSS_VERSION:float = None
SLURM_CLUSTER:bool = None
DPF: bool = False
CRATE_PATH: str = None

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
    def __init__(self, provenance_flag:bool, new_dataset_flag:bool) -> bool:
        global CRATE_PATH
        self.crate_directory = CRATE_PATH
        self.provenance_flag = provenance_flag
        self.new_dataset_flag = new_dataset_flag
        self.root_folder = SERVICE_PATH
        self.remote_dataset_flag = False

        crate_compss_version:str = get_compss_crate_version(self.crate_directory)
        print(f"COMPSs VERSION USED INSIDE CRATE: {crate_compss_version}")
        # not using currently to run 3.3.1,3.3 examples on a 3.3 or 3.3.1 compss machine
        # if COMPSS_VERSION != crate_compss_version or get_data_persistence_status(self.crate_directory):
        #     print_colored(f"ERROR| The crate was created with a different version of COMPSs ({get_compss_crate_version(self.crate_directory)}).", TextColor.RED)
        #     sys.exit(1)

        try:
            if not get_data_persistence_status(self.crate_directory):
                data_persistance_false_verifier(self.crate_directory)
                global DPF
                DPF = True
                return

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

        self.log_folder = os.path.join(SUB_DIRECTORY_PATH, 'log')

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

            previous_flags = get_previous_flags(self.crate_directory)# get the previous flags to show the user as reference
            new_command = get_more_flags(new_command, previous_flags) # ask user for more flags he/she wants to add to the final compss command

            new_command = get_change_values(new_command)

            result = executor(new_command,SUB_DIRECTORY_PATH)
            move_results_created(initial_files,CLEAN_UP_FILES, SUB_DIRECTORY_PATH)

            return result

        except Exception as e:
            print_colored(e, TextColor.RED)
            print("Cleaning up intermediate files...")
            cleanup(CLEAN_UP_FILES)
            return False

if __name__ == "__main__":
    try:
        new_dataset_flag = False
        provenance_flag = False
        COMPSS_VERSION:float = check_compss_version() # To check if compss is installed, if yes extract the version, else exit the program
        SLURM_CLUSTER = check_slurm_cluster()[0] # To check if the program is running on the SLURM cluster
        print("Slurm cluster:",SLURM_CLUSTER)
        SERVICE_PATH= os.path.dirname(os.path.abspath(__file__))
        print("Service path is:",SERVICE_PATH)
        SUB_DIRECTORY_PATH = create_new_execution_directory(SERVICE_PATH)
        print("Sub-directory path is:",SUB_DIRECTORY_PATH)
        os.chdir(SUB_DIRECTORY_PATH)

        link_or_path =  sys.argv[1] # take the link or path given by the user
        print(f"Source for crate: {link_or_path}")
        CRATE_PATH = get_workflow(SUB_DIRECTORY_PATH, link_or_path )
        print("Crate path is:",CRATE_PATH)
        if not SLURM_CLUSTER:
            new_dataset_flag = get_yes_or_no("Do you want to reproduce the crate on a new dataset?")

        if not SLURM_CLUSTER:
            provenance_flag = provenance_info_collector(SUB_DIRECTORY_PATH, SERVICE_PATH)

        rs = ReproducibilityService(provenance_flag, new_dataset_flag)
        result = False #default value
        if DPF:
            print(rs.crate_directory)
            result = run_dpf(SUB_DIRECTORY_PATH, rs.crate_directory)
        else:
            result = rs.run()
        if result:
            print_colored("Reproducibility Service has been executed successfully", TextColor.GREEN)
        else:
            print_colored("Reproducibility Service has been failed", TextColor.RED)

        if provenance_flag:
            provenance_checker(SUB_DIRECTORY_PATH)

    except Exception as e:
        print_colored(e,TextColor.RED)
        sys.exit(1)

    sys.exit(0)
# remote_dataset_example: https://workflowhub.eu/workflows/1072/ro_crate?version=1
# basic_example: https://workflowhub.eu/workflows/710/ro_crate?version=1