# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2023-2025 - Business Source License (BSL 1.1). See LICENSE
#
# runai base Backend class
# dj2025-03

class djAISettings:
    def __init__(self, model: str=''):#, temperature: float, max_tokens: int):
        #self.model = 'openai/gpt-4o-mini'#model
        self.model = 'gpt-4o-mini'#model
        #self.temperature = temperature
        #self.max_tokens = max_tokens

"""
class url_settings:
    def __init__(self, url: str, headers: dict = None):
        self.url = url
        self.headers = headers if headers is not None else {}
"""

"""
class server_settings:
    def __init__(self, host: str, port: int, ssl: bool = False, ssl_cert: str = None, ssl_key: str = None):
        self.ssl = ssl
        self.host = host
        self.port = port
"""

# run_ai/backends/base.py
class Backend:
    def __init__(self, ai_settings: djAISettings):
        self.ai_settings = ai_settings
        if not self.ai_settings is None:
            print(f"backend:ai_settings: initialized with model: {self.ai_settings.model}")
            print("backend:ai_settings:", self.ai_settings.__dict__)
        else:
            raise ValueError("AISettings cannot be None")
        # last error from backend
        self.error = ''
        # last response from backend
        self.response = ''

    def create(self):
        # Initialize the backend
        #raise NotImplementedError("Backends must implement create()")
        return True

    # hmm naming - this could just be 'chat' not necessarily 'task' per se.
    def do_task(self, task: str) -> str:
        raise NotImplementedError("Backends must implement do_task()")
