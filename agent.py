# (C) David Joffe / DJ Software
# Import necessary libraries
import sys
import autogen
import os
import json
import requests
import io
import datetime

# custom dual output to capture output and echo it to console so we can both log it and extract code from it but also see it in real-time
from dual_output import DualOutput
from helper_functions import create_files_from_ai_output

# Configuration
worktree = "tlex/DicLib"
files_to_send = ["djNode.h", "djNode.cpp"]
files_to_send = None
files_to_create = ["djVec3d.h", "djVec3d.cpp"]
files_to_create = ["djQuaternion.h", "djQuaternion.cpp"]
files_to_create = ["refactored_lines.cpp"]
targetfolder = "modified_tlex/DicLib"
# settings
# I need to experiment a bit more to see exactly the implications of not creating groups (or creating groups), both if I only have 1 AI agent available or if I have 2 or 3 machines I can use ..
NoGroup=True
#MaxAgents=1
# dj try make setting to control if we have lots or fewer etc. of AIs to use:
# this needs further work though
coder_only=True

# [dj2023-12] local LiteLLM instances ...
config_list_localgeneral=[
    {
        'base_url':"http://10.0.0.13:8000",
        'api_key':"NULL"
    }
]
config_list_localcoder=[
    {
        'base_url':"http://127.0.0.1:8000",
        'api_key':"NULL"
    }
]
config_list_localcoder=[
    {
        'base_url':"http://10.0.0.10:8000",
        'api_key':"NULL"
    }
]
config_list_local3=[
    {
        'base_url':"http://air.local:8000",
        'api_key':"NULL"
    }
]
llm_config_localgeneral={
    "config_list":config_list_localgeneral
}
llm_config_localcoder={
    "config_list":config_list_localcoder
}
llm_config_local3={
    "config_list":config_list_local3
}




#"model": ["gpt-4", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
		"model": ["gpt-4", "gpt-3.5-turbo", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    },
)
# try use gpt-3.5-turbo instead of gpt-4 as seems costly to use gpt-4 on OpenAI
config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-3.5-turbo"],
    },
)

# Get date/time to use in filenames and directories and session logfiles etc.
task_datetime = datetime.datetime.now()
task_formatted_datetime = task_datetime.strftime("%Y-%m-%d %H-%M-%S")
task_output_directory='output_files' + '/' + task_formatted_datetime


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
# * Refactor tStrAppend into non-printf-formatted code
# * Refactor wxString::Format into equivalent
# * Create new .h/.cpp files and new classes
# * Split large .cpp files into smaller sections
# * Harden some parts of code to be more thread-safe
# * Python-related work? ML work?
# * Build testing
# * Add more unit tests

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
    if files_to_send:
        for file_name in files_to_send:
            print(f"SETTINGS:File={file_name}...")
    print(f"SETTINGS: Task={task}")

    # create an AssistantAgent named "assistant"
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config={
            "cache_seed": 1055,  # seed for caching and reproducibility
            #"config_list": config_list,  # a list of OpenAI API configurations
            # above line for OPENAI and this below line for our LOCAL LITE LLM:
            "config_list": config_list_localgeneral,  # a list of OpenAI API configurations
            "temperature": 0,  # temperature for sampling
        },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
    )
    # Create a coder agent
    coder = autogen.AssistantAgent(
        name="coder",
        llm_config=llm_config_localcoder
    )
    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        llm_config=llm_config_localgeneral,
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={
            "work_dir": "coding",
            "use_docker": False,  # set to True or image name like "python:3" to use docker
        },
    )

    """
    if coder_only:
        # the assistant receives a message from the user_proxy, which contains the task description
        #user_proxy.initiate_chat(
        coder.initiate_chat(
            coder,
            message=f"Please do the following task: {task}",
        )
    else:
        # the assistant receives a message from the user_proxy, which contains the task description
        user_proxy.initiate_chat(
            assistant,
            message=f"Please do the following task: {task}",
        )
    """

    if not NoGroup:
        groupchat = autogen.GroupChat(agents=[user_proxy, coder, assistant], messages=[])
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config_localgeneral)
    else:
        groupchat = None
        manager = None

    # [IO redirect begin] Backup the original stdout
    ####original_stdout = sys.stdout
    # [IO redirect begin] Create a StringIO object to capture output
    ####captured_output = io.StringIO()
    ####sys.stdout = captured_output

    # Redirect output to both console and StringIO
    dual_output = DualOutput()
    sys.stdout = dual_output

    # Call the function to process files
    if files_to_create:
        task_message = f"Please create the following files: {', '.join(files_to_create)} with the following specifications: {task}"
        #user_proxy.initiate_chat(assistant, message=create_task_message)
        if coder_only:
            # the assistant receives a message from the user_proxy, which contains the task description
            #coder.initiate_chat(
            user_proxy.initiate_chat(
                coder if manager is None else manager,
                message=task_message,
            )
        else:
            # the assistant receives a message from the user_proxy, which contains the task description
            user_proxy.initiate_chat(
                assistant,
                message=task_message,
            )
    elif files_to_send:
        # If no files to create, do requested task
        print(f"=== Processing files: {', '.join(files_to_send)}")
        process_files(files_to_send, worktree, targetfolder, task)
    else:
        # If no files to create, do requested task
        print(f"=== Processing task: {task}")
        task_message=task
        if coder_only:
            # the assistant receives a message from the user_proxy, which contains the task description
            #coder.initiate_chat(
            user_proxy.initiate_chat(
                coder if manager is None else manager,message=task,
            )
        else:
            # the assistant receives a message from the user_proxy, which contains the task description
            user_proxy.initiate_chat(
                assistant,message=task,
            )


    # [IO redirect] Reset stdout to original
    ####sys.stdout = original_stdout
    # [IO redirect] Get the content from the captured output
    ####ai_output = captured_output.getvalue()

    # Reset stdout to original and get captured output
    sys.stdout = dual_output.console
    #captured_output = dual_output.getvalue()
    ai_output = dual_output.getvalue()


    # Create the log filename
    log_filename_base = f"dj_AI_log.txt"
    # Write the AI output to the log file
    with open(log_filename_base, 'a') as log_file:
        log_file.write("Captured AI Output:\n")
        log_file.write(ai_output)

    # Create the output directory if it doesn't exist
    if not os.path.exists(task_output_directory):
        os.makedirs(task_output_directory)

    # Create the log filename
    log_filename1 = f"{task_output_directory}/dj_AI_log.txt"
    # Write the AI output to the log file
    with open(log_filename1, 'w') as log_file:
        log_file.write("Captured AI Output:\n")
        log_file.write(ai_output)

    # Use ai_output with create_files_from_ai_output function in order to actually create any files in the returned code
    create_files_from_ai_output(ai_output, task_output_directory)

    # Print the captured output to the console
    print("=== Captured AI Output:")
    print(ai_output)


    # Get the current date and time
    current_datetime = task_datetime
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H-%M-%S")

    # Create the log filename
    log_filename = f"dj AI log - {formatted_datetime}.txt"
    # Write the AI output to the log file
    with open(log_filename, 'w') as log_file:
        log_file.write("Captured AI Output:\n")
        log_file.write(ai_output)
    print(f"=== Log saved in file: {log_filename}")

    #result = send_files_for_modification(args.task_description, args.header_file, args.source_file)
    #print(f'Modified files received: {result}')
    print("=== Done! All tasks processed.")
