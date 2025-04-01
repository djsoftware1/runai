# runai OpenAI Backend class
# dj2025-03

from run_ai.backends.base import Backend
#import openai
from openai import OpenAI

class OpenAIBackend(Backend):
    def __init__(self, settings):
        super().__init__(settings)
        self.client = OpenAI()

    def do_task(self, task: str) -> str:
        # Implement the logic to interact with OpenAI API

        print(f"OpenAI task: {task}")
        # Call the OpenAI API with the task
        response = self.client.responses.create(
            model="gpt-4o",#todo model
            input=task
        )
        self.response = response.output_text
        print(f"OpenAI response: {response}")
        print(response.output_text)
        return response.output_text
