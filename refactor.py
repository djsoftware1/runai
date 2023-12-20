# Copyright (C) 2023 David Joffe / DJ Software
import os
import re
import fnmatch
import autogen
import helper_functions
# regular expressions
import re
import globals
from globals import g_ai_output_saved_last_code_block
# Global variable initialization at the top level of the module
#g_ai_output_saved_last_code_block = None

def find_files(directory, pattern):
    """Recursively finds all files in a directory matching the pattern."""
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def grep_file(filename, needle):
    """Searches for a needle in a file and returns line numbers and lines."""
    # Getting encoding errors reading some files so first try utf8 if that fails try cp1252 etc. - probably have to refine this further
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        # Fallback to a different encoding, or handle the error as appropriate
        with open(filename, 'r', encoding='cp1252') as file:
            lines = file.readlines()

    return [(index + 1, line) for index, line in enumerate(lines) if needle in line]

def refactor_code(original_code, task, autogen_user_proxy, autogen_coder):
    """Sends code to autogen for refactoring and returns the modified code."""

    #if (re.match(r'^\s*//', origin)

    # todo low) "cpp" hardcoded as code type here for now
    task_message = task + "\n" + "```cpp" + "\n" + original_code + "\n" + "```\nEnd your reply with the word TERMINATE"
    #print("===TASK_MESSAGE:" + task_message)

    with open('DEBUGLOG.txt', 'a') as file1:
        file1.write("\n<REFACTORpre>originalcode:\n")
        file1.write(original_code)
        file1.write("</REFACTORpre>\n")


    # (1) First let the AI do its thing
    # (2) Then get the AI output which gets captured in the DualOutput class
    # We want to use the final AI output code file
    autogen_user_proxy.initiate_chat(autogen_coder, message=task_message)

    # Wait for a bit to allow for processing
    #time.sleep(2)  # wait for 1 second, adjust as needed

    str_modified_code = ''

    # Initialize modified_code with original_code as default
    modified_code = original_code

    global g_ai_output_saved_last_code_block
    if globals.g_ai_output_saved_last_code_block is not None and globals.g_ai_output_saved_last_code_block!='':
        str_modified_code = globals.g_ai_output_saved_last_code_block
        modified_code = globals.g_ai_output_saved_last_code_block
    # We must be careful if we printf code!
    # because our captured output stuff could trigger codeblock saving and change g_ai_output_saved_last_code_block
    #print("===REFACTOR:Last code block from AI is " + g_ai_output_saved_last_code_block)

    with open('DEBUGLOG.txt', 'a') as file1:
        file1.write("\n<REFACTOR2>originalcode:\n")
        file1.write(original_code)
        file1.write("</REFACTOR2>\n")
        file1.write("\n<REFACTOR3>modified_code:\n")
        file1.write(str_modified_code)
        file1.write("\n</REFACTOR3>\n")

    # Check if the global variable has been set
    if str_modified_code is not None and str_modified_code!='':
        #print("===REFACTOR:Using saved last code block from AI" + str_modified_code)
        modified_code = str_modified_code
    else:
        # If anything went wrong just skip and don't replace
        #print("===REFACTOR:Something went wrong restoring original code")
        modified_code = original_code

    return modified_code

def Refactor(in_folder, wildcard, needle, sTask, autogen_user_proxy, autogen_coder):
    file_list = find_files(in_folder, wildcard)

    for file_path in file_list:
        occurrences = grep_file(file_path, needle)

        if not occurrences:
            continue  # Skip files without the needle

        # Getting encoding errors reading some files so first try utf8 if that fails try cp1252 etc. - probably have to refine this further
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            # Fallback to a different encoding, or handle the error as appropriate
            with open(file_path, 'r', encoding='cp1252') as file:
                lines = file.readlines()

        # Iterate over occurrences in reverse order to make it easier to deal with line numbers changing as we do replacements
        for line_num, line_content in reversed(occurrences):
            # Skip commented lines
            # THIS ISN'T quite correct for multi-line, hmm
            if (re.match(r'^\s*//', line_content)):
                continue

            # Capture leading whitespace (spaces and tabs) so we can re-apply original indentation to replaced code (at least crudely first line for now)
            leading_whitespace = re.match(r'^(\s*)', line_content)
            indent = leading_whitespace.group(1) if leading_whitespace else ''

            print(f"===REFACTOR:Try refactor line {line_num} in file {file_path}")
            # Refactor code
            modified_code = refactor_code(line_content, sTask, autogen_user_proxy, autogen_coder)
            if modified_code!=line_content:
                print(f"===REFACTOR:Replacing line {line_num} in file {file_path}")

                # If we sent it e.g. " Copyright (C) 2022 David Joffe" and it sent back
                # " Copyright (C) 2023 David Joffe" we don't want to just append its space and get:
                # "  Copyright (C) 2023 David Joffe"
                # In effect if it returns indentation matching the original let's not add any more
                leading_whitespace_returned = re.match(r'^(\s*)', modified_code)
                indent_modified = leading_whitespace_returned.group(1) if leading_whitespace_returned else ''


                # Apply the leading whitespace to each line of modified_code
                if (indent_modified==indent):
                    modified_lines = [line if line.strip() else '' for line in modified_code.split('\n')]
                else:
                    modified_lines = [indent + line if line.strip() else '' for line in modified_code.split('\n')]

                # Remove an extra newline at the end if present
                # (litellm with ollama/codemistral at least for me returning lots of this extra blank line at end of code block so strip it out)
                if modified_lines and modified_lines[-1] == '':
                    modified_lines.pop()
                if modified_lines and modified_lines[-1] == '':
                    modified_lines.pop()
                

                # This accounts for the modified code having a different number of lines
                # Replace original line(s) with modified lines
                lines[line_num - 1:line_num] = modified_lines

                out_folder = in_folder#"out_folder"  # Define your output folder
                out_file_path = os.path.join(out_folder, os.path.relpath(file_path, in_folder))
                os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
                # Save the modified file
                print(f"===REFACTOR:Saving file: {out_file_path}")
                with open(out_file_path, 'w', encoding='utf-8') as file:
                    for line in lines:
                        file.write(line if line.endswith('\n') else line + '\n')

# Example usage
#Refactor("input_folder", "*.cpp", "needle", "Refactor this line to...")
