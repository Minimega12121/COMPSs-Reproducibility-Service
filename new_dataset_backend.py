import os
import time

from utils import print_colored, TextColor, get_yes_or_no

def print_directory_contents(path, level=0):
    try:
        # List all the entries in the directory
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            # Print the entry (file or directory) with indentation
            print(' ' * level * 4 + entry)
            # If the entry is a directory, recursively call the function for the sub-directory
            if os.path.isdir(entry_path):
                print_directory_contents(entry_path, level + 1)
    except PermissionError:
        # Handle the case where the program does not have permission to access the directory
        print(' ' * level * 4 + '[Permission Denied]')


def new_dataset_info_collector(crate_directory:str):
    new_dataset_path = os.path.join(crate_directory, "new_dataset")
    os.makedirs(new_dataset_path)
    print(f"\nPlease copy the new dataset to the 'new_dataset' folder :\n")
    print_colored("New dataset path: " + new_dataset_path, TextColor.BLUE)
    print_colored("WARNING| MAKE SURE THE NEW DATASET FOLLOWS THE SAME DIRECTORY STRUCTURE AS THE OLD DATASET", TextColor.RED)
    print("The old directory structure for reference is as follows:\n")
    print_directory_contents(os.path.join(crate_directory, "dataset"))
    check = False
    while not check:
        check = get_yes_or_no("Have you copied the new dataset to the 'new_dataset' folder?")