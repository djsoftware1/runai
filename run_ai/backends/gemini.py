# runai Gemini Backend class
#
# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2025-2026 - Business Source License (BSL 1.1). See LICENSE
#
# run_ai/backends/gemini.py
# dj2026-01


# dj2026-01 Although Gemini is 'OpenAI-compatible' it works a bit differently and uses this specific URL currently ..
# so we create a GeminiBackend even though it itself uses the OpenAIBackend

from run_ai.backends.base import Backend
from colorama import Fore, Style
from openai import OpenAI
import os

# I'm not 100% sure if it's better to derive from our openai backend or just have a new clean backend that uses the openAI api directly here but differently ..
# I think the latter is cleaner and less likely to lead to unexpected side effects, though may be a bit more work to implement additional things it's probably better.

class GeminiBackend(Backend):
    def __init__(self, ai_settings):
        super().__init__(ai_settings)
        
        # Set a sensible default if none provided
        if not self.ai_settings.model or len(self.ai_settings.model) == 0:
            self.ai_settings.model = 'gemini-2.5-flash'

        if self.ai_settings.model_spec:
            # Clean the model name (remove 'gemini/' prefix if present)
            if "/" in self.ai_settings.model:
                self.ai_settings.model = self.ai_settings.model.split("/")[-1]

            self.client = OpenAI(
                # Use v1beta path for the OpenAI-compatible layer
                base_url=self.ai_settings.model_spec.get("base_url", "https://generativelanguage.googleapis.com/v1beta/openai/"),
                api_key=self.ai_settings.model_spec.get("api_key", os.getenv("GEMINI_API_KEY")),
            )
        else:
            # Fallback using standard env vars
            self.client = OpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=os.getenv("GEMINI_API_KEY")
            )

    def do_task(self, task: str) -> str:
        model = self.ai_settings.model
        print(f"[Gemini-Backend] MODEL:{model} task:{task}")

        # Gemini supports standard OpenAI tools, but we'll stick to a simple chat call first
        tools = None
        
        try:
            # CHANGE: Use chat.completions.create with messages format
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful CLI assistant."},
                    {"role": "user", "content": task}
                ],
                tools=tools
            )

            # CHANGE: Extract text from the choices object
            output_text = response.choices[0].message.content
            
            # Print for debug/visibility in CLI
            print(f"{Style.DIM}{model} response: {output_text}{Style.RESET_ALL}")
            
            return output_text

        except Exception as e:
            error_msg = f"Error in GeminiBackend: {str(e)}"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
            return error_msg
