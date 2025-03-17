# main.py
#
# runai - Run or Automate AI/LLM and other tasks (such as code refactoring), optionally with AutoGen. 
# Tasks may be non-AI-related (e.g. code or other document search-and-replace tasks), or we may use AI/LLM for tasks like code refactoring.
#
# See ReadMe.md for setup instructions, for instructions on how to use runai, and how to add it to your PATH.
#
# runai -h             → SHOW HELP
# runai -m MODEL       → Select Model to Use
# runai --showsettings → Just show settings
# 
# runai (dj-run-AI) Source Repo: https://github.com/djsoftware1/runai
# Created by David Joffe - 'Initially to try help with some of my own tasks, and partly as a learning exercise, but have not had enough time to work on it'.
# Copyright (C) 2023-2025 David Joffe / DJ Software
#==================================================================
# Import necessary libraries
import sys
import autogen
#import pyautogen as autogen
import os
import json
import requests
import io
import time
import datetime
# For colored text in output
from colorama import Fore, Style
from globals import g_ai_output_saved_last_code_block


# custom dual output to capture output and echo it to console so we can both log it and extract code from it but also see it in real-time
from dual_output import DualOutput
from helper_functions import create_files_from_ai_output
import djabout
import djrefactor
import djversion
import djargs
import djsettings
from djtasktypes import djTaskTypes
from djtask import djTask

# In future might want multiple settings objects for different things ...
#runtask = djSettings()
runtask = djTask()

# Show short core 'about this application' info on commandline - (dj)
djabout.djAbout().show_about()


##### system/script init:
# Get the directory of the current script (runai.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"{Fore.GREEN}=== Script directory: {script_dir}{Style.RESET_ALL}")


#==================================================================
#todo group all these settings better so it is clearer what is going on - dj2025-03
##### settings defaults
#==================================================================


####################
# TASK SETTINGS:
####################

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
#taskfile='optional-autostart-task.txt'
#if os.path.exists('autotask.txt'):
#    taskfile = 'autotask.txt'  # Or set a default value as needed
settings_pyscript = 'autosettings.py'
# [Setting] optional input file to run task for every line in file with substitution of "{$1}" in task text with each line
# -i "InputFile" a file of input lines to batch-run task on every line in file
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


####################
# AUTOGEN SETTINGS:
####################

# settings
# I need to experiment a bit more to see exactly the implications of not creating groups (or creating groups), both if I only have 1 AI agent available or if I have 2 or 3 machines I can use ..
NoGroup=True
#NoGroup=False
#MaxAgents=1
# dj try make setting to control if we have lots or fewer etc. of AIs to use:
# this needs further work though
coder_only=True

# [Setting] Control whether or not to use the autogen user proxy agent
# no_autogen_user_proxy
no_autogen_user_proxy=True
#no_autogen_user_proxy=False


####################
# LLM settings:
####################
user_select_preferred_model=''

#==================================================================


print(f"{Fore.YELLOW}=== {Fore.YELLOW}USAGE: runai (or python main.py) [taskfile] [targetfolder] [settings.py]{Style.RESET_ALL}")

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
    # We can't show settings right here yet because some of the settings to show depend on having parsed the rest of the command line
    # But should possibly try refactor to have it not be like that in future
    print(f"[runai] Version: {djversion.Version().get_version()}")
    just_show_settings = True
    #sys.exit(0)
if args.folder:
    # worktree: "." by default
    worktree = args.folder
if args.delay_between:
    # Delay between running multiple tasks
    runtask.delay_between = float(args.delay_between)
if args.model:
    # Specify preferred model to use
    user_select_preferred_model = args.model
    print(f"[args] TryUseModel: {user_select_preferred_model}")
elif args.o1_mini:
    user_select_preferred_model = "o1-mini"
    print(f"[args] TryUseModel: {user_select_preferred_model}")
elif args.o1_preview:
    user_select_preferred_model = "o1-preview"
    print(f"[args] TryUseModel: {user_select_preferred_model}")
if args.dryrun:
    runtask.dryrun = True
if args.start_line:
    # --start-line START_LINE           If using a multi-line task file, specify the start line number.
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
def show_setting(name, value, indent=0, descriptionString="", strKeyShortcut=""):
    # dj2025-03 add indent and descriptionString (optional)
    #sBULLET_INFO="→ 🛈"
    #sBULLET_INFO="→"
    sBULLET_INFO=""
    strDashesBefore="=== "
    if indent > 0:
        print("   " * indent, end="")
        strDashesBefore="■ "
        #strDashesBefore = sBULLET_INFO
    else:
        strDashesBefore="=== "
    
    strDescription=""
    if len(descriptionString) > 0:
        strDescription = f" {sBULLET_INFO} {Fore.MAGENTA}{descriptionString}{Style.RESET_ALL}"

    # e.g. "-f FOLDER" info stuff
    # ■ -f FOLDER: Nodjfsdj dsfkjl → Work-folder for tasks like auto-refactoring
    # ■ -t TASK: Hey there! tell me how to make cofee
    strShortCut=""
    if len(strKeyShortcut) > 0:
        strShortCut = f"{Fore.GREEN}{strKeyShortcut}{Style.RESET_ALL}"

    if value is not None:
        print(f"{Fore.GREEN}{strDashesBefore}{name}:{Style.RESET_ALL} {Fore.CYAN}{value}{Style.RESET_ALL}{strDescription} {strShortCut}")
    else:
        print(f"{Fore.GREEN}{strDashesBefore}{name}:{Style.RESET_ALL} {Fore.RED}-{Style.RESET_ALL}{strDescription} {strShortCut}")


def show_settings():
    # TODO some of these settings may already be unused
    print(f"{Fore.BLUE}____________________________________________________{Style.RESET_ALL}")
    #print(f"{Fore.BLUE}=== SETTINGS:"):
    print(f"{Fore.YELLOW}=== SETTINGS:")
    sBullet1='x'
    print(f"{Fore.YELLOW}{sBullet1} Task settings:{Style.RESET_ALL}")
    #default_values
    #default_values['InputFile']='input.txt'
    show_setting("TaskFile", taskfile, 1)#
    show_setting("InputFile", inputfile, 1, "input-file to batch-run task on all lines, with substitution", "-i")
    show_setting("Settings.py", settings_pyscript, 1)
    show_setting("WorkFolder", worktree, 1, "work-folder for tasks like auto-refactoring. (default: \".\" current-folder)", "-f")
    show_setting("TargetFolder", targetfolder, 1, "", "  ")
    show_setting("TASK", task, 1, "task string for LLM or agent to perform", "-t")
    show_setting("Files to send", files_to_send, 1)

    show_setting("max_consecutive_auto_replies", max_consecutive_auto_replies)
    show_setting("refactor_matches", refactor_matches)
    show_setting("replace_with", replace_with)
    show_setting("refactor_wildcards", refactor_wildcards)
    show_setting("task.delay_between (seconds, float)", runtask.delay_between)
    show_setting("send_files", runtask.settings.send_files)
    show_setting("out_files", runtask.settings.out_files)
    show_setting("dryrun", runtask.dryrun)
    show_setting("start_line", runtask.start_line)
    
    print(f"{Fore.YELLOW}{sBullet1} AutoGen settings:{Style.RESET_ALL}")
    show_setting("autogen.no_autogen_user_proxy", no_autogen_user_proxy, 1)
    show_setting("autogen.NoGroup", NoGroup, 1, "If True do not create autogen GroupChat and GroupChatManager")
    show_setting("autogen.use_cache_seed", use_cache_seed, 1, "random seed for caching and reproducibility")
    show_setting("autogen.code_execution_enabled", code_execution_enabled, 1, "Enable AutoGen agent code execution [currently always off]")
    show_setting("coder_only", coder_only, 1)
    
    # LLM SETTINGS/PREFERENCES/COMMAND-LINE OPTIONS
    print(f"{Fore.YELLOW}{sBullet1} LLM settings:{Style.RESET_ALL}")
    show_setting("TryUseModell", user_select_preferred_model, 1)
    sBULLET_SQUARE="■"
    print("   " * 2, end="")#indent
    print(f"{Fore.YELLOW}OpenAI settings:{Style.RESET_ALL}")
    show_setting("USE_OPENAI", 'YES' if use_openai is True else 'NO', 2)
    show_setting("HAVE_OPENAI_CONFIG?", have_openai_config, 2)
    if have_openai_config:
        show_setting("openai.config_list", config_list, 2)

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

"""
config_list_local_ollama=[
    {
        'base_url':"http://127.0.0.1:11434",
        #'model':'deepseek-r1:1.5b',
        'model':'gemma3:4b',
        'api_key':"NULL"
    }
]
"""
# [dj] local LiteLLM instances ...
config_list_localgeneral=[
    {
        """
        'base_url':"http://10.0.0.13:8000",
        """
        'base_url':"http://127.0.0.1:11434",
        #'model':'deepseek-r1:1.5b',
        'model':'gemma3:4b',
        'api_key':"NULL"
    }
]
config_list_localcoder=[
    {
        'base_url':"http://127.0.0.1:11434",
        #'model':'deepseek-r1:1.5b',
        'model':'gemma3:4b',
        'api_key':"NULL"
    }
]
config_list_localcoder=[
    {
        'base_url':"http://127.0.0.1:11434",
        #'model':'deepseek-r1:1.5b',
        'model':'gemma3:4b',
        'api_key':"NULL"
    }
]
config_list_local3=[
    {
        'base_url':"http://127.0.0.1:11434",
        'model':'gemma3:4b',#'model':'deepseek-r1:1.5b',
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

# Note: As of 25 Jan 2024 "gpt-4-turbo-preview" seems to basically supercede "gpt-4-1106-preview" and also is meant to always now point to the latest GPT-4 Turbo (and is also meant to be less "lazy") https://openai.com/blog/new-embedding-models-and-api-updates

# Construct the path to the OAI_CONFIG_LIST file
config_list_path = os.path.join(script_dir, "OAI_CONFIG_LIST")
print(f"=== config_list_path: {config_list_path}")
# Check if the OAI_CONFIG_LIST file exists
if os.path.exists(config_list_path):
    #"model": ["gpt-4", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    if args.gpt4: # Force gpt4 if possible if --gpt4 passed?
        print("[args] TryUseModel: gpt-4")
        user_select_preferred_model="gpt-4"
        config_list = autogen.config_list_from_json(
            config_list_path,
            filter_dict={
                "model": ["gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
            },
        )
    elif args.gpt3: # Force gpt3 if possible if --gpt3 passed?
        print("[args] TryUseModel: gpt-3")
        user_select_preferred_model="gpt-3"
        # try use gpt-3.5-turbo instead of gpt-4 as seems costly to use gpt-4 on OpenAI
        config_list = autogen.config_list_from_json(
            config_list_path,
            filter_dict={
                "model": ["gpt-3.5-turbo"],
            },
        )
    else:
        print("do autogen.config_list_from_json - default")
        # Default
        config_list = autogen.config_list_from_json(
            config_list_path,
            filter_dict={
                "model": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo-preview"],
            },
        )
    have_openai_config = True

    llm_config_coder_openai={
        "config_list":config_list
    }
else:
    print("Warning: No OpenAI configuration - this is not critical if using local AI instances like LiteLLM")
    #dj-check: should we set have_openai_config to False here? (dj2025-03)
    # should we override config_list ..not 100% sure
    #have_openai_config = False
    print("selecting config_list_localgeneral")
    config_list = config_list_localgeneral
    #config_list.model = ["deepseek-r1:1.5b"]
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
        status='found'
        #color='GREEN'
        print(f"{Fore.BLUE}■ {Fore.YELLOW}TaskFile: {taskfile}: {Fore.GREEN}{status}{Style.RESET_ALL}")
        print(f"=== {Fore.YELLOW}Loading TaskFile: {taskfile}{Style.RESET_ALL}")
        with open(taskfile, 'r', encoding='utf-8') as file:
            for line in file:
                task += line.strip() + "\n"  # Appending each line to the task string
        if len(task)==0:
            print(f"{Fore.RED}Warning: TaskFile is empty!{Style.RESET_ALL}")
    else:
        
        # [dj2025-03] Remember the file name "autotask.txt" is like a special "auto-start" "autotask.txt" task file that is fully optional
        # So if "taskfile" is not found, if it is on the default special  "auto-start" "autotask.txt" file, then we just print a message and continue
        status=''
        color='GREEN'
        if os.path.exists(taskfile):
            color = 'GREEN'
            if taskfile=='autotask.txt':
                status='found autostart.txt'
            else:
                # file exists and name is not "autostart.txt" (likely user used "-tf" to specify a taskfile)
                status='found'
        else: # FILE DOES NOT EXIST
            if taskfile=='autotask.txt':
                status='not found, but that is fine as autostart.txt is optional'
                color = 'GREEN'
            else:
                # file does not exist and name is not "autostart.txt" (likely user used "-tf" to specify a taskfile)
                status='ERROR: not found'# and this is bad because it is a red error for user!
                color = 'RED'

        if color=='RED':
            print(f"{Fore.BLUE}■ {Fore.YELLOW}TaskFile: {taskfile}: {Fore.RED}{status}{Style.RESET_ALL}")
            print(f"{Fore.RED}Please either create the file now with your task description, or specify a correct filename.{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}■ {Fore.YELLOW}TaskFile: {taskfile}: {Fore.GREEN}{status}{Style.RESET_ALL}")
        
        # dj2025-03 Hmm I am not sure I am mad about several lines of guidance info like this is good or bad here or if it should move elsewhere (low prio)
        print("--------------------------[ NOTES ]----------------------------")
        print("The name \"autotask.txt\" is a special OPTIONAL filename to \"auto-load/start\" the task.")
        print("It is the AUTOEXEC.BAT of runai, if you will.")
        print("If you want to use a different task file name, please specify it with the -tf parameter.")
        print("---------------------------------------------------------------")
        

if task=="":
    # Define your coding task, for example:
    print(f"■ No task specified")
    #if not force_show_prompt:
        #print("=== Please specify a task in task.txt (or pass filename as 1st parameter) or use -p to prompt for a task or -t for default test/sample task")
        #task = "Write a Python function to sort a list of numbers."
        #print("=== Using default sample task: {task}")

#if task=="":
#    # Define your coding task, for example:
#    print("=== No task specified, using default task")
#    task = "Write a Python function to sort a list of numbers."

# Check if 'task' is an empty string or None
# Show short core 'about this application' info on commandline - (dj)
#djabout.djAbout().show_about(True)

if task == "" or task is None or force_show_prompt:
    task = input(f"{Fore.CYAN}(Ctrl+C to stop) {Fore.YELLOW}What would you like to do? Please enter a task:{Style.RESET_ALL} ")

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
    print("--- start-main")
    # CWD is not so much a 'setting' as a 'current state' of runtime environment but we log it here anyway, it may be useful to know
    sCWD=os.getcwd()#getcwd just for logging
    print(f"• current-directory: {sCWD}")
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

        # string to show in front of output
        str_pre = "==="
        if runtask.dryrun:
            str_pre = "=== [dryrun]"
        for inputline in inputlines_array:
            line_number += 1
            # Check if skipping lines due to e.g. "--start-line" etc.?
            if runtask.start_line > 0 and line_number < runtask.start_line:
                print(f"{str_pre} LINE {line_number}/{len(inputlines_array)} [start-line:{runtask.start_line}]: {inputline} (SKIPPING)")
            else:
                print(f"{str_pre} LINE {line_number}/{len(inputlines_array)} [start-line:{runtask.start_line}]: {inputline}")
            #if runtask.dryrun:
            #    print(f"=== DRY RUN")
            # Replace {$1} in task with the inputline
            task_line = task
            task_line = task_line.replace("{$1}", inputline)
            # Replace ${line} with the line number
            task_line = task_line.replace(r'{$line}', str(line_number))
            
            # Note here we use exact date/time of each line not the start date/time of entire task start (later we might desire options for both)
            # Replace ${date} with the current date YYYY-MM-DD (UCT? I think UCT to prevent timezone unambiguity) .. I suppose we could have different variables for users later eg "$dateutc"
            if '{$date}' in task_line:
                now = datetime.datetime.utcnow()
                # Format date as YYYY-MM-DD
                task_line = task_line.replace(r'{$date}', now.strftime("%Y-%m-%d"))

            if '{$time}' in task_line:
                now = datetime.datetime.utcnow()
                # Format date as YYYY-MM-DD
                task_line = task_line.replace(r'{$time}', now.strftime("%H-%M-%S"))

            if '{$datetime}' in task_line:
                now = datetime.datetime.utcnow()
                # Format date as YYYY-MM-DD HH-MM-SS
                task_line = task_line.replace(r'{$datetime}', now.strftime("%Y-%m-%d %H-%M-%S"))

            # If no files to create, do requested task
            #pause_capture in case our own task has code blocks in it - we don't want those auto-saving by mistake
            if runtask.start_line > 0:
                # Skip lines until we reach start_line
                if line_number < runtask.start_line:
                    #print(f"=== Skipping line {line_number} as it's before start_line {runtask.start_line}")
                    continue

            # Log requested task but pause the savefiles thing otherwise it will auto grab our own codeblacks out the task
            dual_output.PauseSaveFiles()
            print(f"=== Processing task: {task_line}")
            dual_output.UnpauseSaveFiles()


            if runtask.dryrun:
                continue


            # Add some logging so user can see where we left off quickly if we need to restart
            log_task = f"_inputlines_tasklog_runinfo.log"
            with open(log_task, 'a', encoding='utf-8') as log_file:
                # Get date/time to use in filenames and directories and session logfiles etc.
                log_datetime = datetime.datetime.now()
                log_formatted_datetime = log_datetime.strftime("%Y-%m-%d %H-%M-%S")

                log_file.write(f"=== EXECUTING LINE {line_number}/{len(inputlines_array)} [start-line:{runtask.start_line}][{log_formatted_datetime}]: {inputline}\n")
                """
                log_file.write(f"=== EXECUTING LINE {line_number}/{len(inputlines_array)} [start-line:{runtask.start_line}]: {inputline}\n")
                """


            if coder_only and no_autogen_user_proxy:
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
        if coder_only and no_autogen_user_proxy:
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
        if coder_only and no_autogen_user_proxy:
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
    # Not quite sure if this should also be in task_output_directory or not
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

