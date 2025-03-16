# djabout.py: Small helper class to show some core 'about this application' info
# Copyright (C) 2023-2025 David Joffe / DJ Software
# runai https://github.com/djsoftware1/runai GitHub source repo
# By David Joffe / DJ Software.
#-------------------------------------------------------------------------------
# Import necessary libraries

import djversion
# For colored text in output
from colorama import Fore, Style

class djAbout:
    #def __init__(self):
    #   self.current_version = '0.8.3'

    def show_about(self):
        # brief about overview
        print(f"{Fore.YELLOW}runai {Fore.CYAN}Run or automate AI/LLM & other kinds of tasks, like code refactoring, optionally with AutoGen.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}runai -h {Fore.CYAN}show full help {Fore.YELLOW}--showsettings {Fore.CYAN}just show settings {Fore.YELLOW}--version {Fore.CYAN}show version number {Fore.YELLOW}--dryrun{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}      -t \"TASK\" {Fore.CYAN}\"task for LLM to do\" {Fore.YELLOW}-tf \"TaskFile\"{Fore.CYAN} \"file with task\". default={Fore.GREEN}autotasks.txt{Style.RESET_ALL}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}      -m \"MODEL\" {Fore.CYAN}\"select model\" {Fore.YELLOW}-3 {Fore.CYAN}use gpt-3 {Fore.YELLOW}-4 {Fore.CYAN}use gpt-4 {Fore.YELLOW}--o1-mini --o1-preview{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}      -f \"FOLDER\" {Fore.CYAN}\"set work-folder\" (refactor,build,create,createfrom,modify) ...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}      -i \"InputFile\" {Fore.CYAN}to batch-run task on all lines, with substitution. default={Fore.GREEN}input.txt{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Created by{Fore.GREEN} David Joffe. v{djversion.Version().get_version()} beta. {Fore.BLUE}github.com/djsoftware1/runai{Fore.BLUE} djoffe.com")
        print(f"{Style.RESET_ALL}__________________________________________________________________")