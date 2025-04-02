# runai OpenAI Backend class
# dj2025-03

from run_ai.backends.base import Backend
#import openai
from colorama import Fore, Style

from openai import OpenAI

class OpenAIBackend(Backend):
    def __init__(self, ai_settings):
        super().__init__(ai_settings)
        if len(self.ai_settings.model) == 0:
            self.ai_settings.model = 'gpt-4o-mini'
            print(f"OpenAI model not set, using default: {self.ai_settings.model}")
        self.client = OpenAI()

    def do_task(self, task: str) -> str:
        # Implement the logic to interact with OpenAI API
        model = self.ai_settings.model
        if len(self.ai_settings.model) == 0:
            self.ai_settings.model = 'gpt-4o-mini'
            print(f"do_task: OpenAI model not set, using default: {self.ai_settings.model}")
        print(f"OpenAI model {self.ai_settings.model} task: {task}")
        # Call the OpenAI API with the task
        response = self.client.responses.create(
            model=model,#"gpt-4o",#todo model
            input=task
        )
        self.response = response.output_text
        print(f"{Style.DIM}OpenAI response: {response}{Style.RESET_ALL}")
        print(response.output_text)
        return response.output_text
