# runai OpenAI Backend class
# dj2025-03

from run_ai.backends.base import Backend
import openai

class OpenAIBackend(Backend):
    def __init__(self, settings):
        super().__init__(settings)

    def do_task(self, task: str) -> str:
        # Implement the logic to interact with OpenAI API
        response = openai.ChatCompletion.create(
            model=self.settings.model,
            messages=[{"role": "user", "content": task}]
        )
        return response.choices[0].message['content']
