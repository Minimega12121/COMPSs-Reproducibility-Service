from utils import print_colored, TextColor, get_objects, get_by_id, get_instument, get_objects_dict, get_results_dict, check_slurm_cluster, executor, get_previous_flags

from rocrate.rocrate import ROCrate
from urllib.parse import urlparse
from get_workflow import get_more_flags, get_change_values
import os
import datetime as dt
import re
import shlex

RESULT_PATH:str = None
OUTPUT_NUM:int = 0


def check_file_accessibility(crate: ROCrate) -> tuple[bool,dict]:
    """
    Check if the specified file paths are accessible.

    Parameters:
    file_paths (list): A list of file paths to check.

    Returns:
    dict: A dictionary with file paths as keys and a boolean indicating if the file is accessible as values.
    """
    file_paths = get_objects(crate)
    accessibility = {}
    flag = True
    for path in file_paths:
        parsed_url = urlparse(path)
        # Remove the 'file://<id>' prefix
        file_path = path.replace(f"file://{parsed_url.netloc}", "")

        if file_path:
            accessibility[file_path] = os.access(file_path, os.R_OK)
            if accessibility[file_path] == False:
                flag = False
                print(file_path+ "\n" + "INACCESSIBLE")
            else:
                print(file_path+ "\n" + "ACCESSIBLE")

    return flag,accessibility

def files_verifier_dpf(crate_path: str):
    """
    Verify files within an RO-Crate against their metadata.

    Args:
        crate_path (str): Path to the root directory of the RO-Crate.
        instrument (str): Identifier of the instrument file within the RO-Crate.
        objects (list[str]): List of identifiers for objects/inputs within the RO-Crate.

    Raises:
        FileNotFoundError: If any referenced file in the RO-Crate does not exist in the directory.
        ValueError:If the content size of any file does not match the recorded size in the RO-Crate.

    Notes:
        This function verifies the existence and size of files referenced in the RO-Crate
        against the actual files in the specified directory. Optionally, it can also verify
        modification dates, although this feature is currently commented out.
    """
    crate = ROCrate(crate_path)
    instrument  = get_instument(crate)
    size_verifier = True
    date_verifier = True
    temp_size = []
    temp_date = []
    crate = ROCrate(crate_path)
    instrument_path = os.path.join(crate_path, instrument)

    if not os.path.getsize(instrument_path) == get_by_id(crate, instrument)["contentSize"]:
        size_verifier = False
        temp_size.append(instrument_path)

    #Verify the objects/inputs
    crate = ROCrate(crate_path)
    file_paths = get_objects(crate)
    for path in file_paths:
        parsed_url = urlparse(path)
        # Remove the 'file://<id>' prefix
        file_path = path.replace(f"file://{parsed_url.netloc}", "")

        file_object = get_by_id(crate, path)

        if "contentSize" in file_object:
            content_size = file_object["contentSize"]
            # Verify the above content size with the actual file size

            # Get the actual file size
            actual_size = os.path.getsize(file_path)

            # Verify the content size with the actual file size
            if actual_size != content_size:
                print(f"Size of {file_path} is incorrect")
                size_verifier = False
                temp_size.append(file_path)
            else:
                print(f"Size of {file_path} is correct")

        actual_modified_date = dt.datetime.utcfromtimestamp(os.path.getmtime(file_path)).replace(microsecond=0).isoformat()
        if "dateModified" in file_object and actual_modified_date != file_object["dateModified"][:-6]:
            print(f"DateModified of {file_path} is incorrect\n")
            date_verifier = False
            temp_date.append(file_path)
        else:
            print(f"DateModified of {file_path} is correct")

    if date_verifier:
        print_colored("All files have correct dateModified", TextColor.GREEN)

    if size_verifier:
        print_colored("All files have correct sizes.", TextColor.GREEN)

    if not size_verifier:
        if not date_verifier:
            raise ValueError(f"Content size mismatch in files: {temp_size}")
        else:
            raise ValueError(f"Content size mismatch in files: {temp_size}\nDateModified mismatch in files: {temp_date}")

    if not date_verifier:
        raise ValueError(f"DateModified mismatch in files: {temp_date}")

def data_persistance_false_verifier(crate_path:str):
    if check_slurm_cluster()[0]:
        print("Slurm cluster")
    else:
        print("Not a Slurm cluster")
        raise ValueError ("The crate was created with data persistence set to false. Please run the crate on the cluster in which the dataset paths are available.")

    crate = ROCrate(crate_path)

    (accessible,access_map) = check_file_accessibility(crate)

    if not accessible:
        print_colored("The following paths are not accessible:",TextColor.RED)
        for p in access_map:
            if not access_map[p]:
                print_colored(p, TextColor.RED)

    else:
        print_colored("All files are accessible", TextColor.GREEN)
        print("Checking file sizes...")
        try:
            files_verifier_dpf(crate_path)
        except ValueError as e:
            print_colored(str(e), TextColor.RED)

def addr_extractor(path: str) -> dict:
    """
    Extracts the addresses of datasets in the given path. For this particular case,
    it is used to extract the mapping of filenames in the crate/dataset and
    crate/application_sources directories.

    Args:
        path (str): The path to the directory containing the datasets.

    Returns:
        dict: A dictionary mapping dataset filenames to a value of 1.
    """
    if not os.path.exists(path):
        os.makedirs(path)
    hash_map = {}
    for filename in os.listdir(path):
        hash_map[filename] = 1

    return hash_map
def address_converter_backend(path: str, addr: str, dataset_hashmap: dict) -> str:
    """
    Converts the given address to a mapped address inside the RO_Crate
    based on the dataset hashmap.

    Args:
        path (str): The base path of the dataset.
        addr (str): The address to be converted.
        dataset_hashmap (dict): A dictionary containing the mapping of dataset addresses.

    Returns:
        str: The mapped address corresponding to the given address.

    Raises:
        FileNotFoundError: If the mapped address for the given address is not found.
    """
    filename = None
    mapped_addr = None

    if addr.startswith("./"):
        addr = addr[1:]

    if not addr.startswith("/"):
        addr = "/" + addr

    # Check if the address is a file or a directory and split it accordingly
    if addr.endswith("/"):
        addr_list = addr.split("/")
    else:
        addr_list = addr.split("/")
        filename = addr_list.pop()

    for i in range(1, len(addr_list)):
        if addr_list[i] in dataset_hashmap:
            temp_addr = os.path.join(path, addr_list[i])
            for j in range(i + 1, len(addr_list)):
                temp_addr = os.path.join(temp_addr, addr_list[j])

            if os.path.exists(temp_addr):
                mapped_addr = temp_addr
                break

    # If the address is a file, append the filename and check if exists
    if filename:
        if not mapped_addr:
            mapped_addr = path
        mapped_addr = os.path.join(mapped_addr, filename)
        if not os.path.exists(mapped_addr):
            return None


    return mapped_addr

def address_mapper_dpf(addr:str, object_list, result_list, application_sources_hash_map: dict, path:str) -> str:
    filename = None
    mapped_addr = None
    application_path = os.path.join(path, "application_sources")

    mapped_addr =  address_converter_backend(application_path, addr, application_sources_hash_map) #check if the path is in application sources inside the crate

    if mapped_addr:
        return mapped_addr # if the path is in application sources then return the path as it is

    if addr.startswith("./"):
        addr = addr[1:]

    if not addr.startswith("/"):
        addr = "/" + addr

    # Check if the address is a file or a directory and split it accordingly
    if addr.endswith("/"):
        addr_list = addr.split("/")
    else:
        addr_list = addr.split("/")
        filename = addr_list.pop()

    print("Addr list is:",addr_list)
    matched_len = -1
    result_flag = False

    for i in range(len(addr_list)-1,-1,-1):
        len_matched_result = 0
        temp_addr_object = None
        len_matched_object = 0
        for ls in result_list:
            if addr_list[i] in ls:
                temp_addr =""
                j= len(ls)-1
                while j>=0 and ls[j] != addr_list[i]:
                    j-=1
                if j==-1: #nothing matched
                    break
                for k in range(0,j+1): # join the complete matched part
                    temp_addr = os.path.join(temp_addr, ls[k])
                len_matched_result = j #storing how much comman is addr with any result path
                for j in range(i + 1, len(addr_list)):
                    temp_addr = os.path.join(temp_addr, addr_list[j])

                if not os.path.exists(f"/{temp_addr}"):
                    len_matched_result = 0

        for ls in object_list:
            if addr_list[i] in ls:
                print(ls)
                temp_addr =""
                j= len(ls)-1
                while j>=0 and ls[j] != addr_list[i]:
                    j-=1
                if j==-1: #nothing matched
                    break
                for k in range(0,j+1): # join the complete matched part
                    temp_addr = os.path.join(temp_addr, ls[k])
                len_matched_object = j #storing how much comman is addr with any result path
                for j in range(i + 1, len(addr_list)):
                    temp_addr = os.path.join(temp_addr, addr_list[j])

                if os.path.exists(f"/{temp_addr}"):
                    temp_addr_object = temp_addr
                else:
                    len_matched_object = 0

        if len_matched_object==0 and len_matched_result ==0:
            continue
        print("length matched result is:",len_matched_result)
        print("length matched object is:",len_matched_object)
        if len_matched_result>len_matched_object:# Assigning the one with more common path
            if len_matched_result>matched_len:
                matched_len = len_matched_result
                mapped_addr = RESULT_PATH
                result_flag = True
        else:
            if len_matched_object>matched_len:
                matched_len = len_matched_object
                mapped_addr = temp_addr_object
                result_flag = False

    if result_flag:
        global OUTPUT_NUM
        os.makedirs(os.path.join(RESULT_PATH,f"new_output_{OUTPUT_NUM}"), exist_ok=True)
        mapped_addr = os.path.join(RESULT_PATH,f"new_output_{OUTPUT_NUM}")
        OUTPUT_NUM+=1
        print(mapped_addr)
        return mapped_addr
    # If the address is a file, append the filename and check if exists
    if mapped_addr and filename:
        mapped_addr = os.path.join(mapped_addr, filename)
        mapped_addr = "/"+mapped_addr
        if not os.path.exists(mapped_addr):
            raise FileNotFoundError(f"Could not find the mapped address for: {addr}")
        else:
            return mapped_addr

    #Could not find such directory or file
    if not mapped_addr:
        # print all above varibles for debugging
        print("Address is:"+addr)
        print("Object list is:",object_list)
        print("Result list is:",result_list)
        print("Application sources hashmap is:",application_sources_hash_map)

        raise FileNotFoundError(f"Could not find the mapped address for: {addr}")

    mapped_addr = "/"+mapped_addr # since in dpf path is always absolute and starts with /
    print("Mapped addr is:"+mapped_addr)

    return mapped_addr

def url_splitter(addr: str)-> list[str]:
    """
    Split the given URL into a list of its components.

    Args:
        addr (str): The URL to split.

    Returns:
        list[str]: A list of the components of the URL.
    """
    parsed_url = urlparse(addr)
    addr = addr.replace(f"file://{parsed_url.netloc}", "")
    if addr.startswith("./"):
        addr = addr[1:]

    if not addr.startswith("/"):
        addr = "/" + addr

    # Check if the address is a file or a directory and split it accordingly
    if addr.endswith("/"):
        addr_list = addr.split("/")
    else:
        addr_list = addr.split("/")
        addr_list.pop()
    addr_list = addr_list[1:]

    return addr_list

def command_line_generator_dpf(command: str,path:str) -> list[str]:
    """
    Generates a modified command line by replacing paths in the command with their
    mapped counterparts based on the dataset and application sources mappings.
    Acts as the main logic behind generate_command_line.

    Args:
        command (str): Original command line string.
        path (str): Path to the RO_Crate directory.
        dataset_hashmap (dict): Hashmap generated from addr_extractor.
        application_sources_hashmap (dict): Hashmap generated from addr_extractor.

    Returns:
        list[str]: Modified command line arguments with mapped paths.
    """
    crate = ROCrate(path)
    objects = get_objects_dict(crate)
    results = get_results_dict(crate)
    application_sources_hashmap = addr_extractor(os.path.join(path, "application_sources"))
    result_list = []
    object_list = []

    for _,val in objects.items():
        # print(val)
        print(url_splitter(val))
        object_list.append(url_splitter(val))

    for _,val in results.items():
        # print(val)
        print(url_splitter(val))
        result_list.append(url_splitter(val))

    object_list = [item for item in object_list if item not in result_list]
    print(object_list)
    print(result_list)
    command = shlex.split(command)
    flags = []
    paths = []
    values = []

    for i, cmd in enumerate(command):
        if cmd.startswith("--") or cmd.startswith("-"):
            if not (cmd.startswith("--provenance") or cmd.startswith("-p")):
                flags.append((cmd, i))
        elif re.compile(r'[/\\]').search(cmd): # Pattern for detecting paths
            paths.append((cmd, i))
        else:
            values.append((cmd, i))

    new_paths = []

    for filepath in paths:
        new_filepath = address_mapper_dpf(filepath[0], object_list, result_list, application_sources_hashmap, path)
        new_paths.append((new_filepath, filepath[1]))

    paths = new_paths

    p1 = 0
    p2 = 0

    new_command = []

    while p1 < len(paths) and p2 < len(values):
        if paths[p1][1] < values[p2][1]:
            new_command.append(paths[p1][0])
            p1 += 1
        else:
            new_command.append(values[p2][0])
            p2 += 1

    while p1 < len(paths):
        new_command.append(paths[p1][0])
        p1 += 1

    while p2 < len(values):
        new_command.append(values[p2][0])
        p2 += 1


    new_command[0] = "enqueue_compss"

    return new_command

def run_dpf(EXECUTION_PATH:str, crate_path: str) ->bool:
    try:
        global RESULT_PATH
        RESULT_PATH = os.path.join(EXECUTION_PATH,"Result")
        compss_submission_command_path = os.path.join(crate_path, "compss_submission_command_line.txt")

        with open(compss_submission_command_path, 'r', encoding='utf-8') as file:
            compss_submission_command = next(file).strip()

        new_command = command_line_generator_dpf(compss_submission_command,crate_path)
        print("New command is:",new_command)
        previous_flags = get_previous_flags(crate_path) # get the flags from the previous command
        new_command = get_more_flags(new_command, previous_flags) # ask user for more flags he/she wants to add to the final compss command

        new_command = get_change_values(new_command)

        result = executor(new_command,EXECUTION_PATH)

        return result
    except Exception as e:
        print_colored(e, TextColor.RED)
        return False


