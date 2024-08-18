import os
from utils import download_file, get_Create_Action, print_colored, TextColor, get_by_id
from rocrate.rocrate import ROCrate
import sys

def remote_dataset(crate: ROCrate,crate_directory: str) -> bool:

    createAction = get_Create_Action(crate)
    remote_datasets= {}
    if "object" in  createAction:
        temp = createAction["object"]
    else:
        return (False, None)

    for input in temp: # get the remote_datasets mapped with their names
        if (input.id).startswith("http"):
            remote_datasets[input["name"]] = input.id

    for key,val in remote_datasets.items(): # download the remote datasets with the specified names
        try:
            print_colored(f"Please wait while remote file {key} is being downloaded from {val} ...", TextColor.YELLOW)
            download_file(val, os.path.join(crate_directory,"remote_dataset"),key)

            if "contentSize" in get_by_id(crate,val):
                if get_by_id(crate,val)["contentSize"] == os.path.getsize(os.path.join(crate_directory,"remote_dataset",key)):
                    print_colored(f"Remote file {key} has been successfully downloaded with size verified.", TextColor.GREEN)
            else:
                print_colored(f"Remote file {key} has been successfully downloaded. Could not verify size as it is not mentioned in the metadata", TextColor.GREEN)

        except ValueError:
            print(f"Remote dataset {key} could not be downloaded.")
            sys.exit(1)

    if len(remote_datasets) == 0:
        return (False, None)
    else:
        return (True, remote_datasets)