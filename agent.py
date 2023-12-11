# (C) David Joffe / DJ Software
# Import necessary libraries
import sys
#import argparse

import autogen

import os
import json
import requests

# Configuration
worktree = "tlex"
files_to_send = ["DicLib/djNode.h", "DicLib/djNode.cpp"]
targetfolder = "modified_tlex"


#"model": ["gpt-4", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
		"model": ["gpt-4", "gpt-3.5-turbo", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    },
)


# Define the command line arguments
#parser = argparse.ArgumentParser(description='Send files for code modification tasks.')
#parser.add_argument('task_description', type=str, help='Description of the task to be performed')
#parser.add_argument('header_file', type=str, help='Header file to be modified')
#parser.add_argument('source_file', type=str, help='Source file to be modified')

# Read task from tasks.txt
#with open('tasks.txt', 'r') as file:
with open('task.txt', 'r') as file:
    task = file.read().strip()
    print(f"===== agent TASK:{task}")

# Simulate command line argument input (this would normally come from sys.argv)
# Here we provide an example of arguments
#sys.argv = ['script.py', 'Refactor wxStrings to std::wstring', 'example.h', 'example.cpp']
# Types of tasks:
# * Refactor wxString-based code to std::wstring
# * Refactor std::wstring to std::string utf8 in some cases
# * Refactor djLog's into tlLOG that are not printf-formattig-based code (instead use safer better alternatives like e.g. std to_string, plain string concatenation)
# * Refactor wxString::Format into equivalent
# * Split large .cpp files into smaller sections
# * Harden some parts of code to be more thread-safe
# * Python-related work? ML work?
# * Build testing
# * Add more unit tests

#args = parser.parse_args()

# Function to simulate sending files and receiving modified files
# In a real scenario, this function would interact with an external service like Taskweaver
# Since I cannot perform actual HTTP requests, this is a placeholder for the function

# Function to send files to AutoGen and receive modified files
def send_to_autogen(file_path, task):
    (f"===== send:{file_path}")

    # Assuming AutoGen has an API endpoint for file processing
    autogen_url = "https://api.autogen.com/process_file"
    headers = {'Content-Type': 'application/json'}

    # Read file content
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Prepare data for AutoGen API
    data = {
        "file_name": os.path.basename(file_path),
        "file_content": file_content,
        "task": task
    }

    # Send request to AutoGen
    response = requests.post(autogen_url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["modified_file_content"]
    else:
        raise Exception("Error processing file with AutoGen")


# Function to process files
def process_files(files_to_send, worktree, targetfolder, task):
    for file_name in files_to_send:
        file_path = os.path.join(worktree, file_name)
        if os.path.exists(file_path):
            print(f"Processing {file_name}...")
            try:
                modified_content = send_to_autogen(file_path, task)

                # Save modified file
                target_path = os.path.join(targetfolder, file_name)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, 'w') as file:
                    file.write(modified_content)
                print(f"Saved modified {file_name} to {targetfolder}")
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")
        else:
            print(f"File not found: {file_name}")

# Main script execution
if __name__ == '__main__':
    for file_name in files_to_send:
        print(f"SETTINGS:File={file_name}...")
    print(f"SETTINGS: Task={task}")

    # create an AssistantAgent named "assistant"
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config={
            "cache_seed": 42,  # seed for caching and reproducibility
            "config_list": config_list,  # a list of OpenAI API configurations
            "temperature": 0,  # temperature for sampling
        },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
    )
    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={
            "work_dir": "coding",
            "use_docker": False,  # set to True or image name like "python:3" to use docker
        },
    )
    # the assistant receives a message from the user_proxy, which contains the task description
    user_proxy.initiate_chat(
        assistant,
        message=f"Please do the following task: {task}",
    )

    # Call the function to process files
    process_files(files_to_send, worktree, targetfolder, task)
    #result = send_files_for_modification(args.task_description, args.header_file, args.source_file)
    #print(f'Modified files received: {result}')
    print("All files processed.")
