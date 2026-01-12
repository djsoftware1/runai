# djversion.py: Small "Version" helper class to manage and return current version of the application
# Copyright (C) David Joffe and DJ Software 2023-2025
# Version helper
# runai website: https://djoffe.com/dj-software/runai/

from run_ai._version import __version__

class Version:
    def __init__(self):
        self.current_version = __version__

    def get_version(self):
        return self.current_version
