# Copyright (C) David Joffe 2023-2024

from djtasktypes import djTaskTypes
import djsettings

class djTask:
    def __init__(self):

        self.type = djTaskTypes.chat
        self.settings = djsettings.djSettings()
