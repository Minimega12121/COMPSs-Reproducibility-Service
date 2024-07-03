import os
from rocrate.rocrate import ROCrate
import datetime as dt

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

# Date_modified verifier also works but commented out as during testing it is not needed
def files_verifier(crate_path:str,instrument:str, objects:list[str]):
    verified = True
    size_verifier = True
    date_verifier = True
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
                
            # actual_modified_date = dt.datetime.utcfromtimestamp(os.path.getmtime(os.path.join(crate_path, input))).replace(microsecond=0).isoformat()
            
            # if actual_modified_date != file_object["sdDatePublished"][:-6]:
            #     date_verifier = False
            #     temp_date.append(os.path.join(crate_path, input))
                
    # if not date_verifier:
    #     print_colored(f"The dateModified of the following files is not the same as recorded in the RO-Crate : {temp_date}", TextColor.RED)
    
    if not size_verifier:
        if verified:
            raise Exception(f"The content size of the following files is not the same as recorded in the RO-Crate : {temp_size}")
        else:
            raise Exception(f"The content size of the following files is not the same as recorded in the RO-Crate : {temp_size}\n\nThe following files in the RO-Crate are not present in the directory : {temp_path}")
    
    if not verified:
        raise Exception(f"The following files in the RO-Crate are not present in the directory : {temp_path}")
    
