# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2023-2026 - Business Source License (BSL 1.1). See LICENSE
#
# Command line argument parser helper class
# "djargs" = "dj arguments" (commandl line arguments)

import argparse

class CmdLineParser:
    def __init__(self, prog_override=''):
        if prog_override == '':
            self.parser = argparse.ArgumentParser(description='runai - Run AI/LLM or other tasks, optionally with autogen')
        else:
            self.parser = argparse.ArgumentParser(description='runai - Run AI/LLM or other tasks, optionally with autogen', prog=prog_override)
        self.parser.add_argument('--project', '-p', type=str, help='Specify the project name to organize output.')
        self.parser.add_argument('--version', action='store_true', help='Show version number and exit.')
        self.parser.add_argument('-c', '--showsettings', action='store_true', help='Show settings and exit.') # -c "config"
        self.parser.add_argument('-q', '--quiet', action='store_true', help='Quiet file output mode: do not generate any output files (still prints to stdout).')
        self.parser.add_argument('--test', action='store_true', help='Run test task(s).')
        self.parser.add_argument('--prompt', action='store_true', help='Force show task prompt.')
        self.parser.add_argument('-s', '--settings', type=str, help='Specify the task custom settings .py file.')
        self.parser.add_argument('-t', '--task', type=str, help='Specify the task string.')
        self.parser.add_argument('-tf', '--taskfile', type=str, help='Specify the task text file containing possibly multi-line task description.')
        self.parser.add_argument('-i', '--input', type=str, help='Specify a file of input lines if you want to run task on every line in file.')
        self.parser.add_argument('-f', '--folder', type=str, help='Specify the work folder name.')
        self.parser.add_argument('--start-line', type=str, help='If using a multi-line task file, specify the start line number.')
        self.parser.add_argument('-d', '--delay-between', type=str, help='Optional delay in seconds (floating point) between running multiple tasks for multiline mode and others.')
        self.parser.add_argument('-3', '--gpt3', action='store_true', help='Use gpt-3.5-turbo.')
        self.parser.add_argument('-4', '--gpt4', action='store_true', help='Use gpt-4.')
        self.parser.add_argument('--o1-mini', action='store_true', help='Try use model o1-mini')
        self.parser.add_argument('--o1-preview', action='store_true', help='Try use model o1-preview')
        self.parser.add_argument('--model', '-m', type=str, help='Specify preferred model to use.')
        self.parser.add_argument('--dryrun', action='store_true', help='Show roughly what would be done but do not actually execute the task.')

        """
        # todo-future:
        # Capture anything not a flag e.g.:
        # runai "Hi"
        # runai -t "task string" more task string
        # runai --openai "task string"
        # runai --openai "task string" --echo
        self.parser.add_argument(
            'task',
            nargs='*',
            help='Task string (can be multiple words)'
        )
        """

        """
        group = self.parser.add_argument_group('AutoGen settings', 'AutoGen settings.')
        group.add_argument('--local', action='store_true', help='Use only own local AI instances (tag local).')
        group.add_argument('--tag', action='store_true', help='Filter config_list by tag for model selection.')"
        """

        group = self.parser.add_argument_group('Backend selection', 'Backend selection options.')
        group.add_argument('--openai', action='store_true', help='Use OpenAI backend directly (without AutoGen) for tasks.')
        group.add_argument('--djchat', action='store_true', help='Use djchatbot backend for tasks if available.')
        group.add_argument('--autogen', action='store_true', help='Use AutoGen backend.')
        group.add_argument('--dummy', action='store_true', help='Use dummy echo style backend for testing.')
        group.add_argument('--echo', action='store_true', help='Echo mode: Echo back task string for testing.')
        #refactor_parser.add_argument('--backend', type=str, help='Specify the backend name')

        subparsers = self.parser.add_subparsers(dest='subcommand')

        # Subparser for the 'refactor' command
        refactor_parser = subparsers.add_parser('refactor', help='Refactor command help')
        refactor_parser.add_argument('-r', '--find-regex', type=str, help='Specify the refactor regex')
        refactor_parser.add_argument('--find-text', type=str, help='Specify the refactor string to find')
        refactor_parser.add_argument('-w', '--wildcards', type=str, nargs='+', help='Specify the refactor file wildcards')
        refactor_parser.add_argument('--replace-with', type=str, help='Specify the string to replace with (non-AI find and replace)')
        refactor_parser.add_argument('-s', '--send', type=str, nargs='+', help='Specify list of files to send in query for refactoring')

        # Subparser for the 'build' command
        sub_parser = subparsers.add_parser('build', help='Build command help')
        sub_parser.add_argument('-e', '--exec', type=str, help='Specify the file to exec')

        # Subparser for the 'create' command
        create_parser = subparsers.add_parser('create', help='Create command help')
        create_parser.add_argument('-o', '--out', type=str, nargs='+', help='Specify the output file name(s)')

        # Subparser for the 'modify' command
        sub_parser = subparsers.add_parser('modify', help='Modify command help')
        sub_parser.add_argument('--editfile', type=str, help='Specify the file to edit')
        sub_parser.add_argument('-e', '--edit', type=str, nargs='+', help='Specify file(s) to send in query for edit')
