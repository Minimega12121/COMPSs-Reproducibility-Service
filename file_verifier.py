"""
RS File Verification Module

This module verifies files referenced in an RO-Crate against their metadata,
ensuring their existence and optionally their size and modification date.

Functions:
    - files_verifier(crate_path: str, instrument: str, objects: list[str])
      Verify files within an RO-Crate against their metadata.
"""

import os

from rocrate.rocrate import ROCrate
from utils import get_by_id, print_colored, TextColor, key_exists_with_first_element
import datetime as dt

def files_verifier(crate_path: str, instrument: str, objects: dict, remote_dataset_dict: dict):
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
    print_colored("Verifying the files in the crate",TextColor.GREEN)
    verified = True
    size_verifier = True
    # date_verifier = True
    temp_size = []
    temp_path = []
    # temp_date = []
    crate = ROCrate(crate_path)
    instrument_path = os.path.join(crate_path, instrument)

    # Verify the instrument file
    if not os.path.exists(instrument_path):
        verified = False
        temp_path.append(instrument_path)
    if not os.path.getsize(instrument_path) == get_by_id(crate, instrument)["contentSize"]:
        size_verifier = False
        temp_size.append(instrument_path)

    #Verify the objects/inputs
    crate = ROCrate(crate_path)

    if objects == None:
        print_colored("No objects found in the crate, so nothing to verify", TextColor.GREEN)
        return

    for name,input in objects.items():
        if remote_dataset_dict != None and key_exists_with_first_element(remote_dataset_dict,name[0]): # Do not verifiy the local objects if remote dataset exists
            continue
        # Skip the remote objects
        if input.startswith("http"):
            continue
        file_path = os.path.join(crate_path, input)
        if not os.path.exists(file_path):
            verified = False
            temp_path.append(file_path)
            continue
        else:
            print(file_path+"\n"+"FILE EXISTS")
        file_object = get_by_id(crate, input)
        if "contentSize" in file_object:
            content_size = file_object["contentSize"]
            # Verify the above content size with the actual file size
            # Get the actual file size
            actual_size = os.path.getsize(file_path)

            # Verify the content size with the actual file size
            if actual_size != content_size:
                size_verifier = False
                temp_size.append(os.path.join(crate_path, input))
            else:
                print(os.path.join(crate_path, input)+"\n"+"SIZE VERIFIED")

        # actual_modified_date = dt.datetime.utcfromtimestamp(os.path.getmtime(file_path)).replace(microsecond=0).isoformat()
        # if "dateModified" in file_object and actual_modified_date != file_object["dateModified"][:-6]:
        #     print(f"DateModified of {file_path} is incorrect\n")
        #     date_verifier = False
        #     temp_date.append(file_path)
        #     print("Actual modified date",actual_modified_date)
        #     print("Date modifed in crate",file_object["dateModified"][:-6])
        #     print("sdDatePublished in crate",file_object["sdDatePublished"][:-6])
        # else:
        #     print(f"DateModified of {file_path} is correct")



    if not size_verifier:
        if verified:
            raise ValueError(f"Content size mismatch in files: {temp_size}")
        else:
            raise ValueError(f"Content size mismatch in files: {temp_size}\nFiles missing: {temp_path}")
    if not verified:
        raise FileNotFoundError(f"Files missing in directory: {temp_path}")

    print_colored("All files in the crate have been verified successfully", TextColor.GREEN)


