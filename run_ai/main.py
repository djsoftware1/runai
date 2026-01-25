# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2023-2026 - Business Source License (BSL 1.1). See LICENSE
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
# runai create -h      → Subcommand help
# 
# runai website: https://djoffe.com/dj-software/runai/
# runai github repo: https://github.com/djsoftware1/runai
# Created by David Joffe - 'Initially to try help with some of my own tasks, and partly as a learning exercise, but have not had enough time to work on it'.
# Copyright (C) 2023-2026 David Joffe / DJ Software
#==================================================================

# todo[med] - add auto-todo named tasks
# todo[main.py djargs.py] - add batcat-if-have support --batcat
# todo[] stress-tests should have the dummy mode auto-generate exceptions to help test smooth recovery from errors from backends (eg 404s, 'no credit' API situations, other errors)

# Import necessary libraries
import sys
import io
# force utf8 for unicode handling etc.
sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer,
    encoding="utf-8",
    errors="replace",
)
from run_ai.backends.autogendetect import has_autogen
if has_autogen():
    import autogen
import os
import json
import requests
import io
import time
import datetime
import logging
# for attachments --attach:
import base64
import mimetypes
# For colored text in output
from colorama import Fore, Style
from .globals import g_ai_output_saved_last_code_block

# custom dual output to capture output and echo it to console so we can both log it and extract code from it but also see it in real-time
from .dual_output import DualOutput
from .helper_functions import create_files_from_ai_output
from . import djrefactor
from . import djversion
from . import djargs
from . import djsettings
from .djtasktypes import djTaskType
from .djtask import djTask
import run_ai.djabout # show_about() core about/usage info
from run_ai.config.display import show_setting
from run_ai.backends.selector import BackendSelector
from run_ai.backends.base import djAISettings
from run_ai.djapp import App
from run_ai.modelspec import parse_model_spec

from run_ai.djautogen.settings import djAutoGenSettings
from run_ai.config.settings import autogen_settings, djSettings

# task_output_directory/outfiles_final: output_runai/2026-01-01 02-14-53/outfiles_final (dj2026-01) .. someday make configurable (todo - low)
path_runai_out = 'runai_out' # was output_runai

#=== BACKEND SELECTOR:
#settings = djAISettings()
selector = None
backend = None

# AutoGen objects are created later (inside main()) but referenced by djAutoGenDoTask().
# Initialize them here so static analysis (flake8) and runtime both have defined names.
assistant = None
coder = None
user_proxy = None
groupchat = None
manager = None


# [dj2026-01] Redirect stdout to stderr
# but save stdout handle so we can just output
# that when we have the real output so that
# Unix piping of output works!
# e.g. we can do:
# $ runai -t "make a list" > newlist.txt
# $ runai -t "cure aging, thanks" |cowsay
# redirect testing stuff for stdoud todo and cleanup so we can pipe output
# This makes it very powerful as it becomes another composable Unix-style CLI tool!
import sys
save_real_stdout = sys.stdout
sys.stdout = sys.stderr


import logging
log = logging.getLogger("runai")

# careful, we have currently two djSettings, for in-progress refactoring ...dj2026-01
# we have 'default settings' and current user settings at runtime
#settings_default = runai_ai.config.djSettings()
settings_default = djsettings.djSettings()
settings_default.backend = 'openai'
# todo rename/refactor .. maybe move ..
settings_runai = djsettings.djSettings()
settings_runai = settings_default

# AI settings .. todo refactor this should live 'per task' for multi-task running in future
settings = djAISettings()

# this may be refactored away or elsewhere or differently later ... dj2026-01
def using_autogen():
    global use_backend
    if has_autogen() and use_backend=='autogen':
        return True
    return False

# Specify preferred model to use. NB you must save the return value. do_select_model() calls parse_model_spec()
def do_select_model(model: str):
    print(f"(select_model \"{model}\"",end='')
    # Specify preferred model to use
    global user_select_preferred_model
    user_select_preferred_model = model
    # Force use specified AI model
    #userconfig.model = args.model
    #print(f"Select Model: {user_select_preferred_model}")
    # in long run these globals should be refactored to live in module ... dj2026-01 todo
    global model_spec
    model_spec = parse_model_spec(model)
    # must use show setting to hide keys just in case
    show_setting(f"[DOSELECT] {Fore.YELLOW}MODEL{Fore.GREEN} '{model}' spec", model_spec, strEnd=')');

    # we may need to try auto-change selected default backend e.g. for anthropic
    #openai_compatible=['openai','xai','ollama','lmstudio']
    # note though Gemini is technically 'OpenAI compatible' it works differently to our OpenAI backend hence it's handle specially ...
    OPENAI_COMPATIBLE = {'openai', 'xai', 'ollama', 'lmstudio'}
    global use_backend
    if model_spec:
        provider = model_spec.get("provider")
        if provider:
            provider = provider.lower()        # use lower() kn case user passes e.g. "XaI/foo"
            # for now map deepseek to gemini as that seems to be closest to working but re-test still
            if provider=='google' or provider=='gemini' or provider=='deepseek':
                use_backend = 'gemini'
            if provider not in OPENAI_COMPATIBLE:
                use_backend = provider
                show_setting(f"[DOSELECT][{provider} backend={use_backend}] {Fore.YELLOW}MODEL{Fore.GREEN} '{model}' spec", model_spec, strEnd=')');

    show_setting(f"[DOSELECT][provider={provider} backend={use_backend}] {Fore.YELLOW}MODEL{Fore.GREEN} '{model}' spec", model_spec, strEnd=')');
    return model_spec

####################s
# LLM settings:
####################
user_select_preferred_model=''

# this will probably change in future but the idea is moving toward having general user settings like default backend
# there should also someday be project-specific backend selection stuff ... a bit like git global config vs local config
settings_default_backend='openai'
#settings_default_backend='autogen'
#settings_default_backend='dummy'
#use_backend='autogen'
use_backend=settings_runai.backend

# don't use more costly models by default but here for testing/convenience ..
#model_spec = parse_model_spec('openai/gpt-5.2')
# default .. gpt-4o-mini = cheaper default for mid-range tasks... dj2026-01
#model_spec = parse_model_spec('openai/gpt-4o-mini')
# hm wouldn't "do_select_model" be better than parse? yes...
model_spec = do_select_model('openai/gpt-4o-mini')

run_tests=False
# dj2026-01:
echo_mode=False
project_name = ''

# Quiet mode: suppress file output only (still prints to stdout/stderr)
quiet_file_output = False

# Attachments passed on command line
attach_files = []

#=== BACKEND SELECTOR:
#settings = djAISettings()
selector = None
backend = None

def djGetFormattedDatetime(datetime_input):
    #tmp_task_datetime = datetime.datetime.now()
    return datetime_input.strftime("%Y-%m-%d %H-%M-%S")

class SessionStats:
    def __init__(self):
        self.datetime_start = datetime.datetime.now()
        self.datetime_end = None
        self.elapsed_time = None
        # todo add more info - e.g. numerrors or numwarnings etc. ..

# runai App controller
class djAppController:
    def __init__(self):
        self.app = App(appname="runai")
        #self.runtask = djTask()
        self.app.app_dir = os.path.dirname(os.path.abspath(__file__))
        #self.config_list_path = os.path.join(self.app.app_dir, "OAI_CONFIG_LIST")
        self.session_stats = None

    def AppInitialize(self):
        # 'controller' app initialize
        # verbosity level?
        print(f"{Fore.GREEN}🤖 controller app-initialize{Style.RESET_ALL}")
        # Show short core 'about this application' info on commandline - (dj)
        run_ai.djabout.djAbout().show_about()
        # [dj2025-03]
        self.session_stats = SessionStats()
        print(f"{Fore.GREEN}=== App directory: {self.app.app_dir}{Style.RESET_ALL}")

    def AppDone(self):
        # 'controller' app-done
        #print(f"{Fore.GREEN}🤖 app-done{Style.RESET_ALL}")
        self.session_stats.datetime_end = datetime.datetime.now()
        self.session_stats.elapsed_time = self.session_stats.datetime_end - self.session_stats.datetime_start
        print(f"{Fore.GREEN}🤖 app-done: Elapsed time: {self.session_stats.elapsed_time}{Style.RESET_ALL}")


# Create a new application instance
#app = djapp.App(appname="runai")
controller=djAppController()
controller.AppInitialize()
app = controller.app

# In future might want multiple settings objects for different things ...
#runtask = djSettings()
runtask = djTask()



#==================================================================
#todo group all these settings better so it is clearer what is going on - dj2025-03
##### settings defaults
#==================================================================


####################
# TASK SETTINGS:
####################


task=''
task_folder = "tasks/copyright"

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
taskfile='runai.autotask.txt'#autotask.txt'
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
# !! todo clear up confusion between related settings here for output files:
#   ■ task_output_directory/outfiles_final: output_runai/2026-01-01 02-14-53/outfiles_final
#   ■ Task info:
#      ■ runtask.type: djTaskType.create
#      ■ files_to_create:
#         -> same idea as out_files but currently autogen code-path only which shouldn't be... should maybe be one setting? to think about ..
#      ■ files_to_send: -
#   ■ File-related info:
#      ■ runtask.settings.out_files: ['test1.cpp']
files_to_create=None
#targetfolder = "modified_tlex/DicLib"
# currently not used:
targetfolder = ''


#==================================================================
##user_proxy.initiate_chat(coder, message=task_message)
# This started as autogen-specific then we added more backends
# The idea is to refactor more still .. everywhere this appears - dj2026
def djAutoGenDoTask(task: str, do_handle_task=False):#, settings_ai=settings):
    global assistant, coder, user_proxy, manager

    # DEBUG/INFO START
    # verbose debug info: Show MODEL SPEC and backend used just before task exec:
    show_setting('[backend',use_backend,strEnd='')
    global settings
    if settings.model_spec:
        for key, value in settings.model_spec.items():
            # this is confusing 'key, value' is standard map terminology yes but "key" below is entirely different.
            # it means if this is a value like "api_key" hide it as it's sensitive!
            if "key" in key.lower() and value:
                value = '.'
            show_setting(f"{Fore.YELLOW}{key}", value, strEnd='')
        print("]")
    # DEBUG/INFO END
    # todo scalability[low] put fastest paths first ..

    global selector
    if selector is None:
        raise RuntimeError('Error[runai]: Should have backend selector if we have reached here')

    print(f"{Fore.YELLOW}■ DOTASK[{use_backend}]: {Fore.CYAN}{task}{Style.RESET_ALL}")
    # dj2026 add if not have autogen just return
    #if not run_ai.backends.autogendetect.have_autogen():
    if use_backend=='autogen' and not has_autogen():
        if not selector is None:
            print(f"{Fore.YELLOW}■ DOTASK[{use_backend}]: ERROR: autogen selected but not supported - falling back{Style.RESET_ALL}")
            result = selector.do_task(task)
            backend = selector.get_backend()
            return result
        # should not happen? todo test and clean up all this .. dj2026
        print(f"{Fore.RED}■ DOTASK[{use_backend}]: ERROR: autogen selected but not supported{Style.RESET_ALL}")
        # don't really want exception but for now want to debug incorrectly being here
        raise RuntimeError('autogen selected but not supported')
        return ''
    # If we aren't using ..
    if use_backend!='autogen':
        #result = djAutoGenDoTask(task)
        result = selector.do_task(task)
        backend = selector.get_backend()

        if len(backend.error)>0:
            print(f"■ DoTask[backend:{selector.backend_name}] {Fore.RED}ERROR: {backend.error}. RESPONSE:{Style.RESET_ALL}")
            print(f"{Fore.RED}{backend.response}{Style.RESET_ALL}")
            print(f"{Fore.RED}{result}{Style.RESET_ALL}")
            #print(f"{result}")
        else:
            print(f"■ DoTask[backend:{selector.backend_name}] {Fore.GREEN}SUCCESS:{Style.RESET_ALL}")
            #print(f"{Fore.GREEN}{result}{Style.RESET_ALL}")
            global dual_output
            global save_real_stdout
            if dual_output is not None:
                dual_output.begin_ai()
            print(result,end="") # no automatic newline or we end up with an extra newline in the captured output

            # PIPE TO STDOUT!
            # THIS IS THE REAL IMPORTANT OUTPUT THAT CAN BE PIPED:
            print(result, file=save_real_stdout, end='')
            # prefix = 'runai-AGI say: '
            #print(f"runai-AGI say: {result}", file=save_real_stdout, end='')
            #sys.stdout = save_real_stdout
            # todo should we flush?
            # NB: in Windows testing it seems save_real_stdout can become invalid along the way
            # so we avoid save_real_stdout.flush here
            #save_real_stdout.flush()


            # this should be optional but add more saving of results
            # todo put project name in here too
            global project_name
            if not quiet_file_output:
                if len(project_name)>0:
                    with open(f'_runai_out_all-{project_name}.txt', 'a', encoding='utf-8', errors="replace") as f:
                        f.write(f"{result}\n")
                else:
                    with open('_runai_out_all.txt', 'a', encoding='utf-8', errors="replace") as f:
                        f.write(f"{result}\n")

            # TODO: add safer handlers and checks also eg wrap in exception check etc. in case handle is invalid
            #sys.stdout.flush()
            if dual_output is not None:
                dual_output.end_ai()
            #dual_output.flush()

        # Use the backend selector to get the appropriate backend for the task
        #backend = selector.get_backend()
        #ret = backend.do_task(task)
        print(f"{Fore.YELLOW}■ DOTASK DONE{Style.RESET_ALL}")
        return result

    # dj refactoring 2025 .. only the create task  currently does this do_handle_task=True behavior ... todo, check if this is still needed
    # task_message = f"Create the following file and return in a ```...``` code block with filename: {', '.join(files_to_create)} with the following specifications: {task}"
    """
    # task_message = f"Create the following file and return in a ```...``` code block with filename: {', '.join(files_to_create)} with the following specifications: {task}"
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
    """
    if not has_autogen():
        raise RuntimeError('check fallback path autogen not supported')
        return ''

    response = ''
    # not 100% sure about these yet .. dj2026-01:
    if dual_output is not None:
        dual_output.begin_ai()
    if autogen_settings.coder_only and autogen_settings.no_autogen_user_proxy:
        if do_handle_task:
            response = coder.handle_task(task)
            print(response)
        else:
            user_proxy.initiate_chat(
                coder,message=task,
            )
    elif autogen_settings.coder_only:
        # Can we just let coder chat with itself to solve problems?
        # the assistant receives a message from the user_proxy, which contains the task description
        #coder.initiate_chat(
        ##ChatResult result =
        user_proxy.initiate_chat(
            coder if manager is None else manager,message=task,
        )
    else:
        # the assistant receives a message from the user_proxy, which contains the task description
        ##ChatResult result =
        user_proxy.initiate_chat(
            assistant,message=task,
        )
    if dual_output is not None:
        dual_output.end_ai()
    print(f"{Fore.YELLOW}=== DOTASK DONE{Style.RESET_ALL}")
    return ''
#==================================================================


print(f"{Fore.YELLOW}=== {Fore.YELLOW}USAGE: runai (or python main.py) [taskfile] [targetfolder] [settings.py]{Style.RESET_ALL}")

# dj2026-01 auto-detect warning
if not has_autogen():
    print(f"{Fore.YELLOW}WARNING autogen modules not found, disabling autogen support{Style.RESET_ALL}")
#print(f"DBG:done has-autogen check")

# Check if defaultsettings.py exists in runai folder and run it if it does
default_settings = os.path.join(app.app_dir, "defaultsettings.py")
if os.path.exists(default_settings):
    # Read and exec the .py file
    settings_py = ''
    with open(default_settings, 'r', encoding='utf-8', errors="replace") as file:
        settings_py = file.read()
    #print(f"DBG:runai:exec[{default_settings}]: {Fore.GREEN}{settings_py}{Style.RESET_ALL}")
    exec(settings_py)
    #print(f"DBG:runai:exec done")

#else:
#	print(f"No default_settings py")

# dj2026-01 UNIX-STYLE PIPED INPUT e.g. cat myfile.txt | runai -t "Summarize this"
"""
def read_stdin_if_piped():
    if sys.stdin is None:
        return None
    if sys.stdin.isatty():
        return None
    #return sys.stdin.read().strip()
    data = sys.stdin.buffer.read()
    # if we just return sys.stdin.read().strip() we get errors like "UnicodeEncodeError: 'utf-8' codec can't encode character '\udc8f' in position 22036: surrogates not allowed"
    # doing this seems to fix it but we must do more testing ... not sure if it's obscure edge cases or common etc.: dj 2026-01
    return data.decode("utf-8", errors="replace")
"""
# dj2026-01 UNIX-STYLE PIPED INPUT e.g. cat myfile.txt | runai -t "Summarize this"
"""
def read_stdin_if_piped():
    try:
        if sys.stdin is None:
            return None

        # If running interactively, do not read
        if sys.stdin.isatty():
            return None

        # On Windows / embedded shells, stdin may be a pipe with no data
        # Use non-blocking check
        if hasattr(sys.stdin, "buffer"):
            import select
            if not select.select([sys.stdin], [], [], 0.0)[0]:
                return None

        data = sys.stdin.buffer.read()
        if not data:
            return None

        return data.decode("utf-8", errors="replace")

    except Exception:
        return None

def read_stdin_if_piped():
    try:
        stdin = sys.stdin

        if stdin is None:
            return None

        # Interactive terminal → do not read
        if stdin.isatty():
            return None

        # Read everything (safe for pipes & redirects)
        data = stdin.buffer.read()

        if not data:
            return None

        return data.decode("utf-8", errors="replace")

    except Exception:
        return None
"""

# fix blocks inside runai-studio .. dj2026-01
def read_stdin_if_piped():
    try:
        stdin = sys.stdin
        #DEBUG:print("AAAAA")
        if stdin is None or stdin.isatty():
            return None

        #DEBUG:print("AAAAA")
        # --- UNIX: use select ---
        if os.name != "nt":
            import select
            r, _, _ = select.select([stdin], [], [], 0)
            if not r:
                return None
            #DEBUG:print("AAAAA1")
            data = stdin.buffer.read()
            #DEBUG:print("AAAAA2")
            return data.decode("utf-8", errors="replace") if data else None

        # --- WINDOWS: use msvcrt ---
        else:
            import msvcrt
            #DEBUG:print("wAAAAA")

            # If no key waiting, stdin pipe has no data
            if not msvcrt.kbhit():
                return None

            #DEBUG:print("wAAAAA")
            data = stdin.buffer.read()
            return data.decode("utf-8", errors="replace") if data else None

    except Exception:
        return None
# read stdin
#log = logging.getLogger(__name__)
#log.debug(f"read stdin")

print(f"read stdin")#DEBUG
stdin_text = read_stdin_if_piped()
#print(f"DBG:read stdin done: [{stdin_text}]")#DEBUG


# [Application flow control]
force_show_prompt=False
just_show_settings=False
use_deprecating_old_arg_handling=True


def resolve_setting(key, defaultValue=''):
    #if cli.has(key):
    #    return cli[key], "cli"
    # e.g. "task" -> "RUNAI_TASK"
    key_env = f"RUNAI_{key.upper()}"
    if key_env in os.environ:
        #if env.has(f"RUNAI_{key.upper()}"):
        env_value = os.getenv(key_env)
        print(f"{Fore.CYAN}{Fore.YELLOW}{key_env}{Fore.CYAN}={Fore.GREEN}{env_value}{Style.RESET_ALL}",end=' ')
        return env_value
    else:
        print(f"{Fore.CYAN}{Fore.YELLOW}{key_env}{Fore.CYAN}={Style.RESET_ALL}", end=' ')

    #if config.has(key):
    #    return config[key], "config"
    #if defaults.has(key):
    #    return defaults[key], "default"
    #return infer(key), "auto"
    return defaultValue

"""
SETTINGS = [
    "model", "task", "taskfile", "max_tokens", "temperature", "project", "quiet"
]
"""
print(f"resolve settings")
print(f"{Fore.CYAN}ENV {Style.RESET_ALL}",end=' ')
task = resolve_setting('task')
model = resolve_setting('model')
project_name = resolve_setting('project')
taskfile = resolve_setting('taskfile', 'runai.autotask.txt')
print("")
if model:
    # we must do this to parse model_spec and set up backend and so on ... though -m may override later again:
    model_spec = do_select_model(model)
"""
RUNAI_MODEL=ollama/deepseek
RUNAI_BACKEND=ollama
RUNAI_TEMPERATURE=0.7
RUNAI_MAX_TOKENS=4096
RUNAI_PROFILE=lexicography
RUNAI_POSTPROCESSOR=cowsay
ENV_VARS = {
    "RUNAI_MODEL": {
        "description": "Preferred AI model",
        #"call": lambda v: do_select_model(v)  # Fixed lambda syntax
    }
}
"""

#print(f"CmdLineParse")
# More generic new arg parser (dj2025 we must pass appname here so it does noto show "usage: main.py")
CmdLineParser = djargs.CmdLineParser(app.appname)
#print(f"DBG:1")
args = CmdLineParser.parser.parse_args()
#print(f"DBG:2")
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
if args.quiet:
    quiet_file_output = True
if args.folder:
    # worktree: "." by default
    worktree = args.folder
if args.delay_between:
    # Delay between running multiple tasks
    runtask.delay_between = float(args.delay_between)
if args.djchat:
    use_backend = 'djchat'
elif args.openai:
    use_backend = 'openai'
elif args.dummy:
    use_backend = 'dummy'
elif args.echo: # dummy backend but in echo mode
    use_backend = 'dummy'
    echo_mode = True
elif args.autogen:
    if not has_autogen():
        print("No autogen support, try install the required modules")
    else:
        use_backend = 'autogen'
else:
    use_backend = settings_runai.backend

if args.model:
    # Specify preferred model to use
    user_select_preferred_model = args.model
    model_spec = do_select_model(user_select_preferred_model)
    #show_setting(f"[args] MODEL {args.model}", model_spec);
    show_setting(f"[args] {Fore.YELLOW}MODEL{Fore.GREEN} '{args.model}' spec", model_spec);
if args.project:
    # Set the project name
    project_name = args.project
    print(f"[args] Project Name: {project_name}")
elif args.gpt4:
    user_select_preferred_model = "gpt-4"
    print(f"[args] Select Model: {user_select_preferred_model}")
elif args.gpt3:
    user_select_preferred_model = "gpt-3"
    print(f"[args] Select Model: {user_select_preferred_model}")
elif args.o1_mini:
    user_select_preferred_model = "o1-mini"
    print(f"[args] Select Model: {user_select_preferred_model}")
elif args.o1_preview:
    user_select_preferred_model = "o1-preview"
    print(f"[args] Select Model: {user_select_preferred_model}")
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
if args.attach:
    attach_files = args.attach
#elif stdin_text:
#    task = stdin_text
if args.test:
    #use_sample_default_task=True
    run_tests=True
    #task = 'Say Hi 3 times'
    #task = "Write a Python function to sort a list of numbers."
    taskfile = ''
if args.prompt:
    # Force ask for task prompt from input?
    print("=== Force show user prompt for task: True")
    force_show_prompt = True
if args.subcommand:
    if args.subcommand == 'refactor':
        print("TASK: Refactor")
        do_refactor = True
        runtask.type = djTaskType.refactor
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
        runtask.type = djTaskType.create
        if args.out:
            runtask.settings.out_files = args.out
    elif args.subcommand == 'build':
        runtask.type = djTaskType.build
        if args.exec:
            # Specify the file to exec
            runtask.settings.exec = args.exec
    #elif args.subcommand == 'modify' or args.subcommand == 'edit':
    elif args.subcommand == 'modify':
        runtask.type = djTaskType.modify
        if args.editfile:
            # Specify the file to edit
            runtask.settings.send_files = [ args.editfile ]
            runtask.settings_modify.send_files = [ args.editfile ]
        if args.edit:
            runtask.settings.send_files = args.edit
            runtask.settings_modify.send_files = args.edit
        ################## ?
        # dj: clean up and consolidate and simplify these various sendfile settings ...
        # dj I guess maybe we should copy this to files_to_send? hm ..
        #files_to_send = runtask.settings.send_files
        # Add all passed wildcards to refactor_wildcards array (which looks like e.g. refactor_wildcard = ["*.cpp", "*.h"])
        refactor_wildcards = ''
        refactor_matches = ''
        replace_with = ''
        #runtask.settings.send_files = args.send
        #files_to_send = runtask.settings.send_files

        #if args.exec:
            # Specify the file to exec
         #   runtask.settings.exec = args.exec
    else:
        print(f"Unknown subcommand: {args.subcommand}")


"""
#--enable-startup-script
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
"""

# ATTACHMENTS
def _guess_mime_type(path: str) -> str:
    mt, _ = mimetypes.guess_type(path)
    if mt:
        return mt
    return "application/octet-stream"

def _is_image_mime(mime_type: str) -> bool:
    return isinstance(mime_type, str) and mime_type.startswith("image/")

def _load_attachments(paths):
    """
    Returns list of attachment dicts:
      { path, filename, mime_type, kind, data_base64 }
    kind: "image" or "file"
    """
    attachments = []
    if not paths:
        return attachments

    for p in paths:
        if p is None:
            continue
        path = os.path.expanduser(p)
        if not os.path.isabs(path):
            path = os.path.abspath(path)

        if not os.path.exists(path):
            print(f"{Fore.RED}ERROR: attachment not found: {path}{Style.RESET_ALL}")
            continue
        if os.path.isdir(path):
            print(f"{Fore.RED}ERROR: attachment is a directory (expected file): {path}{Style.RESET_ALL}")
            continue

        mime_type = _guess_mime_type(path)
        kind = "image" if _is_image_mime(mime_type) else "file"
        filename = os.path.basename(path)

        try:
            with open(path, "rb") as f:
                data = f.read()
            data_b64 = base64.b64encode(data).decode("ascii")
        except Exception as e:
            print(f"{Fore.RED}ERROR: failed to read attachment {path}: {e}{Style.RESET_ALL}")
            continue

        attachments.append({
            "path": path,
            "filename": filename,
            "mime_type": mime_type,
            "kind": kind,
            "data_base64": data_b64,
        })

    return attachments
################################




def show_settings():
    # TODO some of these settings may already be unused
    print(f"{Fore.BLUE}____________________________________________________{Style.RESET_ALL}")
    #print(f"{Fore.BLUE}=== SETTINGS:"):
    print(f"{Fore.YELLOW}=== SETTINGS:")
    #print(f"default_backend={settings_runai.backend}")
    # show_setting gives us not just things like coloring but critical things like hiding sensitive keys!
    # SHOW DEFAULT SETTINGS?
    #show_setting('default-backend', settings_runai.backend)#, strEnd=' ')
    #show_setting('default-backend', settings_runai.backend, strEnd=' ')

    sBullet1='x'
    sBullet1='→'
    sBullet1='● '
    #sBullet1='_'
    #sBullet1='__'
    #sBullet1=''
    sHeadingSuffix='________'
    sHeadingSuffix=''
    print(f"{Fore.YELLOW}{sBullet1}Task settings:{Style.RESET_ALL}")
    #default_values
    #default_values['InputFile']='input.txt'
    show_setting("TaskFile", taskfile, 1)#
    show_setting("InputFile", inputfile, 1, "input-file to batch-run task on all lines, with substitution", "-i")
    if stdin_text!='':
        show_setting('STDIN', True, 1)
    show_setting("Settings.py", settings_pyscript, 1)
    show_setting("WorkFolder", worktree, 1, "work-folder for tasks like auto-refactoring. (default: \".\" current-folder)", "-f")
    show_setting("TargetFolder", targetfolder, 1, "", "  ")
    show_setting("TASK", task, 1, "task string for LLM or agent to perform", "-t")

    show_setting("runtask.type", runtask.type, 1)
    show_setting("runtask.delay_between (seconds, float)", runtask.delay_between, 1)
    show_setting("runtask.start_line", runtask.start_line, 1)

    show_setting("runtask.send_files", runtask.settings.send_files, 1)
    show_setting("runtask.out_files", runtask.settings.out_files, 1)

    show_setting("Files to send", files_to_send, 1)

    show_setting(f"{Fore.YELLOW}task.refactor:{Fore.GREEN} refactor_matches", refactor_matches, 1)

    show_setting("replace_with", replace_with, 2)
    show_setting("refactor_wildcards", refactor_wildcards, 2)
    #show_setting("task.settings.send_files", runtask.settings.send_files, 2)


    show_setting(f"{Fore.YELLOW}task.modify{Fore.GREEN}.send_files", f"{runtask.settings_modify.send_files}", 1)

    if attach_files:
        show_setting("Attachments (--attach/-a)", attach_files, 1)

    # HEADING
    enabled = ''
    if not using_autogen():
        enabled = ' [inactive] '
    print(f"{Fore.YELLOW}{sBullet1}AutoGen settings:{sHeadingSuffix}{Style.RESET_ALL}{enabled}")
    show_setting("no_autogen_user_proxy", autogen_settings.no_autogen_user_proxy, 1)
    show_setting("NoGroup", autogen_settings.NoGroup, 1, "If True do not create autogen GroupChat and GroupChatManager")
    show_setting("use_cache_seed", autogen_settings.use_cache_seed, 1, "random seed for caching and reproducibility")
    show_setting("code_execution_enabled", autogen_settings.code_execution_enabled, 1, "Enable AutoGen agent code execution [currently always off]")
    show_setting("coder_only", autogen_settings.coder_only, 1)
    show_setting("max_consecutive_auto_replies", autogen_settings.max_consecutive_auto_replies, 1)

    #sBULLET_SQUARE="■"
    #print("   " * 2, end="")#indent
    # why showing twice
    # HEADING
    print(f"   {Fore.YELLOW}{sBullet1}AutoGen OpenAI settings:{sHeadingSuffix}{Style.RESET_ALL}")
    show_setting("USE_OPENAI", 'YES' if use_openai is True else 'NO', 2)
    show_setting("HAVE_OPENAI_CONFIG?", have_openai_config, 2)
    if have_openai_config:
        # NB hide sensitive data like API keys
        s = f"{config_list}"
        #s = re.sub(r'sk-(.*)["\']', "\"(hidden)\"", s, flags=re.MULTILINE)
        #show_setting("openai.config_list", config_list, 1)
        show_setting("openai.config_list", s, 2)
    # HEADING
    # LLM SETTINGS/PREFERENCES/COMMAND-LINE OPTIONS
    print(f"{Fore.YELLOW}{sBullet1}LLM settings:{sHeadingSuffix}{Style.RESET_ALL}")

    #global config_list
    if config_list:
        # Convert the object to a JSON string and print it
        #show_setting("global.config_list", json.dumps(config_list, indent=4))
        # todo if we add a --verbose or something
        s = json.dumps(config_list)
        #s = re.sub(r'sk-(.*)["\']', "\"(hidden)\"", s, flags=re.MULTILINE)
        """
        'api_key': '"s(key_hidden)"}]
         config_list: [
        """
        show_setting("global.config_list", s)
    show_setting("dryrun", runtask.dryrun, strEnd=' ')
    show_setting("echo_mode", echo_mode, strEnd=' ')
    show_setting("quiet_file_output (-q)", quiet_file_output, strEnd=' ')
    show_setting(f'MODEL: "{user_select_preferred_model}" modelspec', model_spec);
    show_setting("selected-backend", use_backend, defaultValue=settings_default.backend)
    print(f"{Fore.BLUE}__________________________________{Style.RESET_ALL}")
    # TODO also try let coder handle things more directly?
    return



##### Local AI instance configuration (should make this easier in future to chop and change for specific tasks/setups etc.)
# Either via command-line or extra setuup.py or both etc. or maybe even environment variables
# e.g. maybe in future could look in local folder for settings.py and if found exec it after these defaults

"""
config_list_local_ollama=[
    {
        'base_url':"http://127.0.0.1:11434/v1",
        'model':'gemma3:1b',
        'api_key':"NULL"
    }
]
config_list_localgeneral_LITELLM=[
    {
        'base_url':"http://127.0.0.1:8000/v1",
        'model':'gemma-3-4b-it',
        'api_key':"NULL"
    }
]
"""
# [dj] local LiteLLM instances ...
config_list_localgeneral=[
    {
        #'base_url':"http://127.0.0.1:8000",#'base_url':"http://127.0.0.1:11434/v1/chat/completions",
        'base_url':"http://127.0.0.1:11434/v1",
        'model':'gemma3:1b',#'model':'gemma-3-4b-it',
        #'model':'deepseek-r1:1.5b',
        #'model':'gemma3:4b',
        'api_key':"NULL"
    }
]
config_list_localcoder=[
    {
        #'base_url':"http://127.0.0.1:8000",
        'base_url':"http://127.0.0.1:11434/v1",
        'model':'gemma3:1b',#'model':'gemma-3-4b-it',
        #'model':'deepseek-r1:1.5b',
        #'model':'gemma3:4b',
        'api_key':"NULL"
    }
]
config_list_localcoder=[
    {
        #'base_url':"http://127.0.0.1:8000",
        'base_url':"http://127.0.0.1:11434/v1",
        'model':'gemma3:1b',#'model':'gemma-3-4b-it',
        #'model':'deepseek-r1:1.5b',
        #'model':'gemma3:4b',
        'api_key':"NULL"
    }
]
config_list_local3=[
    {
        'base_url':"http://127.0.0.1:11434/v1",
        'model':'gemma3:1b',#'model':'gemma-3-4b-it',
        #'model':'deepseek-r1:1.5b',
        #'model':'gemma3:4b',
        'api_key':"NULL"

    }
]

#testing
config_list_local_ollama=[
    {
        #'base_url':"http://127.0.0.1:11434/v1/chat/completions",
        'base_url':"http://127.0.0.1:11434/v1",
        #'model':'lm_studio/deepseek-r1:1.5b',#'model':'gemma3:4b',
        'model':'gemma3-1b',#'model':'gemma-3-4b-it',#'model':'gemma3:4b',
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

print(f"=== user_select_preferred_model: \"{user_select_preferred_model}\"")
# Construct the path to the OAI_CONFIG_LIST file
config_list_path = os.path.join(app.app_dir, "OAI_CONFIG_LIST")
"""
print(f"=== config_list_path: {config_list_path}")
"""
if os.path.exists(config_list_path):
    print(f"=== config_list_path: {config_list_path} {Fore.GREEN}(file found){Style.RESET_ALL}")
else:
    if using_autogen():
        print(f"=== config_list_path: {config_list_path} {Fore.RED}warning: not found - please configure.{Style.RESET_ALL}")
        print("Try attempt fallback to local AI instances")
        # todo: fallback stuff (autogen and non-autogen paths)
    else:
        print(f"=== config_list_path: {config_list_path} {Fore.GREEN}not found (autogen inactive).{Style.RESET_ALL}")
        #print("Will attempt fallback to local AI instances")

    #"deepseek-r1:1.5b""
    # TESTING: Try fall back to local ollama ...
    # ollama is meant to be API-compatible with OpenAI but I'm not 100% sure if we should pass here the ollama modelname or give it modelname "gpt-4" in a sort of pretense for autogen
    # [dj] I think we should TRY pass the ollama modelname here, as it is a different model and we should be explicit about what we are using
    # (Unless override is specific with user_select_preferred_model?)

    #config_list_path = os.path.join(app.app_dir, "userconfigs/local_ollama.json")
    _try_config_list_path = os.path.join(app.app_dir, "configs/local_ollama.json")
    if os.path.exists(_try_config_list_path):
        print(f"=== TRY config_list_path FALLBACK: {_try_config_list_path}")
        model = "deepseek-r1:1.5b"
        if user_select_preferred_model:
            model = user_select_preferred_model
            print(f"TRY USE MODEL: {user_select_preferred_model}")
        config_list = autogen.config_list_from_json(
            _try_config_list_path,#config_list_local_ollama,
            filter_dict={
                #"model": ["deepseek-r1:1.5b","gpt-4"],
                "model": [model, "gpt-4"],
            },
        )

# Check if the OAI_CONFIG_LIST file exists
# dj2026-01 should we just not do this at all if no autogen or does it make sense for other backends?
if os.path.exists(config_list_path) and has_autogen():
    #"model": ["gpt-4", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    if user_select_preferred_model=="gpt-4": # Force gpt4 if possible if --gpt4 passed?
        print("Trying selected model gpt-4")
        config_list = autogen.config_list_from_json(
            config_list_path,
            filter_dict={
                "model": ["gpt-4", "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
            },
        )
    elif user_select_preferred_model=="gpt-3": # Force gpt3 if possible if --gpt3 passed?
        print("Trying selected model gpt-3")
        # try use gpt-3.5-turbo instead of gpt-4 as seems costly to use gpt-4 on OpenAI
        config_list = autogen.config_list_from_json(
            config_list_path,
            filter_dict={
                "model": ["gpt-3.5-turbo"],
            },
        )
    elif len(user_select_preferred_model)>0:
        # NB Depending on model this may be OpenAI or may not be OpenAI
        # E.g. if model is "gemma-3-4b-it" it's not OpenAI - it may be, say, local LM Studio
        # If model is "gemma3:4b" it may be local ollama
        # If it's gpt-4o-mini it is likely OpenAI
        print(f"Trying selected model {user_select_preferred_model}")
        config_list = autogen.config_list_from_json(
            config_list_path,
            filter_dict={
                "model": [user_select_preferred_model],
            },
        )
		# Not 100% mad about this behaviour in that if I were a user and I was running say LM Studio with "model-foo" and I passed it on commandline I would expect it should work without also having to add a specific entry for that to the OAI_CONFIG_LIST .. ? Now it will instead filter to none.
        # Maybe if we end up with 'None' here then try do something 'smarter'
        # And/or if we allow (say) "ollama/modelname" or "lm_studio/modelname" we could try to construct a config?
        # And/or if we add a commandline parameter like "--local" and/or "--url_base" etc.
        if config_list:
            s = json.dumps(config_list)
            show_setting(f'FILTER LIST FROM MODEL user_select_preferred_model={user_select_preferred_model}', s)
        else:
            # If this is say a local ollama and it's present why not just allow it and bypass? it's an extra pain to have to edit OAI_CONFIG dj2026 ..
            print(f"{Fore.RED}FILTER LIST FROM MODEL {user_select_preferred_model}: MODEL NOT FOUND IN CONFIG LIST{Style.RESET_ALL}")
            # And/or fallback to some existing model from the list (the first? first local one?) but try specify model
            # Here just fallback to first in list for now
            config_list = autogen.config_list_from_json(config_list_path)
            if config_list:
                # todo if we add a --verbose or something
                s = json.dumps(config_list)
                show_setting('FALLBACK-CONFIG_LIST', s)# NB show_setting does important stuff like hide sensitive info like keys
            else:
                print(f"{Fore.GREEN}FALLBACK-CONFIG_LIST: NONE{Style.RESET_ALL}")

    else:
        print("do autogen.config_list_from_json - default")
        # Default
        # If no model passed in then just use the first one in the list
        # Otherwise if user has (say) their own better preferred model than gpt-4 e.g. "gpt-4o-mini" then our '"gpt-4"' filter below kills and overrides that.
        config_list = autogen.config_list_from_json(config_list_path)
    have_openai_config = True

    def sanitize_oai_config_list(cfg_list):
        ALLOWED_KEYS = {
            "model",
            "api_key",
            "base_url",
            "temperature",
            "max_tokens",
            "timeout",
            "stream"
        }

        return [
            {k: v for k, v in cfg.items() if k in ALLOWED_KEYS}
            for cfg in cfg_list
        ]

    # dj2025-12 some autogen versions don't like the "api_type" and "tags" and give errors
    # Fix it by pre-sanitizing the list ..
    # but we may have to later re-implement the idea of tags differently ..
    print("--- Sanitize openAI config and resolve env vars such as env:OPENAI_API_KEY")
    original_raw_config = config_list
    clean_config = sanitize_oai_config_list(original_raw_config)
    config_list = clean_config

    def resolve_value(v, strict=True):
        if isinstance(v, str) and v.startswith("env:"):
            name = v[4:]
            val = os.getenv(name)
            if val is None and strict:
                raise RuntimeError(f"Missing env var: {name}")
            return val
        return v
    def resolve_env_vars(obj):
        if isinstance(obj, dict):
            return {k: resolve_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [resolve_env_vars(v) for v in obj]
        else:
            return resolve_value(obj)

    # Resolve environment variable values
    # This allows us to put (say) the following in the config:
    # "api_key": "env:OPENAI_API_KEY",
    # then at runtime it converts that to get key from ENV
    # This allows us to support others also e.g.:
    #"env:OPENAI_API_KEY": "OPENAI_API_KEY",
    #"env:AZURE_OPENAI_KEY": "AZURE_OPENAI_KEY",
    #"env:ANTHROPIC_API_KEY": "ANTHROPIC_API_KEY",
    #"env:GROQ_API_KEY": "GROQ_API_KEY",
    #print("--- Resolve env vars such as env:OPENAI_API_KEY")
    resolved_cfg = resolve_env_vars(clean_config)
    config_list = resolved_cfg
    #clean_cfg = sanitize_oai_config(resolved_cfg)



    #print(f"{Fore.GREEN}'--- {config_list_path}' found. have_openai_config=Y{Style.RESET_ALL}")
    print("--- setting have-AutoGen-config_list")
    #print("OpenAI configuration loaded")
    # todo (low) show details of OpenAI config picked up? eg models and whatever else ... and if have key
    llm_config_coder_openai={
        "config_list":config_list
    }
else:
    # {Hmm .. hould we have something like 'default to local ollama or LM Studio' settings?}
    # If the OAI_CONFIG_LIST file does not exist, print a warning message
    #print(f"{Fore.RED}Warning: '{config_list_path}' file not found{Style.RESET_ALL}")

    # NB this warning only applies to autogen backend now at this stage (dj2026-01)
    if has_autogen() and use_backend=='autogen':
        print("runai[autogen] Warning: No AutoGen OpenAI configuration - this is not critical if using local LLMs")

    #dj-check: should we set have_openai_config to False here? (dj2025-03)
    # should we override config_list ..not 100% sure
    #have_openai_config = False
    # I am not sure if config_list_localgeneral still applies outside of autogen stuff - probalby not especially now we have new model_spec - check later during refactor (dj2026-01)
    print(f"[use-backend:{use_backend}] runai[autogen] selecting config_list_localgeneral")
    config_list = config_list_localgeneral
    #config_list.model = ["deepseek-r1:1.5b"]
    have_openai_config = False
    use_openai = False

if config_list:
    # todo if we add a --verbose or something
    s = json.dumps(config_list)
    show_setting('CONFIG_LIST', s) # NB show_setting does important stuff like hide sensitive info like keys
else:
    print(f"{Fore.RED}CONFIG_LIST: NONE{Style.RESET_ALL}")
    #show_setting("global.config_list", s)
#if wait_for_confirm:
#    input('Press a key')


if just_show_settings:
    show_settings()
    sys.exit(0)

show_settings()

# Get date/time to use in filenames and directories and session logfiles etc.
task_datetime = datetime.datetime.now()
task_formatted_datetime = task_datetime.strftime("%Y%m%d-%H%M%S")

# In quiet mode, do not create any output directories/files.
task_output_directory = ''
if not quiet_file_output:
    task_output_directory = os.path.join(project_name, path_runai_out, task_formatted_datetime) if project_name else os.path.join(path_runai_out, task_formatted_datetime)
    # Create the output directory if it doesn't exist
    if not os.path.exists(task_output_directory):
        #  NB even though we just checked if not exists, in tasks like runai studio's 'run multiple commands at once' (for example) this easily really happens that it exists and has just been created .. and that's ok
        os.makedirs(task_output_directory, exist_ok=True)

#todo fix: .. auto-rename add _2 etc.??
#    from .main import main
#  File "C:\Users\david\pipx\venvs\runai-cli\Lib\site-packages\run_ai\main.py", line 1277, in <module>
#    os.makedirs(task_output_directory)
#  File "<frozen os>", line 225, in makedirs
#FileExistsError: [WinError 183] Cannot create a file when that file already exists: 'lexicographer_out\\output_runai\\2026-01-24 00-56-46'

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
        print(f"{Fore.BLUE}■ {Fore.YELLOW}TaskFile: {taskfile}: {Fore.GREEN}{Style.RESET_ALL}{status}")
        print(f"=== {Fore.YELLOW}Loading TaskFile: {taskfile}{Style.RESET_ALL}")
        with open(taskfile, 'r', encoding='utf-8') as file:
            for line in file:
                task += line.strip() + "\n"  # Appending each line to the task string
        if len(task)==0:
            print(f"{Fore.RED}Warning: TaskFile is empty!{Style.RESET_ALL}")
    else:

        # [dj2025-03] Remember the file name "runai.autotask.txt" is like a special "auto-start" task file that is fully optional
        # So if "taskfile" is not found, if it is on the default special  "auto-start" file, then we just print a message and continue
        status=''
        color='GREEN'
        if os.path.exists(taskfile):
            color = 'GREEN'
            if taskfile=='runai.autotask.txt':
                status='found runai.autotask.txt'
            else:
                # file exists and name is not "autostart.txt" (likely user used "-tf" to specify a taskfile)
                status='found'
        else: # FILE DOES NOT EXIST
            if taskfile=='runai.autotask.txt':
                status='not found (it is optional)'
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
        #print("--------------------------[ NOTES ]----------------------------")
        print(f"Note: {Fore.CYAN}runai.autotask.txt{Style.RESET_ALL} is an optional default task file that auto-loads/starts if no task file specified.")
        print(f"Use {Fore.CYAN}-tf <filename>{Style.RESET_ALL} to specify a different task file.")
        print("---------------------------------------------------------------")


if task=="":
    # Define your coding task, for example:
    # Hm, saying "No task specified" is misleading if the user passed a taskfile and it was empty or not found - from their perspective they did try to specify a task
    #print(f"■ No task specified")
    print(f"■ No task specified")
    #if not force_show_prompt:
        #print("=== Please specify a task in task.txt (or pass filename as 1st parameter) or use -p to prompt for a task or -t for default test/sample task")
        #task = "Write a Python function to sort a list of numbers."
        #print("=== Using default sample task: {task}")

# Check if 'task' is an empty string or None
if task == "" or task is None or force_show_prompt:
    sCWD=os.getcwd()#getcwd just for logging
    print(f"• current-directory={sCWD} • working-folder={worktree}")
    if stdin_text:
        # dj2026-01 if no parameters passed but there is stdin, use it as task - but this may change later ...
        task = stdin_text
    else:
        task = input(f"{Fore.CYAN}(Ctrl+C to stop)({sCWD}) {Fore.YELLOW}What would you like to do? Please enter a task:{Style.RESET_ALL} ")

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
    print(f"DEBUG: PROCESS_FILES {files_to_send} worktree={worktree} targetfolder={targetfolder} {runtask.type} {task}")
    for file_name in files_to_send:
        file_path = os.path.join(worktree, file_name)
        if os.path.exists(file_path):
            print(f"Processing {file_name}...")
            try:
                modified_content = send_to_autogen(file_path, task)

                # Save modified file
                target_path = os.path.join(targetfolder, file_name)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, 'w', encoding='utf-8', errors="replace") as file:
                    file.write(modified_content)
                print(f"Saved modified {file_name} to {targetfolder}")
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")
        else:
            print(f"File not found: {file_name}")

# Main script execution
from colorama import init
init()

dual_output = None
# dj2026-01 new main() for refactoring for a.o. pip install...
def main():
    global dual_output
    global selector, settings, user_select_preferred_model
    # autogen vars .. should move later in refactoring ..
    global assistant, coder, user_proxy, groupchat, manager

    print("--- start-main")
    # CWD is not so much a 'setting' as a 'current state' of runtime environment but we log it here anyway, it may be useful to know
    sCWD=os.getcwd()#getcwd just for logging
    print(f"• current-directory: {sCWD}")
    if files_to_send:
        for file_name in files_to_send:
            print(f"SETTINGS:File={file_name}...")
    print(f"SETTINGS: Task={task}")
    print(f"[autogen-USE_OPENAI]={use_openai}")

    # dj2025-03 adding backend selector
    print(f"USE_BACKEND={use_backend}")
    #settings = djAISettings()
    if len(user_select_preferred_model)>0:
        settings.model = user_select_preferred_model
        # Kind of JIT-style do it again in case it (model) changed right here before we actually need it
        model_spec = do_select_model(user_select_preferred_model)
    settings.model_spec = model_spec
    # hmm todo/fixme where does echo_mode belong?
    settings.echo_mode = echo_mode

    # Attachments: load and store in settings for backends
    settings.attachments = _load_attachments(attach_files)
    if settings.attachments:
        print(f"{Fore.YELLOW}Attachments loaded: {len(settings.attachments)}{Style.RESET_ALL}")
        for a in settings.attachments:
            print(f"  - {a.get('filename')} ({a.get('mime_type')}) kind={a.get('kind')}")

    print('=== BackendSelector setup')
    #print(f"SELECT MODEL {settings.model} {settings.model_spec}")
    show_setting(f"[run] {Fore.YELLOW}MODEL{Fore.GREEN} '{settings.model}' spec", settings.model_spec);

    #show_setting()

    # Create backend selector
    selector = BackendSelector(settings, use_backend)

    # RUN BACKEND TEST:
    global run_tests
    if run_tests:
        #input(f"Press a key to run tests")
        #task = 'Say Hi 3 times'
        #task = "Write a Python function to sort a list of numbers."

        print('=== TEST:')
        result = selector.do_task('Say hi 3 times')

        backend = selector.get_backend()
        #print(f"=== BackendSelector TEST: {result}")
        if len(backend.error)>0:
            print(f"=== test DoTask[backend:{selector.backend_name}]: {Fore.RED}ERROR: {backend.error}. RESPONSE:{Style.RESET_ALL}")
            print(f"{Fore.RED}{backend.response}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{result}{Style.RESET_ALL}")
        else:
            print(f"=== test DoTask[backend:{selector.backend_name}]: {Fore.GREEN}SUCCESS:{Style.RESET_ALL}")
            print(f"{Fore.RED}{result}{Style.RESET_ALL}")
        print(f"RESULT (TEST): {result}")
        print("---------------------------------------")
        print('=== BackendSelector TEST:')
        testtask = "Write a Python function to sort a list of numbers."
        result = selector.do_task(testtask)

        backend = selector.get_backend()
        #print(f"=== BackendSelector TEST: {result}")
        if len(backend.error)>0:
            print(f"=== test DoTask[backend:{selector.backend_name}]: {Fore.RED}ERROR: {backend.error}. RESPONSE:{Style.RESET_ALL}")
            print(f"{Fore.RED}{backend.response}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{result}{Style.RESET_ALL}")
        else:
            print(f"=== test DoTask[backend:{selector.backend_name}]: {Fore.GREEN}SUCCESS:{Style.RESET_ALL}")
            print(f"{Fore.RED}{result}{Style.RESET_ALL}")
        print(f"RESULT (TEST): {result}")
        print("---------------------------------------")

    # Log the task to keep a record of what we're doing and help study/analyze results
    if not quiet_file_output and task_output_directory:
        log_task = f"{task_output_directory}/tasklog.txt"
        with open(log_task, 'a', encoding='utf-8', errors="replace") as log_file:
            log_file.write(task)

    ###############################################
    # NB! Be careful here, from below any output is auto-captured and redirected for things like auto-codeblock extraction to save to files
    # Redirect output to both console and StringIO
    #if not quiet_file_output and task_output_directory:
    dual_output = DualOutput(task_output_directory)
    sys.stdout = dual_output
    #else:
    #    dual_output = None

    # The stuff below is not part of the actual captured AI output but is part of the main program output
    # but it's getting added to it ... hmmm
    # We may need to separate these output streams better ... distinguish what should be 'logged' in output folder for user, what should be visible but not captured

    # todo add option whether to wait on keypress or auto go-ahead
    print(f"DEBUG: selector.get_active_backends: {selector.get_active_backends()}")
    ##input(f"■ Press a key to run task: {Fore.CYAN}{task}{Style.RESET_ALL}")

    #print("---------------------------------------")
    if using_autogen():
        llm_config_general={
            "config_list":config_list, "cache_seed": autogen_settings.use_cache_seed, "stream": False
        }
        llm_config_coder={
            "config_list":config_list, "cache_seed": autogen_settings.use_cache_seed, "stream": False
        }

    # NB hide keys! Also this should be before general output capture probably? It's like settings info
    #print(f"=== {Fore.CYAN}llm_config_general: {llm_config_general}{Style.RESET_ALL}")
    #print(f"=== {Fore.CYAN}llm_config_coder: {llm_config_coder}{Style.RESET_ALL}")
    # show_setting does important stuff like hide sk-* keys for privacy
    #dual_output.PauseSaveFiles()
    if using_autogen():
        show_setting("■ autogen:llm_config_general", llm_config_general)
        show_setting("■ autogen:llm_config_coder  ", llm_config_coder)
    #dual_output.UnpauseSaveFiles()
    # this is incorrectly going into our captured output log file ...

    #djAutoGenDoTask(task)
    #elif len(backend.response)==0:
    #    # this will still happen with autogen as our autogen backend is a stub... (dj2025-03)
    #    print(f"empty response")
    print("---------------------------------------")
    # dj2025-04:

    #input('Press a key ....')

    if has_autogen() and using_autogen():
        # create an AssistantAgent named "assistant"
        assistant = autogen.AssistantAgent(
            name="assistant",
            llm_config={
                #"use_system_message": False,  # <-- critical: disables system role
                "cache_seed": autogen_settings.use_cache_seed,  # seed for caching and reproducibility
                #"config_list": config_list,  # a list of OpenAI API configurations
                # above line for OPENAI and this below line for our LOCAL LITE LLM:
                "config_list": config_list,#_localgeneral,  # a list of OpenAI API configurations
                "temperature": 0,  # temperature for sampling
            },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
        )
        # Below had to do with LM studio compatibility niggledies [dj2025-03/04]
        assistant.use_system_message = False
        assistant.llm_config["stream"] = False
        # Create a coder agent
        coder = autogen.AssistantAgent(
            name="coder",
            llm_config=llm_config_coder#llm_config_coder_openai if use_openai else llm_config_localcoder
        )
        # create a UserProxyAgent instance named "user_proxy"
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            ########### ollama-testing:
            # [dj2025-04] working on ollama/LiteLLM compatibility issues but double-check if below line causes issues with OpenAI API
            llm_config=llm_config_general,
            #llm_config=llm_config_localgeneral if use_openai else llm_config_localgeneral,
            #code_execution_config=code_execution_enabled,
            max_consecutive_auto_reply=autogen_settings.max_consecutive_auto_replies,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            #code_execution_config=code_execution_enabled,
            code_execution_config=False,
            #code_execution_config={
            #    "work_dir": "__coding__",
            #    "use_docker": False,  # set to True or image name like "python:3" to use docker
            #},
        )

        """
        if autogen_settings.coder_only:
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

        if not autogen_settings.NoGroup:
            print("=== Creating groupchat and manager")
            groupchat = autogen.GroupChat(agents=[user_proxy, coder, assistant], messages=[])
            manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config_localgeneral)
        else:
            print("=== no groupchat or manager")
            groupchat = None
            manager = None

    # Check if we have a input.txt file and if so use that as input to the AI to run on all lines of the file
    inputlines_array = []

    # STDIN PIPED?
    if stdin_text is not None and len(stdin_text)>0:
        # encode STDIN as a triple-backtick codeblock e.g.
        # $ cat main.cpp | runai -t "Review for errors"
        # task:
        # Review for errors
        # ``
        # contents of main.cpp
        # ```
        # Add contents of STDIN as "attachment" to task
        # Naming:
        #stdin_mode = "attachment"
        #stdin_mode = "taskfile"
        #stdin_mode = "task"
        #Once named, bugs disappear.
        stdin_mode = "attachment"
        if len(task)>0 and stdin_mode=="attachment":
            newline_char='\n'
            task_message = task + newline_char + "```" + newline_char + stdin_text + "```"
            print("runai:DEBUG:STD ATTACHMENT MODE")
            djAutoGenDoTask(task_message)
        elif len(inputfile)==0:
            # If NO input file specified but we have a task treat it rather like 'inputfile' though we may still need to split it ...
            inputlines_array.append(stdin_text)
    elif os.path.exists(inputfile):
        print(f"=== Using inputfile: {inputfile}")
        #input = ""
        with open(inputfile, 'r', encoding='utf-8', errors="replace") as file:
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
            # BATCH MODE SUBSTITUTIONS:
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
            #pause_capture in case our own task has code blocks in it - we don't want it auto-saving by mistake
            if runtask.start_line > 0:
                # Skip lines until we reach start_line
                if line_number < runtask.start_line:
                    #print(f"=== Skipping line {line_number} as it's before start_line {runtask.start_line}")
                    continue

            # Log requested task but pause the savefiles thing otherwise it will auto grab our own codeblacks out the task
            if dual_output is not None:
                dual_output.PauseSaveFiles()
            print(f"=== Processing task: {task_line}")
            if dual_output is not None:
                dual_output.UnpauseSaveFiles()


            if runtask.dryrun:
                continue


            # Add some logging so user can see where we left off quickly if we need to restart
            if not quiet_file_output:
                log_task = f"_inputlines_tasklog_runinfo.log"
                with open(log_task, 'a', encoding='utf-8', errors="replace") as log_file:
                    # Get date/time to use in filenames and directories and session logfiles etc.
                    log_datetime = datetime.datetime.now()
                    log_formatted_datetime = log_datetime.strftime("%Y-%m-%d %H-%M-%S")

                    log_file.write(f"=== EXECUTING LINE {line_number}/{len(inputlines_array)} [start-line:{runtask.start_line}][{log_formatted_datetime}]: {inputline}\n")
                    """
                    log_file.write(f"=== EXECUTING LINE {line_number}/{len(inputlines_array)} [start-line:{runtask.start_line}]: {inputline}\n")
                    """

            print("--- 1")
            djAutoGenDoTask(task_line)
            # Optional delay between each line (in milliseconds)? (e.g. to not hammer server)
            if runtask.delay_between:
                print(f"=== Sleeping {runtask.delay_between}s between tasks")
                time.sleep(runtask.delay_between)
    elif runtask.type==djTaskType.modify:
        print("=== Do task type: {runtask.type}")

        # [dj2025] THIS APPLIES NOW TO "EDIT":
        if len(runtask.settings_modify.send_files)>0:
            for filename in runtask.settings_modify.send_files:
                print(f"=== MODIFY: PROCESSING FILE: {filename}")
                # Read all lines from the file
                #with open(file, 'r', encoding='utf-8') as file:
                with open(filename, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                # Read a line a time
                str_loaded_file_content = ""
                for line in lines:
                    str_loaded_file_content += line# + "\n"
                    print(line)
                    #loaded_file_content = file.read()
                print(f"=== Loaded file content:\n```\n{str_loaded_file_content}\n```")
                input(" Please press a key to continue. loaded_file_content")

                # todo low) "cpp" hardcoded as code type here for now
                newline_char = "\n"

                #str_loaded_file_content = f"{loaded_file_content}"
                #print(f"=== Loaded file content: {loaded_file_content}")
                print(f"task:{task}")
                task_message = task + newline_char + f"```{filename}" + newline_char + str_loaded_file_content + "```"
                print(f"task_message:{task_message}")

                # DEBUG/TESTING and maybe actual use: Save the task_message to file
                # but if filename exists generate new filename
                #task_message_filename = f"{file}.task"
                if not quiet_file_output:
                    str_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    task_message_filename = f"{filename}__{str_datetime}-task.txt"
                    while os.path.exists(task_message_filename):
                        str_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        task_message_filename = f"{filename}__{str_datetime}-task.txt"
                    with open(task_message_filename, 'w', encoding='utf-8', errors="replace") as file:
                        file.write(task_message)

                # wait for keypress
                input('Please press a key to continue.')
                # (1) First let the AI do its thing
                # (2) Then get the AI output which gets captured in the DualOutput class
                # We want to use the final AI output co ..
                print("--- 2")
                djAutoGenDoTask(task_message)
                #user_proxy.initiate_chat(coder, message=task_message)
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
        if dual_output is not None:
            dual_output.PauseSaveFiles()
        if len(files_to_create)==1:
            task_message = f"Create the following file and return in a ```...``` code block with filename: {', '.join(files_to_create)} with the following specifications: {task}"
        else:
            task_message = f"Create the following files and return in ```...``` code blocks with filenames: {', '.join(files_to_create)} with the following specifications: {task}"
        if dual_output is not None:
            dual_output.UnpauseSaveFiles()
        #user_proxy.initiate_chat(assistant, message=create_task_message)
        print("--- 3")
        djAutoGenDoTask(task_message, True)
    elif files_to_send and len(files_to_send)>=1:
        # If no files to create, do requested task
        if dual_output is not None:
            dual_output.PauseSaveFiles()
        if len(files_to_send)==1:
            print(f"=== Sending file [{runtask.type}]: {', '.join(files_to_send)}")
        else:
            print(f"=== Sending files [{runtask.type}]: {', '.join(files_to_send)}")
        if dual_output is not None:
            dual_output.UnpauseSaveFiles()
        # Call the function to process files
        # This is maybe not going to be used anymore, not sure..
        # wait for keypress
        #input('process_files')
        process_files(files_to_send, worktree, targetfolder, task)
    else:
        # If no files to create, do requested task
        #pause_capture in case our own task has code blocks in it - we don't want those auto-saving by mistake
        if dual_output is not None:
            dual_output.PauseSaveFiles()
        print(f"=== Processing task [type={runtask.type}]: {task}")
        if dual_output is not None:
            dual_output.UnpauseSaveFiles()
        task_message=task
        print("--- final-else")

        # Start adding exception catching for elegant recovery and better user experience
        # e.g.: Anthropic error: {"type":"error","error":{"type":"invalid_request_error","message":"Your credit balance is too low to access the Anthropic API"
        #task_success = False
        try:
            djAutoGenDoTask(task_message)
            #task_success = True
        except Exception as e:
            #task_success = False
            log.error("Backend DO-TASK failed", exc_info=settings_runai.debug)
            print(f"{Fore.RED}ERROR{Fore.YELLOW}:runai[Backend DO-TASK]:{str(e)}{Style.RESET_ALL}")
            # we want the traceback to help debug if debug mode, but normal users it should just display a message but continue operating ... not a crash-y-like traceback
            if settings_runai.is_debug():
                import traceback
                traceback.print_exc()
                raise   # preserves original traceback



    # Reset stdout to original and get captured output
    if dual_output is not None:
        sys.stdout = dual_output.console
        ai_output = dual_output.getvalue()
    else:
        sys.stdout = sys.stderr
        ai_output = ''

    # Get the current date and time
    formatted_datetime = task_datetime.strftime("%Y-%m-%d %H-%M-%S")

    if not quiet_file_output and ai_output:
        # Create the log filename
        # Not quite sure if this should also be in task_output_directory or not
        log_filename_base = f"dj_AI_log.txt"
        # Write the AI output to the log file
        with open(log_filename_base, 'a', encoding='utf-8', errors="replace") as log_file:
            log_file.write(f"[{formatted_datetime}] Captured AI Output:\n")
            log_file.write(ai_output)
            log_file.write("----------------------\n")

        # Create the log filename
        log_filename1 = f"{task_output_directory}/dj_AI_log.txt"
        # Write the AI output to the log file
        with open(log_filename1, 'a', encoding='utf-8', errors="replace") as log_file:
            log_file.write(f"[{formatted_datetime}] Captured AI Output:\n")
            log_file.write(ai_output)
            log_file.write("----------------------\n")

    # We're effectively doing below twice now ..
    # Use ai_output with create_files_from_ai_output function in order to actually create any files in the returned code

    if not quiet_file_output and dual_output is not None and dual_output.get_captured() is not None:
        print("runai: Creating files from AI output task_output_directory {task_output_directory}/outfiles")
        files_created = create_files_from_ai_output(ai_output, task_output_directory + '/outfiles')
    else:
        files_created = None

    # Print the captured output to the console
    #ai_output_actual = dual_output.
    if dual_output is not None and dual_output.get_captured() is not None:
        capture_output_actual = dual_output.get_captured()
        #print(f"runai: Captured AI Output:{len(dual_output.get_captured())}")
        print('____________________ AI OUTPUT ______________________________')
        #print(ai_output)
        for line in capture_output_actual:
            #print("[" + line + "]" + f"{len(line)}")
            print(line)#+ f"{len(line)}")
        print('____________________ END OF AI OUTPUT _______________________')
    else:
        # eg failure
        print(f"{Fore.YELLOW}No result{Style.RESET_ALL}")



    # dj2025-03 list files created and list files first required (e.g. "runai create -o file1.cpp file2.h") so we can see if all files were created
    if runtask.type == djTaskType.create:
        print("🤖create files requested:")
        if not runtask.settings.out_files is None:
            for file in runtask.settings.out_files:
                print(f"  '{file}'")

        print("🤖 files to create:")
        if not files_to_create is None:
            for file in files_to_create:
                print(f"  {file}")
        #files_created = create_files_from_ai_output
        print("🤖💾files created by final create_files_from_ai_output:")
        if not files_created is None:
            for file in files_created:
                print(f"  {file}")


    #result = send_files_for_modification(args.task_description, args.header_file, args.source_file)
    #print(f'Modified files received: {result}')
    # Get date/time to use in filenames and directories and session logfiles etc.
    controller.AppDone()
    #app = controller.apps
    #datetime_completed = controller.datetime_end#djGetFormattedDatetime(datetime.datetime.now())
    print(f"🤖=== Done! All tasks processed. Completed {controller.session_stats.datetime_end}")
    #print(f"{Fore.YELLOW}_______________________________\nFinal Session Stats & Info:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Final Session Stats & Info:{Style.RESET_ALL}")
    #HEADING: Session Stats
    #show_setting(f"{Fore.YELLOW}Session Stats{Style.RESET_ALL}", '', 1)
    print(f"   {Fore.YELLOW}Session: {Fore.WHITE}started: {Fore.BLUE}{controller.session_stats.datetime_start}{Style.RESET_ALL}")
    print(f"   {Fore.YELLOW}         {Fore.WHITE}completed: {Fore.BLUE}{controller.session_stats.datetime_end}{Style.RESET_ALL}")
    print(f"   {Fore.YELLOW}         {Fore.WHITE}time: {Fore.BLUE}{controller.session_stats.elapsed_time}{Style.RESET_ALL}")
    #show_setting('total tasks', controller.session_stats.total_tasks, 1)
    show_setting('task_output_folder', task_output_directory, strEnd=' ')
    show_setting('outfiles', (task_output_directory+'/outfiles') if task_output_directory else '', 1)
    #HEADING: Task info
    show_setting(f"{Fore.YELLOW}Task settings{Style.RESET_ALL}", "", strEnd=' ')
    show_setting("runtask.type", runtask.type, strEnd=' ')
    show_setting("files_to_create", files_to_create, strEnd=' ')
    show_setting("files_to_send", files_to_send, strEnd=' ')

    #HEADING: File-related info
    #show_setting(f"{Fore.YELLOW}File-related info{Style.RESET_ALL}", '', 1)
    show_setting("out_files", runtask.settings.out_files, strEnd=' ')
    show_setting("send_files", runtask.settings.send_files)
    #show_setting("files_created", files_created, 2)

    # Show MODEL SPEC and backend used:
    show_setting('backend',use_backend,strEnd='')
    if settings.model_spec:
        #KEY_COLOR   = "\033[36m"  # cyan
        #VALUE_COLOR = "\033[33m"  # yellow
        #RESET       = "\033[0m"
        for key, value in settings.model_spec.items():
            # this is confusing 'key, value' is standard map terminology yes but "key" below is entirely different
            # it means if this is a value like "api_key" hide it as it's sensitive!
            if "key" in key.lower() and value:
                value = '*'
            show_setting(f"{key}", value, strEnd='')
        print("")
    print(f"🤖 - {Fore.MAGENTA}\"Done! What else can I help you with next?\"{Style.RESET_ALL}")
    # Debug / verbose / progress → stderr
    #print("Using backend: ollama", file=sys.stderr)
    #print("Tokens used: 1234", file=sys.stderr)
    #sys.stdout.flush()
    #print("out", file=sys.stdout)
    #sys.stdout.flush()



if __name__ == '__main__':
    main()
