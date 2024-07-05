"""
Address Mapper Module

This module provides functionality to map and convert addresses of datasets
within a given directory structure. It includes the following functions:

1. `addr_extractor(path: str) -> dict`:
   Extracts the addresses of datasets in the given path. For this particular case,
   it is used to extract the mapping of filenames in the crate/dataset and
   crate/application_sources directories.

2. `address_converter_backend(path: str, addr: str, dataset_hashmap: dict) -> str`:
   Converts the given address to a mapped address inside the RO_Crate
   based on the dataset hashmap.

3. `address_converter(path: str, addr: str, dataset_hashmap: dict,
                            application_sources_hashmap: dict) -> str`:
   Attempts to convert the given address first using the dataset hashmap and then
   using the application sources hashmap. Raises a `FileNotFoundError` if the address
   cannot be mapped in either case.

# Problems:
# IF THE DIRECTORY IS TAKEN IN THE FORM OF DATA/INPUT INSTED OF DATA/INPUT/
# THEN IT WILL NOT BE ABLE TO FIND THE DIRECTORY
# DO NOT INCLUDE DOUBLE SLASHES IN THE PATHS LIKE INPUT//TEXT.TXT IT WILL NOT FIND IT
"""


import os

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
            raise FileNotFoundError(f"Could not find the mapped address for: {addr}")

    # Could not find such directory or file
    if not mapped_addr:
        raise FileNotFoundError(f"Could not find the mapped address for: {addr}")

    return mapped_addr

def address_converter(path: str, addr: str, dataset_hashmap: dict,
                      application_sources_hashmap: dict, new_dataset_flag: bool) -> str:
    """
    Attempts to convert the given address first using the dataset hashmap and
    then using the application sources hashmap. Raises a `FileNotFoundError` if
    the address  cannot be mapped in either case.

    Args:
        path (str): Path to the RO_Crate directory.
        addr (str): Address to be converted.
        dataset_hashmap (dict): Hashmap generated from addr_extractor.
        application_sources_hashmap (dict): Hashmap generated from addr_extractor.

    Raises:
        FileNotFoundError: Cannot find the address inside the RO_Crate.

    Returns:
        str: The mapped address.
    """
    if new_dataset_flag:
        dataset_path = os.path.join(os.getcwd(), "new_dataset")
    else:
        dataset_path = os.path.join(path, "dataset")
    application_sources_path = os.path.join(path, "application_sources")
    try:
        # First, check if the address is in the dataset
        return address_converter_backend(dataset_path, addr, dataset_hashmap)
    except FileNotFoundError as e1:
        try:
            # If the dataset address conversion fails, try the application sources
            return address_converter_backend(application_sources_path, addr,
                                             application_sources_hashmap)
        except FileNotFoundError as e2:
            # If both fail, raise an exception with context from both errors
            raise FileNotFoundError(
                f"Could not find the mapped address for: {addr}\n"
                f"Dataset Error: {e1}\nApplication Sources Error: {e2}"
            ) from e2
