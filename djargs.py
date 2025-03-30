# Copyright (C) David Joffe / DJ Software 2023-2025
# Command line argument parser helper class
# "djargs" = "dj arguments" (commandl line arguments)
import argparse

class CmdLineParser:
    def __init__(self, prog_override=''):
        if prog_override == '':
            self.parser = argparse.ArgumentParser(description='runai - Run AI/LLM or other tasks, optionally with autogen')
        else:
            self.parser = argparse.ArgumentParser(description='runai - Run AI/LLM or other tasks, optionally with autogen', prog=prog_override)
        #self.parser.add_argument('--help', action='store_true', help='Show this help message and exit.')
        self.parser.add_argument('--version', action='store_true', help='Show version number and exit.')
        self.parser.add_argument('--showsettings', action='store_true', help='Show settings and exit.')
        self.parser.add_argument('--test', action='store_true', help='Run test task(s).')
        self.parser.add_argument('--prompt', action='store_true', help='Force show task prompt.')
        self.parser.add_argument('-s', '--settings', type=str, help='Specify the task custom settings .py file.')
        self.parser.add_argument('-t', '--task', type=str, help='Specify the task string.')
        self.parser.add_argument('-tf', '--taskfile', type=str, help='Specify the task text file containing possibly multi-line task description.')
        self.parser.add_argument('-i', '--input', type=str, help='Specify a file of input lines if you want to run task on every line in file.')
        self.parser.add_argument('-f', '--folder', type=str, help='Specify the work folder name.')
        self.parser.add_argument('--start-line', type=str, help='If using a multi-line task file, specify the start line number.')
        #self.parser.add_argument('--delay-before', type=str, help='Delay in seconds before running task ')
        self.parser.add_argument('-d', '--delay-between', type=str, help='Optional delay in seconds (floating point) between running multiple tasks for multiline mode and others.')
        self.parser.add_argument('-3', '--gpt3', action='store_true', help='Use gpt-3.5-turbo.')
        self.parser.add_argument('-4', '--gpt4', action='store_true', help='Use gpt-4.')
        self.parser.add_argument('--o1-mini', action='store_true', help='Try use model o1-mini')
        self.parser.add_argument('--o1-preview', action='store_true', help='Try use model o1-preview')
        self.parser.add_argument('--model', '-m', type=str, help='Specify preferred model to use.')
        self.parser.add_argument('--dryrun', action='store_true', help='Show roughly what would be done but do not actually execute the task.')


        group = self.parser.add_argument_group('Backend selection', 'Backend selection options.')
        #self.parser.add_argument('--use-djchatbot', '--djchatbot', action='store_true', help='use djchatbot backend for chat tasks.')
        group.add_argument('--djchat', action='store_true', help='Use djchatbot backend for tasks if available.')
        #group.add_argument('--openai', action='store_true', help='Use OpenAI backend directly for tasks.')



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
        # TODO this should become , nargs='+' an array of wildcards
        refactor_parser.add_argument('-r', '--find-regex', type=str, help='Specify the refactor regex')
        refactor_parser.add_argument('--find-text', type=str, help='Specify the refactor string to find')
        refactor_parser.add_argument('-w', '--wildcards', type=str, nargs='+', help='Specify the refactor file wildcards')
        refactor_parser.add_argument('--replace-with', type=str, help='Specify the string to replace with (non-AI find and replace)')
        refactor_parser.add_argument('-s', '--send', type=str, nargs='+', help='Specify list of files to send in query for refactoring')
        """
        refactor_parser.add_argument('--replace-text', type=str, help='Specify the refactor string to replace')
        refactor_parser.add_argument('--neg-regex', type=str, nargs='+', help='Specify the refactor regex to exclude')
        refactor_parser.add_argument('--neg-text', type=str, help='Specify the refactor string to exclude')
        refactor_parser.add_argument('--neg-replace-text', type=str, help='Specify the refactor string to exclude')
        refactor_parser.add_argument('--neg-replace-with', type=str, help='Specify the refactor string to exclude')
        refactor_parser.add_argument('-t', '--codetype', type=str, help='Specify the refactor code type')
        refactor_parser.add_argument('-e', '--exec', type=str, help='Specify the command to exec')
        refactor_parser.add_argument('-f', '--folder', type=str, help='Specify the work folder name.')
        refactor_parser.add_argument('-i', '--input', type=str, help='Specify a file of input lines.')
        refactor_parser.add_argument('-o', '--outname', type=str, help='Specify the output file name')
        refactor_parser.add_argument('-if', '--inputfile', type=str, nargs='+', help='Specify the input file name')
        """

        # Subparser for the 'build' command
        sub_parser = subparsers.add_parser('build', help='Build command help')
        sub_parser.add_argument('-e', '--exec', type=str, help='Specify the file to exec')

        # Subparser for the 'create' command
        create_parser = subparsers.add_parser('create', help='Create command help')
        # Make this also -o or --outname
        create_parser.add_argument('-o', '--out', type=str, nargs='+', help='Specify the output file name(s)')

        # Subparser for the 'createfrom' command
        sub_parser = subparsers.add_parser('createfrom', help='Create command help')
        sub_parser.add_argument('-s', '--srcdir', type=str, help='Specify the output file name')

        # Subparser for the 'modify' command
        # MAY CHANGE:
        sub_parser = subparsers.add_parser('modify', help='Modify command help')
        # MAY CHANGE:
        sub_parser.add_argument('--editfile', type=str, help='Specify the file to edit')
        #sub_parser.add_argument('--editfiles', '-e', type=str, help='Specify the files to edit')
        # MAY CHANGE:
        sub_parser.add_argument('-e', '--edit', type=str, nargs='+', help='Specify file(s) to send in query for edit')

        # Subparser for the 'edit' command (? synonym for modify? or different?)
        """
        sub_parser = subparsers.add_parser('edit', help='Modify command help')
        """


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
