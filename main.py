# Copyright (C) 2023 David Joffe / DJ Software
# Import necessary libraries
import sys
import autogen
import os
import json
import requests
import io
import datetime
import refactor
from globals import g_ai_output_saved_last_code_block

# custom dual output to capture output and echo it to console so we can both log it and extract code from it but also see it in real-time
from dual_output import DualOutput
from helper_functions import create_files_from_ai_output

##### system/script init:
# Get the directory of the current script (runai.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"=== Script directory: {script_dir}")

##### settings defaults
# dj2023-12 This anyway only works for Python currently and the user agent goes back and forth with coder and coder thinks there's a problem and sends the code again and again because user agent couldn't execute
# Even if it could exec C++ I don't currently want it to for these tasks so let's make this a parameter
# Maybe in future for some tasks it should be true eg simpler Python stuff it can exec or if it gets better in future
code_execution_enabled=False
# TODO also try let coder handle things more directly?
#max_consecutive_auto_replies=10
max_consecutive_auto_replies=0

task_folder = "tasks/copyright"
use_cache_seed=24
use_openai=False
#use_openai=True

# Configuration
worktree = "src/tlex"
# can also override in your settings.py passed in as parameter:
refactor_wildcards = ["*.cpp", "*.h"]
refactor_wildcard = "*.cpp"
#refactor_wildcard = "*.h"
refactor_codetype = "cpp"
#refactor_matches = "^[ \t]*tStrAppend"
refactor_matches = "tStrAppend("
# Don't change the actual function itself
#refactor_negmatches =["void tStrAppend("]
# can also override in your settings.py passed in as parameter:
refactor_negmatches =[]
#refactor_matches = " tStrAppend"
#refactor_matches = " Copyright (C)"
do_refactor=False
taskfile='task.txt'
inputfile='input.txt'

# Parameter 1: taskfile with task prompt (defaults to task.txt)
if len(sys.argv) > 1:
    print(f"=== Using taskfile: {sys.argv[1]}")
    taskfile = sys.argv[1]
else:
    taskfile = 'task.txt'  # Or set a default value as needed

# Parameter 2: target folder to operate on, for example your codebase e.g. "src/tlex" defaults to 'src'
# Work in current folder by default if not specified?
worktree='.'
if len(sys.argv) > 2:
    print(f"=== Using target folder: {sys.argv[2]}")
    worktree = sys.argv[2]

# Parameter 3: task settings.py to run
if len(sys.argv) > 3:
    print(f"=== Using task settings.py: {sys.argv[3]}")
    settings_pyscript = sys.argv[3]
    if os.path.exists(settings_pyscript):
        # Read the settings.py file
        with open(settings_pyscript, 'r', encoding='utf-8') as file:
            settings_py = file.read()
        # Execute the settings.py file
        exec(settings_py)


# Slightly gross but use this global to capture output from AI of last most recent final code block it sent
#g_ai_output_saved_last_code_block=None

files_to_send = ["djNode.h", "djNode.cpp"]
files_to_send = None
files_to_create = ["djVec3d.h", "djVec3d.cpp"]
files_to_create = ["djQuaternion.h", "djQuaternion.cpp"]
files_to_create = ["refactored_lines.cpp"]
files_to_create=None
targetfolder = "modified_tlex/DicLib"
# settings
# I need to experiment a bit more to see exactly the implications of not creating groups (or creating groups), both if I only have 1 AI agent available or if I have 2 or 3 machines I can use ..
NoGroup=True
#NoGroup=False
#MaxAgents=1
# dj try make setting to control if we have lots or fewer etc. of AIs to use:
# this needs further work though
coder_only=True
no_user_proxy=True
no_user_proxy=False


##### Local AI instance configuration (should make this easier in future to chop and change for specific tasks/setups etc.)
# Either via command-line or extra setuup.py or both etc. or maybe even environment variables
# e.g. maybe in future could look in local folder for settings.py and if found exec it after these defaults

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


##### OpenAI Configurations (if using OpenAI API, it's optional)
# Construct the path to the OAI_CONFIG_LIST file
config_list_path = os.path.join(script_dir, "OAI_CONFIG_LIST")
# Check if the OAI_CONFIG_LIST file exists
if os.path.exists(config_list_path):
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
    have_openai_config = True
else:
    print("Warning: No OpenAI configuration - this is not critical if using local AI instances like LiteLLM")
    have_openai_config = False
    use_openai = False



llm_config_coder_openai={
    "config_list":config_list
}
# Get date/time to use in filenames and directories and session logfiles etc.
task_datetime = datetime.datetime.now()
task_formatted_datetime = task_datetime.strftime("%Y-%m-%d %H-%M-%S")
task_output_directory='output_files' + '/' + task_formatted_datetime
# Create the output directory if it doesn't exist
if not os.path.exists(task_output_directory):
    os.makedirs(task_output_directory)


# Read task from tasks.txt
#with open('tasks.txt', 'r') as file:
###with open('task.txt', 'r') as file:
###    task = file.read().strip()
###    print(f"===== agent TASK:{task}")
# Read all task lines from tasks.txt
task = ""
with open(taskfile, 'r', encoding='utf-8') as file:
    for line in file:
        task += line.strip() + "\n"  # Appending each line to the task string

if task=="":
    # Define your coding task, for example:
    print("=== No task specified, using default task")
    task = "Write a Python function to sort a list of numbers."


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
    with open(file_path, 'r', encoding='utf-8') as file:
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
                with open(target_path, 'w', encoding='utf-8') as file:
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
    print(f"USE_OPENAI={use_openai}")

    # create an AssistantAgent named "assistant"
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config={
            "cache_seed": use_cache_seed,  # seed for caching and reproducibility
            #"config_list": config_list,  # a list of OpenAI API configurations
            # above line for OPENAI and this below line for our LOCAL LITE LLM:
            "config_list": config_list_localgeneral,  # a list of OpenAI API configurations
            "temperature": 0,  # temperature for sampling
        },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
    )
    # Create a coder agent
    coder = autogen.AssistantAgent(
        name="coder",
        llm_config=llm_config_coder_openai if use_openai else llm_config_localcoder
    )
    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        #llm_config=llm_config_localgeneral,
        #code_execution_config=code_execution_enabled,
        max_consecutive_auto_reply=max_consecutive_auto_replies,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
        #code_execution_config={
        #    "work_dir": "coding",
        #    "use_docker": False,  # set to True or image name like "python:3" to use docker
        #},
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

    # Log the task to keep a record of what we're doing and help study/analyze results
    log_task = f"{task_output_directory}/task.txt"
    with open(log_task, 'a', encoding='utf-8') as log_file:
        log_file.write(task)

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
    dual_output = DualOutput(task_output_directory)
    sys.stdout = dual_output

    # Check if we have a input.txt file and if so use that as input to the AI to run on all lines of the file
    inputlines_array = []
    if os.path.exists(inputfile):
        print(f"=== Using inputfile: {inputfile}")
        #input = ""
        with open(inputfile, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.rstrip('\n')
                inputlines_array.append(line)
                #inputlines_array.append(line.strip())
                #input += line.strip() + "\n"

    if len(inputlines_array) > 0:
        print(f"=== Using inputlines_array size %d" % len(inputlines_array))
        #input = ""
        for inputline in inputlines_array:
            # Replace {$1} in task with the inputline
            task_line = task
            task_line = task_line.replace("{$1}", inputline)

            # If no files to create, do requested task
            #pause_capture in case our own task has code blocks in it - we don't want those auto-saving by mistake
            dual_output.PauseSaveFiles()
            print(f"=== Processing task: {task_line}")
            dual_output.UnpauseSaveFiles()

            if coder_only and no_user_proxy:
                response = coder.handle_task(task_line)
                print(response)
            elif coder_only:
                # Can we just let coder chat with itself to solve problems?
                # the assistant receives a message from the user_proxy, which contains the task description
                #coder.initiate_chat(
                user_proxy.initiate_chat(
                    coder if manager is None else manager,message=task_line,
                )
            else:
                # the assistant receives a message from the user_proxy, which contains the task description
                user_proxy.initiate_chat(
                    assistant,message=task_line,
                )
    elif do_refactor:
        #refactor.Refactor(worktree, refactor_wildcard, refactor_negmatches, "^[ \t]*tStrAppend", task, user_proxy, coder)
        # Iterate over array of wildcards e.g. "*.h" "*.cpp"
        for wildcard in refactor_wildcards:
            print("=== Processing wildcard: " + wildcard)
            refactor.Refactor(worktree, wildcard, refactor_matches, refactor_negmatches, task, user_proxy, coder)
    elif files_to_create:
        task_message = f"Please create the following files: {', '.join(files_to_create)} with the following specifications: {task}"
        #user_proxy.initiate_chat(assistant, message=create_task_message)
        if coder_only and no_user_proxy:
            response = coder.handle_task(task_message)
            print(response)
        elif coder_only:
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
        # Call the function to process files
        # This is maybe not going to be used anymore, not sure..
        process_files(files_to_send, worktree, targetfolder, task)
    else:
        # If no files to create, do requested task
        #pause_capture in case our own task has code blocks in it - we don't want those auto-saving by mistake
        dual_output.PauseSaveFiles()
        print(f"=== Processing task: {task}")
        dual_output.UnpauseSaveFiles()
        task_message=task
        if coder_only and no_user_proxy:
            response = coder.handle_task(task)
            print(response)
        elif coder_only:
            # Can we just let coder chat with itself to solve problems?
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
    with open(log_filename_base, 'a', encoding='utf-8') as log_file:
        log_file.write("Captured AI Output:\n")
        log_file.write(ai_output)

    # Create the log filename
    log_filename1 = f"{task_output_directory}/dj_AI_log.txt"
    # Write the AI output to the log file
    with open(log_filename1, 'w', encoding='utf-8') as log_file:
        log_file.write("Captured AI Output:\n")
        log_file.write(ai_output)

    # We're effectively doing below twice now ..
    # Use ai_output with create_files_from_ai_output function in order to actually create any files in the returned code
    create_files_from_ai_output(ai_output, task_output_directory + '/outfiles_final')

    # Print the captured output to the console
    print("=== Captured AI Output:")
    print(ai_output)


    # Get the current date and time
    formatted_datetime = task_datetime.strftime("%Y-%m-%d %H-%M-%S")
    # Create the log filename
    log_filename = f"dj AI final log - {formatted_datetime}.txt"
    # Write the AI output to the log file
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        log_file.write("Captured AI Output:\n")
        log_file.write(ai_output)
    print(f"=== Log saved in file: {log_filename}")

    #result = send_files_for_modification(args.task_description, args.header_file, args.source_file)
    #print(f'Modified files received: {result}')
    print("=== Done! All tasks processed.")

def get_task_from_user(task):
    """Checks if the task is empty or None, and prompts the user for input if it is."""
    while task is None or task.strip() == '':
        task = input("Please enter a task to perform: ").strip()
    return task
