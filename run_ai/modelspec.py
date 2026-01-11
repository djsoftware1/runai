# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 202 - Business Source License (BSL 1.1). See LICENSE

# Handle model specifiers like "ollama/deepseek-r1:8b"

# todo[]: "localhost" can cause issues like small lookup delays or ipv6 confusion .. better to use 127.0.0.1?

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
      anthropic/claude-haiku-4-5-20251001
      gemini/gemini-2.5-flash
      xai/grok-4
    """
    # todo[] - could try smartly auto-detect based on what API_KEY keys user has ..s
    #logging.debug(f"(model_spec \"{spec}\")")
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

    if provider == "anthropic":
        return {
            "provider": "anthropic",
            "model": model,
            "base_url": "https://api.anthropic.com/v1",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
        }

    if provider == "groq":
        return {
            "provider": "groq",
            "model": model,
            "base_url": "https://api.groq.com/v1",
            "api_key": os.getenv("GROQ_API_KEY"),
        }

    if provider == "grok":
        return {
            "provider": "grok",
            "model": model,
            "base_url": "https://api.grok.com/v1",
            "api_key": os.getenv("GROK_API_KEY"),
        }

    if provider == "lite":
        return {
            "provider": "lite",
            "model": model,
            "base_url": "http://localhost:8000/v1",
            "api_key": "LITE_API_KEY",  # Assuming no real key needed for local
        }

    if provider == "azure":
        return {
            "provider": "azure",
            "model": model,
            "base_url": "https://api.azure.com/v1",
            "api_key": os.getenv("AZURE_API_KEY"),
        }

    if provider == "huggingface":
        return {
            "provider": "huggingface",
            "model": model,
            "base_url": "https://api.huggingface.co/v1",
            "api_key": os.getenv("HUGGINGFACE_API_KEY"),
        }

    if provider == "ibm":
        return {
            "provider": "ibm",
            "model": model,
            "base_url": "https://api.ibm.com/v1",
            "api_key": os.getenv("IBM_API_KEY"),
        }

    # hm .. i think google maybe 'is' gemini?
    # FWIW dj2026-01 According to Gemini:
    # In the context of 2026 and the OpenAI-compatible API:
    # The Model Series is Gemini.
    # The Provider is technically Google, but in developer circles, "Gemini" is often used to refer to the Google AI Studio (the developer-friendly, key-only API).
    # The Standard: For your modelspec, it is best to treat gemini as the provider for the AI Studio API (using the generativelanguage URL) and reserve google or vertex for the enterprise Google Cloud Platform."
    # We can do more testing etc. to clarify and resolve and extend these in future also maybe with more settings/configurability
    # Logic for Google AI Studio (Gemini)
    if provider == "gemini" or provider == "google":
        return {
            "provider": "gemini",  # Standardize on one internal name
            "model": model,        # e.g., "gemini-2.5-flash"
            # Use the v1beta/openai/ path for the OpenAI library
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", 
            # Check for both env var styles to be user-friendly
            "api_key": os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
        }    
    """
    if provider == "google":
        return {
            "provider": "google",
            "model": model,
            "base_url": "https://api.google.com/v1",
            "api_key": os.getenv("GOOGLE_API_KEY"),
        }
    """

    if provider == "aws":
        return {
            "provider": "aws",
            "model": model,
            "base_url": "https://api.aws.com/v1",
            "api_key": os.getenv("AWS_API_KEY"),
        }

    if provider == "baidu":
        return {
            "provider": "baidu",
            "model": model,
            "base_url": "https://api.baidu.com/v1",
            "api_key": os.getenv("BAIDU_API_KEY"),
        }

    if provider == "tencent":
        return {
            "provider": "tencent",
            "model": model,
            "base_url": "https://api.tencent.com/v1",
            "api_key": os.getenv("TENCENT_API_KEY"),
        }

    if provider == "yandex":
        return {
            "provider": "yandex",
            "model": model,
            "base_url": "https://api.yandex.com/v1",
            "api_key": os.getenv("YANDEX_API_KEY"),
        }

    if provider == "deepseek":
        return {
            "provider": "deepseek",
            "model": model,
            "base_url": "https://api.deepseek.com/v1",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
        }

    if provider == "xai":
        return {
            "provider": "xai",
            "model": model,
            "base_url": "https://api.xai.com/v1",
            "api_key": os.getenv("XAI_API_KEY"),
        }

    # Safer not to return None - we return an entry saying 'unknown' or somesuch
    return {
        "provider": "unknown",
        "model": model,
        "base_url": "http://127.0.0.1:80/v1",
        "api_key": "_",
    }
