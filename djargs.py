# Copyright (C) David Joffe 2023
# Command line argument parser helper class
import argparse

class CmdLineParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Command line parser helper class.')
        self.parser.add_argument('--help', action='store_true', help='Show this help message and exit.')
        self.parser.add_argument('--version', action='store_true', help='Show version number and exit.')
        self.parser.add_argument('--taskfile', type=str, help='Specify the task file.')
        self.parser.add_argument('--settings', type=str, help='Specify the settings file.')
        self.parser.add_argument('--task', type=str, help='Specify the task string.')
        self.parser.add_argument('--folder', type=str, help='Specify the folder name.')

    def parse_args(self):
        return self.parser.parse_args()
