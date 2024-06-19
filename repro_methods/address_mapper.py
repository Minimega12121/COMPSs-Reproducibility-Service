    
# Problems: IF THE DIRECTORY IS TAKEN IN THE FORM OF DATA/INPUT INSTED OF DATA/INPUT/ THEN IT WILL NOT BE ABLE TO FIND THE DIRECTORY 
# DO NOT INCLUDE DOUBLE SLASHES IN THE PATHS LIKE INPUT//TEXT.TXT IT WILL NOT FIND IT
import os

def check_is_true(path:str) -> bool:
    if os.path.exists(path):
        return True
    else:
        return False

def addr_extractor(path:str) -> dict:
    """
    Extracts the addresses of datasets in the given path.

    Args:
        path (str): The path to the directory containing the datasets.

    Returns:
        dict: A dictionary mapping dataset filenames to a value of 1.
    """
    if os.path.exists(path) == False:
        os.makedirs(path)
    hashMAP = {}
    for filename in os.listdir(path):
        hashMAP[filename] = 1
    
    return hashMAP

def address_converter_backend(path, addr: str, dataset_hashmap: dict) -> str:
    """
    Converts the given address to a mapped address based on the dataset hashmap.

    Args:
        path (str): The base path of the dataset.
        addr (str): The address to be converted.
        dataset_hashmap (dict): A dictionary containing the mapping of dataset addresses.

    Returns:
        str: The mapped address corresponding to the given address.

    Raises:
        Exception: If the mapped address for the given address is not found.
    """
    filename = None
    mapped_addr = None
    
    if addr.startswith("./"):
        addr = addr[2:]

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
            if check_is_true(temp_addr):
                mapped_addr = temp_addr
                break


    # If the address is a file, append the filename and check if exists
    if filename:
        if not mapped_addr:
            mapped_addr = path
        mapped_addr = os.path.join(mapped_addr, filename)
        if not check_is_true(mapped_addr):
            raise Exception(f"Could not find the mapped address for: {addr}")
        
    # Could not find such directory or file
    if not mapped_addr:
        raise Exception(f"Could not find the mapped address for: {addr}")


    return mapped_addr

def address_converter(path: str, addr: str, dataset_hashmap: dict, application_sources_hashmap: dict) -> str:
    dataset_path = os.path.join(path, "dataset")
    application_sources_path = os.path.join(path, "application_sources")
    try:
        # First, check if the address is in the dataset
        return address_converter_backend(dataset_path, addr, dataset_hashmap)
    except Exception as e1:
        try:
            # If the dataset address conversion fails, try the application sources
            return address_converter_backend(application_sources_path, addr, application_sources_hashmap)
        except Exception as e2:
            # If both fail, raise an exception
            raise Exception(f"Could not find the mapped address for: {addr}\nDataset Error: {e1}\nApplication Sources Error: {e2}")


