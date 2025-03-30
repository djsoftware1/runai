# runai base Backend class
# dj2025-03

# run_ai/backends/base.py
class Backend:
    def __init__(self, settings):
        self.settings = settings
        # last error from backend
        self.error = ''
        # last response from backend
        self.response = ''

    # hmm naming - this could just be 'chat' not necessarily 'task' per se.
    def do_task(self, task: str) -> str:
        raise NotImplementedError("Backends must implement do_task()")
