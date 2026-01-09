# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 202 - Business Source License (BSL 1.1). See LICENSE

# Handle model specifiers like "ollama/deepseek-r1:8b"

import os

# hmm (low - dj2026-01) should we ever return 'None' here or rather just return a generic thing that at lesat is less likely to trigger exceptions? .. 
def parse_model_spec(spec: str):
    """
    Examples:
      ollama/deepseek-r1:8b
      openai/gpt-4o-mini
      lmstudio/phi-3
    """
    if "/" not in spec:
        return None

    provider, model = spec.split("/", 1)

    provider = provider.lower()

    if provider == "ollama":
        return {
            "provider": "ollama",
            "model": model,
            "base_url": "http://localhost:11434/v1",
            "api_key": None,  # ollama ignores
        }

    if provider == "lmstudio":
        return {
            "provider": "lmstudio",
            "model": model,
            "base_url": "http://localhost:1234/v1",
            "api_key": None,
        }

    if provider == "openai":
        return {
            "provider": "openai",
            "model": model,
            "base_url": "https://api.openai.com/v1",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }

    return None
