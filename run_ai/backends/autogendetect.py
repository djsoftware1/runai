# dj2026 try dynamically detect autogen

import importlib.util

def has_autogen() -> bool:
    return importlib.util.find_spec("autogen") is not None
