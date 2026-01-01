

# regex for show_setting for hiding sensitive data
import re
# For colored text in output
from colorama import Fore, Style

# Small helper to show setting name and value in different color
def show_setting(name, value, indent=0, descriptionString="", strKeyShortcut=""):
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

        print(f"{Fore.GREEN}{strDashesBefore}{name}:{Style.RESET_ALL} {Fore.CYAN}{s}{Style.RESET_ALL}{strDescription} {strShortCut}")
    else:
        print(f"{Fore.GREEN}{strDashesBefore}{name}:{Style.RESET_ALL} {Fore.RED}-{Style.RESET_ALL}{strDescription} {strShortCut}")

