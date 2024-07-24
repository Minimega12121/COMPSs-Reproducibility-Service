import os
import shutil
import zipfile
import urllib.parse
# Works/workflow-838-1.crate.zip
from utils import print_colored,print_colored_ns, TextColor, executor, get_yes_or_no

def get_workflow(execution_path: str):
    workflow_path = os.path.join(execution_path, "Workflow")
    if len(os.listdir(workflow_path)) == 1:
        flag = get_yes_or_no(f"There already exists a workflow './Workflow/{os.listdir(workflow_path)[0]}'. Do you want to use it(y) or give another workflow(n)? (yes/no):")
        if not flag:
            if os.path.isdir(os.path.join(workflow_path, os.listdir(workflow_path)[0])):
                shutil.rmtree(os.path.join(workflow_path, os.listdir(workflow_path)[0]))
            else:
                os.unlink(os.path.join(workflow_path, os.listdir(workflow_path)[0]))
        else:
            return
    elif len(os.listdir(workflow_path)) > 1:
        raise ValueError("The directory './Workflow' contains multiple crates. Please ensure it is empty or contains one crate before running this script.")

    workflow_source = input("Do you have the workflow at a path or a WorkflowHub link? Enter 'path' or 'link': ").strip().lower()

    if workflow_source == 'path':
        print_colored("Warning: Please ensure this is the path to a zip file or a directory", TextColor.RED)
        crate_path = input("Please enter the path to the the RO-crate: ").strip()

        # if not os.path.isfile(crate_path):
        #     raise FileNotFoundError(f"The file at path {crate_path} was not found.")

        if zipfile.is_zipfile(crate_path):
            shutil.copy(crate_path, os.path.join(workflow_path, "my_crate.zip"))
        elif os.path.isdir(crate_path): # if a directory then just copy the whole directory into the destination and exit the function
            shutil.copytree(crate_path, os.path.join(workflow_path, "crate"))
            return
        else:
            raise ValueError(f"The file at path {crate_path} is not a valid")

    elif workflow_source == 'link':
        print_colored("Warning: Please try using the wget command to ensure the link works before submitting the link here.",TextColor.RED)
        print_colored("Example) wget -O my_crate.zip https://example.com/my_crate.zip", TextColor.RED)
        crate_link = input("Please enter the WorkflowHub link to the RO-crate: ").strip()

        if not urllib.parse.urlparse(crate_link).scheme in ['http', 'https']:
            raise ValueError("The link provided is not a valid URL.")

        executor(["wget", "-O", os.path.join(workflow_path, "my_crate.zip"), crate_link], execution_path)

    else:
        raise ValueError("Invalid input. Please enter 'path' or 'link'.")

    crate_zip_path = os.path.join(workflow_path, "my_crate.zip")

    try:
        with zipfile.ZipFile(crate_zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(workflow_path,"crate"))
    except zipfile.BadZipFile as e:
        raise ValueError(f"The file {crate_zip_path} is not a valid zip file or it is corrupted.")
    finally:
        os.remove(crate_zip_path)

    print(f"The workflow has been successfully extracted to {workflow_path}")

def get_more_flags(command: list[str]) -> list[str]:
    print_colored("The current command is as follows:", TextColor.YELLOW)
    print_colored_ns(" ".join(command), TextColor.YELLOW)
    more = get_yes_or_no("Do you want to add more flags to the compss runtime command shown above")

    if not more: # return if no more flags are needed
        return command


    print_colored("WARNING: Submit the flags in one go. Example) Please enter the flags you want to add: --lang=python -d -p",TextColor.RED)
    flag = input("Please enter the flags you want to add: ")
    flags: list[str] = flag.split(" ")
    for f in flags:
        command.insert(1, f)

    return command

def get_change_values(command : list[str]) -> list[str]:
    print_colored("The current command is as follows:", TextColor.YELLOW)
    print_colored_ns(" ".join(command), TextColor.YELLOW)
    if not get_yes_or_no("Do you want to change anything from the above command?"):
        return command
    else:
        n = len(command)
        print_colored("The current command indexed is as follows:", TextColor.YELLOW)
        for i in range(n):
            print_colored_ns(f"{i+1}. {command[i]}", TextColor.YELLOW)
        satisfied = True
        while satisfied:
            try:
                m = int(input("How many values do you want to change? Enter the number: "))
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
                return command

            for i in range(m):
                try:
                    index = int(input(f"Enter the index of the value you want to change (1-{len(command)}): "))
                    if index < 1 or index > len(command):
                        raise ValueError
                except ValueError:
                    print("Invalid input. Please enter a valid integer between 1 and the number of values.")
                    return command

                command[index-1] = input(f"Enter the new value for index {index}: ").strip()

            for i in range(n):
                print_colored_ns(f"{i+1}. {command[i]}", TextColor.YELLOW)
            print_colored("Are you happy with the changes above?", TextColor.YELLOW)
            satisfied = not get_yes_or_no("")


    return command
    ...
