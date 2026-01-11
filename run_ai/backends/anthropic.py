# runai OpenAI Backend class - directly send task to OpenAI backend.
#
# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2025-2026 - Business Source License (BSL 1.1). See LICENSE
#
# run_ai/backends/anthropic.py
# dj2026-01

from run_ai.backends.base import Backend
from colorama import Fore, Style
import requests

class AnthropicBackend(Backend):
    def __init__(self, ai_settings):
        super().__init__(ai_settings)

        if not self.ai_settings.model:
            raise RuntimeError("Anthropic model not set")

        if not self.ai_settings.model_spec:
            raise RuntimeError("Anthropic model_spec missing")

        self.api_key = self.ai_settings.model_spec["api_key"]
        self.base_url = self.ai_settings.model_spec["base_url"]
        self.model = self.ai_settings.model_spec.get("model", self.ai_settings.model)

        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

    def do_task(self, task: str) -> str:
        print(f"[Anthropic-backend] MODEL:{self.model} task:{task}")

        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": task,
                }
            ],
        }

        resp = requests.post(
            f"{self.base_url}/messages",
            headers=self.headers,
            json=payload,
            timeout=60,
        )

        # Billing / quota errors land here cleanly
        if resp.status_code != 200:
            print(f"{Fore.RED}Anthropic error:{Style.RESET_ALL}", resp.text)
            resp.raise_for_status()

        data = resp.json()

        # Normalize to simple text (runai convention)
        text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")

        print(f"{Style.DIM}{self.model} response:{Style.RESET_ALL}")
        print(text)
        return text

