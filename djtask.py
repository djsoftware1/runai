# Copyright (C) David Joffe / DJ Software 2023-2025

from djtasktypes import djTaskTypes
import djsettings

class djTask:
    def __init__(self):
        self.type = djTaskTypes.chat
        # more groups of 'task settings'? autogen settings?
        self.settings = djsettings.djSettings()
        ##user_select_preferred_model? LLMsettings?
        self.delay_between = 0
        self.dryrun = False
        # Optional 1-based 'start at line' for multi-line task files
        self.start_line = 0
