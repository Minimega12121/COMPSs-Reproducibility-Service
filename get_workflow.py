import os
import shutil
import zipfile
import urllib.parse
# Works/workflow-838-1.crate.zip
from utils import print_colored, TextColor, executor, get_yes_or_no

def get_workflow():
    workflow_path = "./Workflow"
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
        print_colored("Warning: Please ensure this is the path to the zip file not the extracted crate", TextColor.RED)
        crate_path = input("Please enter the path to the zip file containing the RO-crate: ").strip()

        if not os.path.isfile(crate_path):
            raise FileNotFoundError(f"The file at path {crate_path} was not found.")

        if not zipfile.is_zipfile(crate_path):
            raise ValueError(f"The file at path {crate_path} is not a valid zip file.")

        shutil.copy(crate_path, os.path.join(workflow_path, "my_crate.zip"))

    elif workflow_source == 'link':
        print_colored("Warning: Please try using the wget command to ensure the link works before submitting the link here.",TextColor.RED)
        print_colored("Example) wget -O my_crate.zip https://example.com/my_crate.zip", TextColor.RED)
        crate_link = input("Please enter the WorkflowHub link to the RO-crate: ").strip()

        if not urllib.parse.urlparse(crate_link).scheme in ['http', 'https']:
            raise ValueError("The link provided is not a valid URL.")

        executor(["wget", "-O", os.path.join(workflow_path, "my_crate.zip"), crate_link])

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

    print("The workflow has been successfully extracted to './Workflow/'.")
