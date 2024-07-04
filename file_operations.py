"""
RS File Operations Module

This module provides functions for handling file operations such as removing temporary files,
moving newly created files to a 'Result' folder, and copying files from specific directories
to the current working directory.

Functions:
- move_results_created(initial_files, temp): Removes temporary files and moves newly created files
  to a 'Result' folder in the current working directory.
- dataset_mover_and_application_mover(crate_directory): Copies all files from 'application_sources'
  and 'dataset' folders within the crate directory to the current working directory.
- copy_all_to_cwd(src_path): Recursively copies all files and directories from the specified source
  path to the current working directory.

Notes:
- For 'move_results_created', temporary files are deleted from the current working directory.
  Newly created files are moved to './Result'.
- 'dataset_mover_and_application_mover' copies files from 'application_sources' and 'dataset'
   folders located within 'crate_directory' to the current working directory.
- 'copy_all_to_cwd' copies all files and directories from 'src_path' to the cwd.

Usage:
  The main usecase of this module is to move the final results to a 'Result' folder.
"""

import os
import shutil

def move_results_created(initial_files, temp):
    """
    Removes temporary files and moves newly created files to a 'Result' folder.

    Args:
    initial_files (set): Set of initial files before operation.
    temp (list): List of temporary files to be removed.

    """
    result_folder = "./Result"
    # Get the current list of files in the CWD
    cwd = os.getcwd()
    for filename in temp:
        file_path = os.path.join(cwd, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    current_files = set(os.listdir(cwd))
    # Determine the new files by comparing current files with initial files
    new_files = current_files - initial_files

    if new_files:
        # Create the Result folder if it doesn't exist
        result_folder_path = os.path.join(cwd, result_folder)
        if not os.path.exists(result_folder_path):
            os.makedirs(result_folder_path)
        else:
            # Clear the existing files in the Result folder
            for filename in os.listdir(result_folder_path):
                file_path = os.path.join(result_folder_path, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

        # Move the new files to the Result folder
        for new_file in new_files:
            src_path = os.path.join(cwd, new_file)
            dest_path = os.path.join(result_folder_path, new_file)
            shutil.move(src_path, dest_path)

def dataset_mover_and_application_mover(crate_directory) -> set[str]:
    """
    Copies all files from 'application_sources' and 'dataset' folders in the
    crate directory to the current working directory. Can tackle some cases of h
    ard-coded paths in the application.

    Args:
    crate_directory (str): Path to the RO-Crate directory.

    Returns:
    set: A set of names of the files and directories copied to the current working directory.
    """
    application_folder = os.path.join(crate_directory, "application_sources")
    dataset_folder = os.path.join(crate_directory, "dataset")
    input_files_copied = set()
    input1 = copy_all_to_cwd(application_folder)
    input2 = copy_all_to_cwd(dataset_folder)
    input_files_copied = input1.union(input2)

    return input_files_copied

def copy_all_to_cwd(src_path) -> set[str]:
    """
    Copies all files and folders from the specified source path to the current working directory.

    Parameters:
    src_path (str): The path to the source directory containing files and folders to be copied.

    Returns:
    Set[str]: A set of names of the files and directories copied to the current working directory.
    """
    if not os.path.isdir(src_path):
        print(f"The provided path '{src_path}' is not a valid directory.")
        return set()

    cwd = os.getcwd()
    copied_items = set()

    def copy_item(src_item_path, dst_item_path):
        if os.path.isdir(src_item_path):
            if not os.path.exists(dst_item_path):
                os.makedirs(dst_item_path)
            items = os.listdir(src_item_path)
            for item in items:
                copy_item(os.path.join(src_item_path, item), os.path.join(dst_item_path, item))
        else:
            shutil.copy2(src_item_path, dst_item_path)
        copied_items.add(os.path.relpath(dst_item_path, cwd))

    for item in os.listdir(src_path):
        src_item_path = os.path.join(src_path, item)
        dst_item_path = os.path.join(cwd, item)
        copy_item(src_item_path, dst_item_path)

    print(f"{len(copied_items)} items copied to the current working directory.")
    return copied_items
