import subprocess

def executor(command: list[str]):
    # Start the subprocess
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Read the output and error streams
    stdout, stderr = process.communicate()
    
    if process.returncode == 0:
        print("Standard Output:")
        print(stdout)
        print("Command executed successfully.")
    else:
        print("Standard Error:")
        print(stderr)
        print("Command failed with return code:", process.returncode)
        
        




