
from run_ai.backends.base import Backend
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
    def __init__(self, settings):
        super().__init__(settings)
        self.settings = settings
        print("INIT: Creating AutoGenBackend")

    #def create()

    def do_task(self, task: str) -> str:
        # This is where you would implement the logic to perform the task using the djChat backend
        # For now, we'll just return a placeholder response
        return f"[autogen]do_task: Task '{task}' AUTOGEN TO IMPLEMENT"
