# Copyright (C) David Joffe 2023-2024

from djtasktypes import djTaskTypes
import djsettings

class djTask:
    def __init__(self):
        self.type = djTaskTypes.chat
        self.settings = djsettings.djSettings()
        self.delay_between = 0
        self.dryrun = False
        # Optional 1-based 'start at line' for multi-line task files
        self.start_line = 0
