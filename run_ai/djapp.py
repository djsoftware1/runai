# Copyright (C) David Joffe (and DJ Software) 2023-2025
# APP SETTINGS (AND RELATED):

# only for djappout
import datetime

# [ROUGH DJ DESIGN THOUGHTS]--------------------
# Create for our applications settings (and whatever else we may need in future).
# Should this be called 'runai'? or should we have a module for this? thinking out loud (dj2025-03):
# DESIGN THOUGHTS:
# (some 'quick off-the-cuff, thinking-out-loud' design thoughts - dj2025-03)
# Imagine this whole 'system' becomes in future a module that other Python apps could use .. then I/we would have some
# situation where I/they would be, say, importing it, then using it like either "app.print()" or "runai.print" or,
# maybe, "runai.app.print" (or "dj-autotask.print", or whatever, if we change the name from "runai").
# In that case, other app functionality may then sit in different submodules within that, perhaps.
# E.g. we might have something like "djautotask". In that case, this would be "djautotask.app" (and one
# would call, say, djautotask.app.print or "djautotask.appsettings" etc.
# Other functionality (e.g. the actual "engine") then might be in other modules like "djautotask.taskmanager.run_task" etc.
# E.g. top-level:
# djautotask.taskmanager.run_task
# djautotask.appsettings
# djautotask.print_error (or djautotask.app.print_error, or djautotask.dj_app_output_helperclass.print_error, or djautotask.dj_app_output_helperclass.print)
# djautotask.settings
# djautotask.LLM_settings
# djautotask.user_settings (and maybe djautotask.autogen_settings, or perhaps djautotask.dj_autogen_wrapper.autogen_usersettings) etc.
# djautoask.dj_autogen_wrapper.autogen_send_file
# djautotask.djrefactor.refactor_code
# djautotask.djrunbuild.build_code
# djautotask.djrunbuild.run_tests
# etc.


class AppSettings:
    def __init__(self, appname):
        self.appname = appname
        self.appname = "runai"

class App:
    def __init__(self, appname):
        #self.appname = appname  # "runai"
        self.appname = "runai"
        self.settings = AppSettings(self.appname)
        #self.out = AppOut(self.appname)
        #self.out.print(f"App {self.appname} initialized.")
        print(f"App {self.appname} initialized.")

"""
class AppOut:
    def __init__(self, appname):
        self.appname = appname
        #self.appname = "runai"

        # Naming conventions: If it's uppercase it's more of a "constant", lowercase a variable that could maybe in future be configurable in various ways (for example, user command line parameter, or config file, etc. - but for now keep it simple.)
        # Or maybe in future it could all just be configurable? not sure (low prio - to think about .. dj2025)
        #self.console_prefix = "runai"
        # The basic idea here in my mind is just I want some common (short but recognizable and distinct) prefix for application generated output so users can quickly see and recognize running output from this application
        # The idea here is a 'common output prefix' to easily recognize output from this application. But 'common_output_prefix' is a long name, so trying something shorter.
        # We also don't want this everywhere - just key places to help draw user attention to 'key' output they are interested in.
        self.common_output_prefix="■"
        self.OUTPUT_PREFIX = "■"

        self.BULLET = "■"
        self.BULLET_INFO = "→"
        self.BULLET_WARNING = "⚠"
        self.BULLET_ERROR = "⛔"
        #self.BULLET_SUCCESS = "✔"
        #self.BULLET_FAILURE = "✘"

    # Small simple wrapper for app output that wraps print but serves a couple of purposes:
    # (1) automatically do things like add common output prefixes (and/or disable or change this behaviour centrally in future if needed)
    # (2) could potentially in future help do things like, say, add a specific log file of this output, or even suppress or redirect this output to something else if needed
    # Commenting this for now as don't need. Or maybe it is worthwhile.
    def print_user_output(self, message):
        print(f"{self.OUTPUT_PREFIX}{message}")

    # "print" is convenient synonym for user output (wrapper for print_user_output)
    def print(self, message):
        self.print_user_output(message)

    def print_error(self, message):
        print(f"{self.OUTPUT_PREFIX}{self.BULLET_ERROR}{message}")
        # Log errors as extra output for users to see, to an error log file. Log also date/time.
        filename = f"{self.appname}_error_log.txt"
        str_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        str_message = f"{str_datetime} {message}"
        # Append log message to file
        with open(filename, 'a', encoding='utf-8') as error_log:
            error_log.write(str_message + '\n')

    def print_warning(self, message):
        print(f"{self.OUTPUT_PREFIX}{self.BULLET_WARNING}WARNING:{message}")
"""
