import os
from rocrate.rocrate import ROCrate

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
def files_verifier(crate_path:str,instrument:str, objects:list[str]):
    verified = True
    size_verifier = True
    temp = None
    crate = ROCrate(crate_path)
    # Verify the instrument file
    if not os.path.exists(os.path.join(crate_path, instrument)):
        verified = False
        temp = os.path.join(crate_path, instrument)
    if not os.path.getsize(os.path.join(crate_path, instrument)) == get_by_id(crate, instrument)["contentSize"]:
        size_verifier = False
        temp = os.path.join(crate_path, instrument)
        
    #Verify the objects/inputs
    crate = ROCrate(crate_path)   
    if objects is not None:
        for input in objects:
            if not os.path.exists(os.path.join(crate_path, input)):
                verified = False
                temp = os.path.join(crate_path, input)
                break
            file_object = get_by_id(crate, input)      
            content_size = file_object["contentSize"]
            # Verify the above content size with the actual file size
            
               # Get the actual file size
            actual_size = os.path.getsize(os.path.join(crate_path, input))
            
            # Verify the content size with the actual file size
            if actual_size != content_size:
                size_verifier = False
                temp = os.path.join(crate_path, input)
                break
    
    if not size_verifier:
        raise Exception(f"The content size of a file is not the same as recorded in the RO-Crate : {temp}")
    
    if not verified:
        raise Exception(f"A file specified in the RO-Crate are not present in the directory : {temp}")