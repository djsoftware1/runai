# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2023-2026 - Business Source License (BSL 1.1). See LICENSE
#
# display.py

# regex for show_setting for hiding sensitive data
import re
# For colored text in output
from colorama import Fore, Style

# Small helper to show setting name and value in different color
# NB! This is important to use as it hides sensitive info like user API keys!
def show_setting(name, value, indent=0, descriptionString="", strKeyShortcut="", strEnd='\n', defaultValue=''):
    # dj2025-03 add indent and descriptionString (optional)
    #sBULLET_INFO=
    sBULLET_INFO=""#"→""→ 🛈"
    strDashesBefore=""
    if indent > 0:
        print("   " * indent, end="")
        strDashesBefore="■ "
        #strDashesBefore = sBULLET_INFO
    else:
        strDashesBefore=""
    
    strDescription=""
    if len(descriptionString) > 0:
        strDescription = f" {sBULLET_INFO} {Fore.MAGENTA}{descriptionString}{Style.RESET_ALL}"
    if len(defaultValue) > 0:
        strDescription = strDescription + f" (default {Fore.MAGENTA}{defaultValue}{Style.RESET_ALL})"


    # e.g. "-f FOLDER" info stuff
    # ■ -f FOLDER: Nodjfsdj dsfkjl → Work-folder for tasks like auto-refactoring
    # ■ -t TASK: Hey there! tell me how to make cofee
    strShortCut=""
    if len(strKeyShortcut) > 0:
        strShortCut = f"{Fore.GREEN}{strKeyShortcut}{Style.RESET_ALL}"

    if value is not None:

        # NB hide sensitive data like API keys
        s = f"{value}"
        # Commenting out below as overly-greedy!
        #s = re.sub(r'sk-(.*)["\']', "\"(hidden)\"", s, flags=re.MULTILINE)
        s = re.sub(
            r'(["\']?)\s*(sk-[^"\']+)\s*(["\']?)',
            r'"(hidden)"',
            s,
            flags=re.IGNORECASE,
        )

        #show_setting("openai.config_list", config_list, 1)

        print(f"{Fore.GREEN}{strDashesBefore}{name}:{Style.RESET_ALL} {Fore.CYAN}{s}{Style.RESET_ALL}{strDescription} {strShortCut}", end=strEnd)
    else:
        print(f"{Fore.GREEN}{strDashesBefore}{name}:{Style.RESET_ALL} {Fore.RED}-{Style.RESET_ALL}{strDescription} {strShortCut}", end=strEnd)

