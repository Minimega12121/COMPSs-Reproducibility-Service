import os
import shutil
import time

from rocrate.rocrate import ROCrate
from ruamel.yaml import YAML

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
    
def update_yaml(crate_path: str):
    crate = ROCrate(crate_path)
    instrument = get_instument(crate)
    sources_main_file = os.path.join(crate_path, instrument)
    sources = os.path.join(crate_path, "application_sources")
    name, description = get_name_and_description(crate_path)
    # Create a YAML instance
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml_file_path = './ro-crate-info.yaml'
    # Read the YAML content from the file
    with open(yaml_file_path, 'r') as file:
        data = yaml.load(file)
    
    # Update the name and description fields
     # Update the fields in the loaded YAML content
    data['COMPSs Workflow Information']['sources'] = sources
    data['COMPSs Workflow Information']['sources_main_file'] = sources_main_file   
    data['COMPSs Workflow Information']['name'] = name
    data['COMPSs Workflow Information']['description'] = description
    
    # Write the updated dictionary back to the YAML file
    with open(yaml_file_path, 'w') as file:
        yaml.dump(data, file)
    
    print("YAML file updated successfully.")

def get_Create_Action(entity:ROCrate):
    # Loop through all entities in the RO-Crate
    for entity in entity.get_entities():
        if entity.type == "CreateAction":
            return entity
    return None
def get_instument(entity:ROCrate):
    createAction = get_Create_Action(entity)
    return createAction["instrument"].id

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
        
def provenance_info_collector() -> bool:
    provenance_flag = get_yes_or_no("Do you want to see the provenance of the workflow?")
    print(provenance_flag)
    if provenance_flag:
        current_dir = os.getcwd()
        files = os.listdir(current_dir)
        already_exists = "ro-crate-info.yaml" in files
        time.sleep(1)
        if not already_exists :
            get_ro_crate_info()
            print("Please fill the ro-crate-info.yaml file, generated inside the current working directory.")
            time.sleep(1) 
            check = False
            while not check:
                time.sleep(1)
                check = get_yes_or_no("Have you filled the ro-crate-info.yaml file for provenance generation?")
        else:
            print("ro-crate-info.yaml file already exists in the current working directory.")
            check = get_yes_or_no("Please check if the already existing ro-crate-info.yaml file is correctly filled for provenance generation")
            
            if not check:
                get_ro_crate_info()
                time.sleep(1)
                print("Please fill the new ro-crate-info.yaml file, generated inside the current working directory.")
                check = False
                while not check:
                    time.sleep(1)
                    check = get_yes_or_no("Have you filled the ro-crate-info.yaml file for provenance generation?")
                    
        print("Considering the filled information for provenance generation.")
        
        return provenance_flag