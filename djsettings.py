# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2023-2026 - Business Source License (BSL 1.1). See LICENSE

#import djtasktypes

"""
Thinking out loud:

(1) There's a global runtask, it is an instance of "djTask" class - meaning stuff having to do with TASKS:
    runtask = djTask()
(2) In turn in djTask() constructors:
    runtask.settings = new djsettings.djSettings()
    (2b) Also these settings seem to be set up in a very limited way, which is good e.g. only "runtask.settings.send_files = args.send"
(3) In turn, djSettings itself actually currently only has two TASK-related settings, AND these are attached to "runtask" djTask.
    So, "class djSettings" could maybe be renamed to something like djTaskSettings, or djTaskFileSettings, or djTaskFileTransferSettings, etc.
    As I want to try separate groups of settings that maybe belong in different places? low.
    Here I am thinking of things like, say, "preferred model" for LLM tasks, etc. And/or AutoGen settings.

class djSettings:
    def __init__(self):
        # e.g. runtask.settings.send_files
        # task settings
        # (1) runtask = djTask()
        # *2( runtask.settings = djSettings()
        runtask.settings.send_files
        self.out_files = []
        self.send_files = []
"""
class ModifyTaskSettings:
    def __init__(self):
        self.send_files = []
        self.out_files = []


# See DESIGN-NOTES.md (dj2026-01) on "SETTINGS" ... below is quite fluid still not set in stone but a WIP ..

class djSettings:
    def __init__(self):

        # BACKEND RELATED:

        # system or runai instance related

        # See DESIGN-NOTES.md in-progress thoughts on below: dj2026-01
        #self.user_select_preferred_model = ''
        #self.model = ''
        self.backend = ''

        # TASK-RELATED:

        # User-required output files
        # E.g. "runai --o1-mini -t "Please create a full C++ vec3d helper class, and return it in codeblocks with file names vec3d.h and vec3d.cpp." create -o vec3d.h vec3d.cpp"
        # then this should be ["vec3d.h", "vec3d.cpp"]
        self.out_files = []
        self.send_files = []
        # still in-dev:
        self.exec = None

"""
todo and flesh out, something like below for LLMsettings, say, and more:
# ~dj2025 user settings are preferences such as 'preferred model' selected from command line
class djUserSettings:
    def __init__(self):
        self.user_select_preferred_model = ''

class djUserLLMSettings:
    def __init__(self):
        #  'gpt-3', 'gpt-4', 'o1-mini', 'o1-preview' and many more
        self.preferred_model = None
"""
