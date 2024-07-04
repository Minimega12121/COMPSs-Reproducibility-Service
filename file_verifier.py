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
from utils import get_by_id

def files_verifier(crate_path: str, instrument: str, objects: list[str]):
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
        temp_size.append(instrument_path)
    if not os.path.getsize(instrument_path) == get_by_id(crate, instrument)["contentSize"]:
        size_verifier = False
        temp_path.append(instrument_path)

    #Verify the objects/inputs
    crate = ROCrate(crate_path)
    if objects is not None:
        for input in objects:
            if not os.path.exists(os.path.join(crate_path, input)):
                verified = False
                temp_path.append(os.path.join(crate_path, input))
                continue
            file_object = get_by_id(crate, input)
            content_size = file_object["contentSize"]
            # Verify the above content size with the actual file size

            # Get the actual file size
            actual_size = os.path.getsize(os.path.join(crate_path, input))

            # Verify the content size with the actual file size
            if actual_size != content_size:
                size_verifier = False
                temp_size.append(os.path.join(crate_path, input))

            # actual_modified_date = dt.datetime.utcfromtimestamp(os.path.getmtime
            # (os.path.join(crate_path, input))).replace(microsecond=0).isoformat()

            # if actual_modified_date != file_object["sdDatePublished"][:-6]:
            #     date_verifier = False
            #     temp_date.append(os.path.join(crate_path, input))

    # if not date_verifier:
    #     print_colored(f"The dateModified of the following files is
    # not the same as recorded in the RO-Crate : {temp_date}", TextColor.RED)

    if not size_verifier:
        if verified:
            raise ValueError(f"Content size mismatch in files: {temp_size}")

        raise ValueError(f"Content size mismatch in files: {temp_size}\nFiles missing: {temp_path}")

    if not verified:
        raise FileNotFoundError(f"Files missing in directory: {temp_path}")
