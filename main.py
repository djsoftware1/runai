# Copyright (C) 2023-2024 David Joffe / DJ Software
# Import necessary libraries
import sys
import autogen
import os
import json
import requests
import io
import time
import datetime
from colorama import Fore, Style
from globals import g_ai_output_saved_last_code_block


# custom dual output to capture output and echo it to console so we can both log it and extract code from it but also see it in real-time
from dual_output import DualOutput
from helper_functions import create_files_from_ai_output
# This should probably only import if necessary/used if via commandline --version etc.:
import djrefactor
import djversion
import djargs
import djsettings
from djtasktypes import djTaskTypes
from djtask import djTask

# In future might want multiple settings objects for different things ...
#runtask = djSettings()
runtask = djTask()

##### system/script init:
# Get the directory of the current script (runai.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"{Fore.GREEN}=== Script directory: {script_dir}{Style.RESET_ALL}")

##### settings defaults
# dj2023-12 This anyway only works for Python currently and the user agent goes back and forth with coder and coder thinks there's a problem and sends the code again and again because user agent couldn't execute
# Even if it could exec C++ I don't currently want it to for these tasks so let's make this a parameter
# Maybe in future for some tasks it should be true eg simpler Python stuff it can exec or if it gets better in future
code_execution_enabled=False
# TODO also try let coder handle things more directly?
#max_consecutive_auto_replies=10
max_consecutive_auto_replies=0

task=''
task_folder = "tasks/copyright"
use_cache_seed=24
use_openai=False
use_openai=True

# Configuration
# Work in current folder by default unless otherwise specified
worktree = '.'#"src/tlex"
# can also override in your settings.py passed in as parameter:
#refactor_wildcards = ["*.cpp", "*.h"]
# Override this in runai-folder/defaultsettings.py if you want to use a different wildcard by default for all projects eg if you almost always work with C++
refactor_wildcards=[]
# This is not reeeeally used currently not sure if it will be in future:
refactor_codetype = "cpp"
#refactor_matches = "^[ \t]*tStrAppend"
#refactor_matches = r'tStrAppend\('
refactor_matches = '_regex_needle_to_find_'
# Note if replace_with defined then it's a simple regex replace that does not actually need AI and we just do ourselves
replace_with=''
# Don't change the actual function itself
#refactor_negmatches =["void tStrAppend("]
# can also override in your settings.py passed in as parameter:
refactor_negmatches=[]

do_refactor=False
# [Setting] default task file to use if none specified
taskfile='autotask.txt'
#if os.path.exists('autotask.txt'):
#    taskfile = 'autotask.txt'  # Or set a default value as needed
settings_pyscript = 'autosettings.py'
# [Setting] optional input file to run task for every line in file with substitution of "{$1}" in task text with each line
inputfile='input.txt'



# Slightly gross but use this global to capture output from AI of last most recent final code block it sent
#g_ai_output_saved_last_code_block=None

#files_to_send = ["djNode.h", "djNode.cpp"]
files_to_send = None
#files_to_create = ["djVec3d.h", "djVec3d.cpp"]
files_to_create=None
#targetfolder = "modified_tlex/DicLib"
# currently not used:
targetfolder = ''
# settings
# I need to experiment a bit more to see exactly the implications of not creating groups (or creating groups), both if I only have 1 AI agent available or if I have 2 or 3 machines I can use ..
NoGroup=True
#NoGroup=False
#MaxAgents=1
# dj try make setting to control if we have lots or fewer etc. of AIs to use:
# this needs further work though
coder_only=True
no_user_proxy=True
# [Setting] Control whether or not to use the autogen user proxy agent
#no_user_proxy=False




print("=== USAGE: runai (or python main.py) [taskfile] [targetfolder] [settings.py]")

# Check if defaultsettings.py exists in runai folder and run it if it does
default_settings = os.path.join(script_dir, "defaultsettings.py")
if os.path.exists(default_settings):
    # Read and exec the .py file
    settings_py = ''
    with open(default_settings, 'r', encoding='utf-8') as file:
        settings_py = file.read()
    exec(settings_py)


# [Application flow control]
force_show_prompt=False
just_show_settings=False
use_deprecating_old_arg_handling=True

# More generic new arg parser
CmdLineParser = djargs.CmdLineParser()
args = CmdLineParser.parser.parse_args()
# Check if a subcommand is provided
if args.version:
    # Display version and exit
    print(f"[runai] Version: {djversion.Version().get_version()}")
    sys.exit(0)
if args.showsettings:
    # Display settings and exit
    print(f"[runai] Version: {djversion.Version().get_version()}")
    just_show_settings = True
    #sys.exit(0)
if args.folder:
    # worktree: "." by default
    worktree = args.folder
if args.delay_between:
    # Delay between running multiple tasks
    runtask.delay_between = float(args.delay_between)
if args.dryrun:
    runtask.dryrun = True
if args.start_line:
    runtask.start_line = int(args.start_line)
if args.task:
    # e.g. "Say coffee 10 times, then help cure aging"
    task = args.task
if args.taskfile:
    # Read task from given taskfile? (optionally we can also use 'autotask.txt')
    taskfile = args.taskfile
if args.settings:
    # Per-task task-specific custom settings.py? (optionally we can also use 'autosettings.py')
    settings_pyscript = args.settings
if args.input:
    inputfile = args.input
if args.test:
    #use_sample_default_task=True
    task = "Write a Python function to sort a list of numbers."
    taskfile = ''
if args.prompt:
    # Force ask for task prompt from input?
    print("=== Force show user prompt for task: True")
    force_show_prompt = True
if args.subcommand:    
    if args.subcommand == 'refactor':
        print("TASK: Refactor")
        do_refactor = True
        runtask.type = djTaskTypes.refactor
        # Add all passed wildcards to refactor_wildcards array (which looks like e.g. refactor_wildcard = ["*.cpp", "*.h"])
        if args.wildcards:
            refactor_wildcards = args.wildcards
        if args.find_regex:
            refactor_matches = args.find_regex
        if args.replace_with:
            replace_with = args.replace_with
        if args.send:
            runtask.settings.send_files = args.send
        #print("Taskfile:", args.taskfile)
        #taskfile = args.taskfile
        use_deprecating_old_arg_handling = False
    elif args.subcommand == 'create':
        runtask.type = djTaskTypes.create
        if args.out:
            runtask.settings.out_files = args.out



# Check if autosettings.py exists in current folder and run it if it does
if os.path.exists('autosettings.py'):
    autosettings_py = ''
    # Read and exec the autosettings.py file
    with open('autosettings.py', 'r', encoding='utf-8') as file:
        autosettings_py = file.read()
    exec(autosettings_py)

# Parameter 3: task settings.py to run
# Put this just after all basic settings initialization so user can override all/most default settings
if settings_pyscript is not None and len(settings_pyscript) > 0:
    #settings_pyscript = sys.argv[3]
    print(f"{Fore.BLUE}=== Using custom settings.py: {settings_pyscript}{Style.RESET_ALL}")
    if os.path.exists(settings_pyscript):
        # Read the settings.py file
        with open(settings_pyscript, 'r', encoding='utf-8') as file:
            settings_py = file.read()
        # Execute the settings.py file
        exec(settings_py)


# Small helper to show setting name and value in different color
def show_setting(name, value):
    if value is not None:
        print(f"{Fore.GREEN}=== {name}:{Style.RESET_ALL} {Fore.CYAN}{value}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}=== {name}:{Style.RESET_ALL} {Fore.RED}-{Style.RESET_ALL}")

def show_settings():
    # TODO some of these settings may already be unused
    print(f"{Fore.BLUE}____________________________________________________{Style.RESET_ALL}")
    print(f"{Fore.BLUE}=== SETTINGS:")
    show_setting("Taskfile", taskfile)
    show_setting("Inputfile", inputfile)
    show_setting("Settings.py", settings_pyscript)
    show_setting("Worktree", worktree)
    show_setting("Targetfolder", targetfolder)
    show_setting("Task", task)
    show_setting("Files to send", files_to_send)
    show_setting("use_openai", use_openai)
    show_setting("have_openai_config", have_openai_config)
    show_setting("no_user_proxy", no_user_proxy)
    show_setting("NoGroup", NoGroup)
    show_setting("use_cache_seed", use_cache_seed)
    show_setting("code_execution_enabled", code_execution_enabled)
    show_setting("max_consecutive_auto_replies", max_consecutive_auto_replies)
    show_setting("refactor_matches", refactor_matches)
    show_setting("replace_with", replace_with)
    show_setting("refactor_wildcards", refactor_wildcards)
    show_setting("task.delay_between (seconds, float)", runtask.delay_between)
    show_setting("send_files", runtask.settings.send_files)
    show_setting("out_files", runtask.settings.out_files)
    show_setting("dryrun", runtask.dryrun)
    show_setting("start_line", runtask.start_line)
    #global config_list
    if config_list:
        # Convert the object to a JSON string and print it
        show_setting("config_list", json.dumps(config_list, indent=4))
    print(f"{Fore.BLUE}__________________________________{Style.RESET_ALL}")
    # TODO also try let coder handle things more directly?
    return



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
print(f"=== config_list_path: {config_list_path}")
# Check if the OAI_CONFIG_LIST file exists
if os.path.exists(config_list_path):
    #"model": ["gpt-4", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    if args.gpt4: # Force gpt4 if possible if --gpt4 passed?
        config_list = autogen.config_list_from_json(
            config_list_path,
            filter_dict={
                "model": ["gpt-4-1106-preview", "gpt-4", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
            },
        )
    elif args.gpt3: # Force gpt3 if possible if --gpt3 passed?
        # try use gpt-3.5-turbo instead of gpt-4 as seems costly to use gpt-4 on OpenAI
        config_list = autogen.config_list_from_json(
            config_list_path,
            filter_dict={
                "model": ["gpt-3.5-turbo"],
            },
        )
    else:
        # Default
        config_list = autogen.config_list_from_json(
            config_list_path,
            filter_dict={
                "model": ["gpt-3.5-turbo", "gpt-4-1106-preview"],
            },
        )
    have_openai_config = True

    llm_config_coder_openai={
        "config_list":config_list
    }
else:
    print("Warning: No OpenAI configuration - this is not critical if using local AI instances like LiteLLM")
    have_openai_config = False
    use_openai = False

if just_show_settings:
    show_settings()
    sys.exit(0)

show_settings()

# Get date/time to use in filenames and directories and session logfiles etc.
task_datetime = datetime.datetime.now()
task_formatted_datetime = task_datetime.strftime("%Y-%m-%d %H-%M-%S")
task_output_directory='.output_files_runai' + '/' + task_formatted_datetime
# Create the output directory if it doesn't exist
if not os.path.exists(task_output_directory):
    os.makedirs(task_output_directory)


# Read task from tasks.txt
#with open('tasks.txt', 'r') as file:
###with open('task.txt', 'r') as file:
###    task = file.read().strip()
###    print(f"===== agent TASK:{task}")
# Read all task lines from tasks.txt
#task = ""
if taskfile!='':
    if os.path.exists(taskfile):
        print(f"=== Using taskfile: {taskfile}")
        with open(taskfile, 'r', encoding='utf-8') as file:
            for line in file:
                task += line.strip() + "\n"  # Appending each line to the task string
    else:
        print(f"=== {Fore.BLUE}Taskfile not found:{Fore.CYAN} {taskfile}{Style.RESET_ALL}")

if task=="":
    # Define your coding task, for example:
    print(f"=== No task specified")
    #if not force_show_prompt:
        #print("=== Please specify a task in task.txt (or pass filename as 1st parameter) or use -p to prompt for a task or -t for default test/sample task")
        #task = "Write a Python function to sort a list of numbers."
        #print("=== Using default sample task: {task}")

#if task=="":
#    # Define your coding task, for example:
#    print("=== No task specified, using default task")
#    task = "Write a Python function to sort a list of numbers."

# Check if 'task' is an empty string or None
if task == "" or task is None or force_show_prompt:
    task = input(f"{Fore.BLUE}What would you like to do? Please enter a task:{Style.RESET_ALL} ")

    # Check if the user entered nothing
    if task == "":
        print("No task entered. Exiting the program.")
        sys.exit()

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
from colorama import init
init()

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
    log_task = f"{task_output_directory}/tasklog.txt"
    with open(log_task, 'a', encoding='utf-8') as log_file:
        log_file.write(task)

    if not NoGroup:
        print("=== Creating groupchat and manager")
        groupchat = autogen.GroupChat(agents=[user_proxy, coder, assistant], messages=[])
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config_localgeneral)
    else:
        print("=== no groupchat or manager")
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
        if runtask.dryrun:
            print(f"=== DRY RUN")
        line_number = 0
        for inputline in inputlines_array:
            line_number += 1
            print(f"=== LINE {line_number}/{len(inputlines_array)} [start-line:{runtask.start_line}]: {inputline}")
            if runtask.dryrun:
                print(f"=== DRY RUN")
            # Replace {$1} in task with the inputline
            task_line = task
            task_line = task_line.replace("{$1}", inputline)

            # If no files to create, do requested task
            #pause_capture in case our own task has code blocks in it - we don't want those auto-saving by mistake
            dual_output.PauseSaveFiles()
            print(f"=== Processing task: {task_line}")
            dual_output.UnpauseSaveFiles()
            if runtask.start_line > 0:
                # Skip lines until we reach start_line
                if line_number < runtask.start_line:
                    print(f"=== Skipping line {line_number} as it's before start_line {runtask.start_line}")
                    continue
            if runtask.dryrun:
                continue

            if coder_only and no_user_proxy:
                user_proxy.initiate_chat(
                    coder,message=task_line,
                )
                #response = coder.handle_task(task_line)
                #print(response)
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
            # Optional delay between each line (in milliseconds)? (e.g. to not hammer server)
            if runtask.delay_between:
                print(f"=== Sleeping {runtask.delay_between}s between tasks")
                time.sleep(runtask.delay_between)
    elif do_refactor:
        print("=== Do refactoring file(s)")
        #djrefactor.Refactor(worktree, refactor_wildcard, refactor_negmatches, "^[ \t]*tStrAppend", task, user_proxy, coder)
        # Iterate over array of wildcards e.g. "*.h" "*.cpp"
        for wildcard in refactor_wildcards:
            print("=== Processing wildcard: " + wildcard)
            #print(f"=== worktree: {worktree}")
            #print(f"=== targetfolder: {targetfolder}")
            print(f"=== refactor_matches: {refactor_matches}")
            print(f"=== replace_with (optional): {replace_with}")
            # Note if replace_with defined then it's a simple regex replace that does not actually need AI and we just do ourselves
            djrefactor.Refactor(worktree, wildcard, refactor_matches, refactor_negmatches, replace_with, task, user_proxy, coder)
    elif files_to_create and len(files_to_create)>=1:
        dual_output.PauseSaveFiles()
        if len(files_to_create)==1:
            task_message = f"Create the following file and return in a ```...``` code block with filename: {', '.join(files_to_create)} with the following specifications: {task}"
        else:
            task_message = f"Create the following files and return in ```...``` code blocks with filenames: {', '.join(files_to_create)} with the following specifications: {task}"
        dual_output.UnpauseSaveFiles()
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
    elif files_to_send and len(files_to_send)>=1:
        # If no files to create, do requested task
        dual_output.PauseSaveFiles()
        if len(files_to_send)==1:
            print(f"=== Sending file: {', '.join(files_to_send)}")
        else:
            print(f"=== Sending files: {', '.join(files_to_send)}")
        dual_output.UnpauseSaveFiles()
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
            user_proxy.initiate_chat(
                coder,message=task,
            )
            #response = coder.handle_task(task)
            #print(response)
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



    # Get the current date and time
    formatted_datetime = task_datetime.strftime("%Y-%m-%d %H-%M-%S")

    # Create the log filename
    # Not quite sure if this shoudl also be in task_output_directory or not
    log_filename_base = f"dj_AI_log.txt"
    # Write the AI output to the log file
    with open(log_filename_base, 'a', encoding='utf-8') as log_file:
        log_file.write(f"[{formatted_datetime}] Captured AI Output:\n")
        log_file.write(ai_output)
        log_file.write("----------------------\n")

    # Create the log filename
    log_filename1 = f"{task_output_directory}/dj_AI_log.txt"
    # Write the AI output to the log file
    with open(log_filename1, 'a', encoding='utf-8') as log_file:
        log_file.write(f"[{formatted_datetime}] Captured AI Output:\n")
        log_file.write(ai_output)
        log_file.write("----------------------\n")

    # We're effectively doing below twice now ..
    # Use ai_output with create_files_from_ai_output function in order to actually create any files in the returned code
    create_files_from_ai_output(ai_output, task_output_directory + '/outfiles_final')

    # Print the captured output to the console
    print("=== Captured AI Output:")
    print(ai_output)



    #result = send_files_for_modification(args.task_description, args.header_file, args.source_file)
    #print(f'Modified files received: {result}')
    print("=== Done! All tasks processed.")

#def get_task_from_user(task):
#    """Checks if the task is empty or None, and prompts the user for input if it is."""
#    while task is None or task.strip() == '':
#        task = input("Please enter a task to perform: ").strip()
#    return task

