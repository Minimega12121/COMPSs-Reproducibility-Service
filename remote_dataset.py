from utils import download_file, get_Create_Action
from rocrate.rocrate import ROCrate

def remote_dataset(crate: ROCrate) -> bool:

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
        download_file(val, "./remote_dataset",key)

    if len(remote_datasets) == 0:
        return (False, None)
    else:
        return (True, remote_datasets)