# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2023-2025 - Business Source License (BSL 1.1). See LICENSE
#
# AutoGen backend
# AutoGen itself can use different mix of eg OpenAI and/or local LLMs like ollama.
# This is not to be confused with the actual 'OpenAI backend' which does direct OpenAI with no AutoGen.
#dj2025-03

from run_ai.backends.base import Backend
from run_ai.djautogen.settings import djAutoGenSettings

from run_ai.backends.autogendetect import has_autogen
if has_autogen():
    import autogen
    from run_ai.djautogen.djautogen import djAutoGen


"""
# todo refactor better .. refactoring-in-progress:
# shouldn't be globals etc.
coder_only = None
user_proxy = None
autogen_coder = None
assistant = None
manager = None
no_autogen_user_proxy=True
"""

from run_ai.config.settings import *

class AutoGenBackend(Backend):
    def __init__(self, ai_settings, settings: djAutoGenSettings = autogen_settings):#, **kwargs):
        super().__init__(ai_settings)
        self.autogen_settings = settings#run_ai.config.settings.autogen_settings
        self.djautogen = None
        #print("INIT: Creating AutoGenBackend")
        print("AutoGen-backend initialize with settings:", self.autogen_settings.__dict__)

    def create(self):
        # Initialize the AutoGen backend
        self.djautogen = djAutoGen(self.autogen_settings)
        self.djautogen.InitAutoGen()
        #self.djautogen.start()

    #def create()

    def do_task(self, task: str) -> str:
        # This is where you would implement the logic to perform the task using the djChat backend
        # For now, we'll just return a placeholder response
        return f"[autogen]do_task: Task '{task}' AUTOGEN TO IMPLEMENT"
