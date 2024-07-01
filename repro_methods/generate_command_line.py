# Problems: Anything with / ot \ is considered a path, but it could be a flag or a value
# Plus if the command is " runcompss main.py " it will not convert the path for main.py so it must be declared as " runcompss /main.py " 

import os
import shlex
import os
import re

from .address_mapper import address_converter,addr_extractor


def generate_command_line(self) -> list[str]:
    print('Parsing metadata...', self.crate_directory)
    path = self.crate_directory
    dataset_hashmap = addr_extractor(os.path.join(path,"dataset"))
    application_sources_hashmap = addr_extractor(os.path.join(path,"application_sources"))
    
  
    compss_submission_command_path =  os.path.join(path, "compss_submission_command_line.txt")
    
    for line in open(compss_submission_command_path):
        compss_submission_command = line
        break
    
    command = command_line_generator(compss_submission_command, path, dataset_hashmap, application_sources_hashmap)
    
    return command
        
def command_line_generator(command: str, path: str, dataset_hashmap: dict, application_sources_hashmap: dict) -> list[str]:
    command = shlex.split(command) 
    path_pattern = re.compile(r'[/\\]')  # Pattern for detecting paths
    
    flags = []
    paths = []
    values = []
    
    for i in range(len(command)):
        if command[i].startswith("--") or command[i].startswith("-"):
            # No considering the provenance flag for reproducing
            if not (command[i].startswith("--provenance") or command[i].startswith("-p")):
                 flags.append((command[i],i))
        elif path_pattern.search(command[i]):
            paths.append((command[i],i))
        else:
            values.append((command[i],i))
            
    new_paths = []
    
    for filepath in paths:
        new_filepath = address_converter(path, filepath[0], dataset_hashmap, application_sources_hashmap)
        new_paths.append((new_filepath,filepath[1]))
        
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
    
    if(new_command[0] == "enqueue_compss"):
        new_command[0] = "runcompss"
    
    return new_command

        
    


    
   
    
 
    
    
    
    
    
