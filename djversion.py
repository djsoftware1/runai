# djversion.py: Small "Version" helper class to manage and return current version of the application
# Copyright (C) David Joffe 2023-2025
# Version helper

class Version:
    def __init__(self):
        self.current_version = '0.8.3'

    def get_version(self):
        return self.current_version
