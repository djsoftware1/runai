# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 202 - Business Source License (BSL 1.1). See LICENSE

# Handle model specifiers like "ollama/deepseek-r1:8b"

import os

# NB model_spec may contain sensitive keys
# hmm (low - dj2026-01) should we ever return 'None' here or rather just return a generic thing that at lesat is less likely to trigger exceptions? .. 
# NB: IMPORTANT: The OpenAI backend has a slightly issue where it gives error if no API key environment variable even if you are completely using local only like ollama .. so we make it return 'dummy' keys here. dj2026-01
def parse_model_spec(spec: str):
    """
    Examples:
      ollama/deepseek-r1:8b
      openai/gpt-4o-mini
      lmstudio/phi-3
    """
    print(f"(model_spec \"{spec}\")",end='')
    if "/" not in spec:
        spec = "openai/" + spec;
        # If no prefix part passed assume this default openai/ - later we can make that configurable default by user
        #return parse_model_spec("openai/" + spec)
        #return None

    provider, model = spec.split("/", 1)

    provider = provider.lower()

    if provider == "ollama":
        return {
            "provider": "ollama",
            "model": model,
            "base_url": "http://localhost:11434/v1",
            #"api_key": None,  # ollama ignores
            "api_key": "ollama",  # dummy, explicit
        }

    if provider == "lmstudio":
        return {
            "provider": "lmstudio",
            "model": model,
            "base_url": "http://localhost:1234/v1",
            "api_key": "lmstudio"  # dummy, explicit
        }

    if provider == "openai":
        return {
            "provider": "openai",
            "model": model,
            "base_url": "https://api.openai.com/v1",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }

    return None
