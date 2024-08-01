"""
Command Line Generator Module

This module provides functions to generate and modify command line arguments,
particularly handling paths for datasets and application sources.

Problems:
Anything with r'/' ot r'\' is considered a path, but it could be a flag or a value
Plus if the command is " runcompss main.py " it will not convert the path for main.py
so it must be declared as " runcompss /main.py "
"""

import os
import shlex
import re
from .address_mapper import address_converter, addr_extractor

def generate_command_line(self) -> list[str]:
    """
    Generates a modified command line based on the contents of a compss_submission_command_line.txt
    file and the mappings of dataset and application sources in the crate directory.

    Args:
    crate_directory (str): Path to the crate directory containing dataset and application sources.

    Returns:
    list[str]: Modified command line arguments.
    """
    print('\nParsing metadata...', self.crate_directory)
    path = self.crate_directory

    dataset_flags = (self.remote_dataset_flag, self.new_dataset_flag)

    remote_dataset_hashmap = {}
    if self.remote_dataset_flag:
        print(os.path.join(path, "remote_dataset"))
        remote_dataset_hashmap = addr_extractor(os.path.join(path, "remote_dataset"))
    print(remote_dataset_hashmap)
    if not self.new_dataset_flag:
        dataset_hashmap = addr_extractor(os.path.join(path, "dataset"))
    else:
        dataset_hashmap = addr_extractor(os.path.join(path, "new_dataset"))

    application_sources_hashmap = addr_extractor(os.path.join(path, "application_sources"))

    compss_submission_command_path = os.path.join(path, "compss_submission_command_line.txt")

    with open(compss_submission_command_path, 'r', encoding='utf-8') as file:
        compss_submission_command = next(file).strip()

    new_command = command_line_generator(compss_submission_command, path,
                                     dataset_hashmap, application_sources_hashmap,remote_dataset_hashmap,dataset_flags)

    return new_command

def command_line_generator(command: str, path: str, dataset_hashmap: dict,
                           application_sources_hashmap: dict, remote_dataset_hashmap: dict, dataset_flags: tuple[bool,bool]) -> list[str]:
    """
    Generates a modified command line by replacing paths in the command with their
    mapped counterparts based on the dataset and application sources mappings.
    Acts as the main logic behind generate_command_line.

    Args:
        command (str): Original command line string.
        path (str): Path to the RO_Crate directory.
        dataset_hashmap (dict): Hashmap generated from addr_extractor.
        application_sources_hashmap (dict): Hashmap generated from addr_extractor.

    Returns:
        list[str]: Modified command line arguments with mapped paths.
    """
    command = shlex.split(command)
    flags = []
    paths = []
    values = []

    for i, cmd in enumerate(command):
        if cmd.startswith("--") or cmd.startswith("-"):
            if not (cmd.startswith("--provenance") or cmd.startswith("-p")):
                flags.append((cmd, i))
        elif re.compile(r'[/\\]').search(cmd): # Pattern for detecting paths
            paths.append((cmd, i))
        else:
            values.append((cmd, i))

    new_paths = []

    for filepath in paths:
        new_filepath = address_converter(path, filepath[0],dataset_hashmap,
                                application_sources_hashmap, remote_dataset_hashmap, dataset_flags)

        new_paths.append((new_filepath, filepath[1]))

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

    if new_command and new_command[0] == "enqueue_compss": # Special case for enqueue_compss
        new_command[0] = "runcompss"

    return new_command
