
# runai backend selector
# Allocate/instantiate backend(s) like a factory
# dj2025-03

# todo settings is unimimplemented

#from run_ai.config.back import LLMSettings
from run_ai.backends.base import Backend
from run_ai.backends.base import djAISettings
from run_ai.backends.djchat import djChatBackend
from run_ai.backends.autogen import AutoGenBackend
from run_ai.backends.openai import OpenAIBackend
# future?
# from run_ai.backends.ollama import OllamaBackend


class BackendSelector:
    #LLMSettings
    #def __init__(self, settings: None, backend_name: str = "openai"):
    def __init__(self, ai_settings: djAISettings, backend_name: str = "autogen"):
        self.ai_settings = ai_settings
        self.backend_name = backend_name.lower()
        self.backends = self._initialize_backends()
        for backend in self.backends:
            backend.create()

    def _initialize_backends(self):
        if self.backend_name=='autogen':
            # Initialize AutoGenBackend with settings
            return [AutoGenBackend(self.ai_settings)]
        elif self.backend_name == "djchat":
            # Initialize djChatBackend with settings
            return [djChatBackend(self.ai_settings)]
        elif self.backend_name == "openai":
            # Initialize OpenAIBackend with settings
            return [OpenAIBackend(self.ai_settings)]
        # elif self.backend_name == "ollama":
        #if self.backend_name == "openai":
        #    return [OpenAIBackend(self.settings)]
        # elif self.backend_name == "ollama":
        #     return [OllamaBackend(self.settings)]
        # elif self.backend_name == "multi":
        #     return [OpenAIBackend(self.settings), OllamaBackend(self.settings)]
        else:
            raise ValueError(f"Unknown backend: {self.backend_name}")

    def do_task(self, task: str) -> str:
        # For now, just use the first backend
        return self.backends[0].do_task(task)
    
    def get_backend(self):
        return self.backends[0]

    def get_active_backends(self):
        return [b.__class__.__name__ for b in self.backends]