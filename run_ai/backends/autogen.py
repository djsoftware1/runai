#dj2025-03

from run_ai.backends.base import Backend
from run_ai.djautogen.settings import djAutoGenSettings
from run_ai.djautogen.djautogen import djAutoGen
import autogen

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

class AutoGenBackend(Backend):
    def __init__(self, ai_settings, autogen_settings: djAutoGenSettings = None):
        super().__init__(ai_settings)
        self.autogen_settings = autogen_settings
        self.djautogen = None
        print("INIT: Creating AutoGenBackend")

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
