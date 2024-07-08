import os
import yaml
import shutil
import subprocess
import threading
import time

from ruamel.yaml import YAML
from rocrate.rocrate import ROCrate


class TextColor:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_colored(text, color):
    print(f"\n{color}{text}{TextColor.RESET}\n")

def get_by_id(entity:ROCrate, id:str):
    # Loop through all entities in the RO-Crate
    for entity in entity.get_entities():
        if entity.id == id:
            return entity
    return None

def get_Create_Action(entity:ROCrate):
    # Loop through all entities in the RO-Crate
    for entity in entity.get_entities():
        if entity.type == "CreateAction":
            return entity
    return None

def get_instument(entity:ROCrate):
    createAction = get_Create_Action(entity)
    return createAction["instrument"].id

def get_objects(entity:ROCrate):
    createAction = get_Create_Action(entity)
    objects= []
    try: # It is not necessary to have inputs/objects in Create Action
        temp = createAction["object"]
    except:
        return None

    for val in temp:
        objects.append(val.id)
    return objects

def get_yes_or_no(msg :str) :
    while True:
        user_input = input(f"{msg} (y/n):").lower()
        if user_input == 'y' or user_input == 'n':
            if user_input == 'y':
                return True
            else:
                return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def get_data_persistence_status(crate_path:str) -> bool:
    #It may not be named ro-crate-info.yaml, eg: 838-1 crate
    yaml_file_path = None
    for name in os.listdir(crate_path):
        if name.endswith(".yaml"):
            yaml_file_path = f"{crate_path}/{name}"
            break
    if not yaml_file_path:
        raise FileNotFoundError("ro-crate-info.yaml file not found in the crate")
    # Open and read the YAML file
    with open(yaml_file_path, 'r') as file:
        # Load the content of the YAML file
        config = yaml.safe_load(file)
    # Extract the value of data_persistence
    data_persistence = config.get('COMPSs Workflow Information', {}).get('data_persistence', None)

    return data_persistence

def get_name_and_description(crate_path: str) -> tuple[str, str]:
     #It may not be named ro-crate-info.yaml, eg: 838-1 crate
    yaml_file_path = None
    for name in os.listdir(crate_path):
        if name.endswith(".yaml"):
            yaml_file_path = f"{crate_path}/{name}"
            break
    if not yaml_file_path:
        raise Exception("ro-crate-info.yaml file not found in the crate")
    # Open and read the YAML file
    with open(yaml_file_path, 'r') as file:
        # Load the content of the YAML file
        data = YAML().load(file)

    # Extract name and description
    name = data['COMPSs Workflow Information'].get('name', '')
    description = data['COMPSs Workflow Information'].get('description', '')

    return name, description

def get_ro_crate_info():
    """
    Copies a ro-crate-info.yaml files to the current working directory.

    """
    source = "./APP-REQ/ro-crate-info.yaml"
    # Get the current working directory
    cwd = os.getcwd()

    # Get the base name of the source file
    file_name = os.path.basename(source)

    # Construct the full destination path
    destination = os.path.join(cwd, file_name)

    try:
        # Copy the file to the current working directory
        shutil.copy(source, destination)
        print(f'ro-crate-info.yaml file copied to the current working directory.')
    except Exception as e:
        print(f'Error copying ro-crate-info.yaml file from {source}: {e}')


def executor(command: list[str]):
    joined_command = " ".join(command)
    print_colored(f"Executing command: {joined_command}", TextColor.BLUE)

    # Create log directory if it doesn't exist
    log_dir = os.path.join(os.getcwd(), "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create unique log file names
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    stdout_log = os.path.join(log_dir, f"out_{timestamp}.log")
    stderr_log = os.path.join(log_dir, f"err_{timestamp}.log")

    # Start the subprocess
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Define functions to read and log output
    def read_stdout(pipe, log_file):
        with open(log_file, 'w') as f:
            for line in iter(pipe.readline, ''):
                print(line.strip())
                f.write(line)
        pipe.close()

    def read_stderr(pipe, log_file):
        with open(log_file, 'w') as f:
            for line in iter(pipe.readline, ''):
                print(line.strip())
                f.write(line)
        pipe.close()

    # Create threads to read and log stdout and stderr
    stdout_thread = threading.Thread(target=read_stdout, args=(process.stdout, stdout_log))
    stderr_thread = threading.Thread(target=read_stderr, args=(process.stderr, stderr_log))

    stdout_thread.start()
    stderr_thread.start()

    # Wait for the process to complete
    process.wait()

    # Ensure all output has been logged
    stdout_thread.join()
    stderr_thread.join()

    # Print log file locations
    print(f"Standard output logged to: {stdout_log}")
    print(f"Standard error logged to: {stderr_log}")

    # Check the return code
    if process.returncode == 0:
        print("Command executed successfully.")
        return True
    else:
        print("Command failed with return code:", process.returncode)
        return False


