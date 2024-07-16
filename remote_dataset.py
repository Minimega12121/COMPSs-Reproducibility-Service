import os
from utils import download_file, get_Create_Action
from rocrate.rocrate import ROCrate
import sys

def remote_dataset(crate: ROCrate,crate_directory: str) -> bool:

    createAction = get_Create_Action(crate)
    remote_datasets= {}
    print(createAction)
    if "object" in  createAction:
        temp = createAction["object"]
    else:
        return (False, None)

    print(temp)
    for input in temp: # get the remote_datasets mapped with their names
        if (input.id).startswith("http"):
            remote_datasets[input["name"]] = input.id

    for key,val in remote_datasets.items(): # download the remote datasets with the specified names
        try:
            download_file(val, os.path.join(crate_directory,"remote_dataset"),key)
        except ValueError:
            print(f"Remote dataset {key} could not be downloaded.")
            sys.exit(1)

    if len(remote_datasets) == 0:
        return (False, None)
    else:
        return (True, remote_datasets)