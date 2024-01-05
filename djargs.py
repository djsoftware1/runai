# Copyright (C) David Joffe 2023-2024
# Command line argument parser helper class
import argparse

class CmdLineParser:
    def __init__(self):

        self.parser = argparse.ArgumentParser(description='runai - Run AI tasks with autogen')
        #self.parser.add_argument('--help', action='store_true', help='Show this help message and exit.')
        self.parser.add_argument('--version', action='store_true', help='Show version number and exit.')
        self.parser.add_argument('--showsettings', action='store_true', help='Show settings and exit.')
        self.parser.add_argument('-s', '--settings', type=str, help='Specify the task custom settings .py file.')
        self.parser.add_argument('-t', '--task', type=str, help='Specify the task string.')
        self.parser.add_argument('-tf', '--taskfile', type=str, help='Specify the task text file containing possibly multi-line task description.')
        self.parser.add_argument('-i', '--input', type=str, help='Specify a file of input lines.')
        self.parser.add_argument('-f', '--folder', type=str, help='Specify the work folder name.')


        subparsers = self.parser.add_subparsers(dest='subcommand')

        # Todo what about also being able to set up a list of predefined tasks easily almost like macros?
        # e.g. have a folder 'tasks/predefined' and then can do 'runai run predefined:taskname' or something like that
        # and/or a list of them e.g. 'runai run task1, task2, task3' (although shell can do this with "&&")
        # Then e.g. should be able to set up your own custom things like 'buildtlex' or 'buildgnukem' etc.


        ## half of these aren't used yet - just placeholders

        # Subparser for the 'refactor' command
        refactor_parser = subparsers.add_parser('refactor', help='Refactor command help')
        #refactor_parser.add_argument('--taskfile', type=str, help='Specify the task file')
        # In fact it's an array of regex's I think? But then how do we specify on command line an array?
        # Maybe could be multiple --find-regex and --find-text?
        refactor_parser.add_argument('--find-regex', type=str, help='Specify the refactor regex')
        refactor_parser.add_argument('--find-text', type=str, help='Specify the refactor string to find')

        # Subparser for the 'build' command
        sub_parser = subparsers.add_parser('build', help='Build command help')
        sub_parser.add_argument('-e', '--exec', type=str, help='Specify the file to exec')

        # Subparser for the 'create' command
        create_parser = subparsers.add_parser('create', help='Create command help')
        # Make this also -o or --outname
        create_parser.add_argument('-o', '--outname', type=str, help='Specify the output file name')

        # Subparser for the 'createfrom' command
        sub_parser = subparsers.add_parser('createfrom', help='Create command help')
        sub_parser.add_argument('-s', '--srcdir', type=str, help='Specify the output file name')

        # Subparser for the 'modify' command
        sub_parser = subparsers.add_parser('modify', help='Modify command help')
        sub_parser.add_argument('--editfile', type=str, help='Specify the file to edit')

        """
        # Subparser for the 'clone' command
        sub_parser = subparsers.add_parser('clone', help='Clone command help')
        #sub_parser.add_argument('--exec', type=str, help='Specify the file to exec')

        # Subparser for the 'run' command
        sub_parser = subparsers.add_parser('run', help='Run command help')
        sub_parser.add_argument('-e', '--exec', type=str, help='Specify the command to exec')
        """

    def parse_args(self):
        return self.parser.parse_args()
