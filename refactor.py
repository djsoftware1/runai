# Copyright (C) 2023 David Joffe / DJ Software
import os
import re
import fnmatch
import djgrep
import autogen
import helper_functions
# regular expressions
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
                print(filename)
                yield filename


def refactor_code(original_code, task, autogen_user_proxy, autogen_coder):
    """Sends code to autogen for refactoring and returns the modified code."""

    #if (re.match(r'^\s*//', origin)

    # todo low) "cpp" hardcoded as code type here for now
    #task_message = task + "\n" + "```cpp" + "\n" + original_code + "\n" + "```\nEnd your reply with the word TERMINATE"
    # check if ends with "\n" and if not add it for "```"
    newline_char = "\n"
    if not original_code.endswith("\n"):
        task_message = task + newline_char + "```cpp" + newline_char + original_code + newline_char + "```"
    else:
        task_message = task + newline_char + "```cpp" + newline_char + original_code + "```"
    #print("===TASK_MESSAGE:" + task_message)

    with open('DEBUGLOG.txt', 'a', encoding='utf-8') as file1:
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

    with open('DEBUGLOG.txt', 'a', encoding='utf-8') as file1:
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
        # Try convert CRLF to LF
        modified_code = modified_code.replace('\r\n', '\n')
    else:
        # If anything went wrong just skip and don't replace
        #print("===REFACTOR:Something went wrong restoring original code")
        modified_code = original_code

    return modified_code

# Note if replace_with defined then it's a simple regex replace that does not actually need AI and we just do ourselves
def Refactor(in_folder, wildcard, needle, refactor_negmatches, replace_with, sTask, autogen_user_proxy, autogen_coder):
    file_list = find_files(in_folder, wildcard)

    # Compile negative match patterns for efficiency
    negmatch_patterns = [re.compile(negmatch) for negmatch in refactor_negmatches]

    for file_path in file_list:
        # maybe multiline matching should be an option
        #occurrences = djgrep.grep_file(file_path, needle)
        occurrences = djgrep.grep_multiline2(file_path, needle)
        #occurrences = djgrep.grep_multiline(file_path, needle)

        if not occurrences:
            continue  # Skip files without the needle

        #debug:print(f"===REFACTOR:Found {len(occurrences)} occurrences in file {file_path}")
        # Getting encoding errors reading some files so first try utf8 if that fails try cp1252 etc. - probably have to refine this further
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            # Fallback to a different encoding, or handle the error as appropriate
            with open(file_path, 'r', encoding='cp1252') as file:
                lines = file.readlines()

        # Iterate over occurrences in reverse order to make it easier to deal with line numbers changing as we do replacements
        for line_num, line_content, num_lines in reversed(occurrences):
            # Skip commented lines
            # THIS ISN'T quite correct for multi-line, hmm
            # Also sometimes we may actually want to target comment lines so let's make this configurable via new negmatches setting:
            #if (re.match(r'^\s*//', line_content)):
            #    continue

            # Skip other optional custom 'negative-matches' if any
            # For example if we are refactoring a function call we might want to skip the function definition and only refactor usages of a function not the actual definition itself
            # re.match is wrong for neg-matches because it only matches from beginning of string, we want to match anywhere in the string
            #for negmatch in refactor_negmatches:
            #    if (re.match(negmatch, line_content)):
            #        continue
            # Check against negative match patterns
            skip_line = False
            for negmatch_pattern in negmatch_patterns:
                if negmatch_pattern.search(line_content):
                    skip_line = True
                    break  # Break the inner loop
                
            if skip_line:
                continue  # Skip to the next occurrence                

            # Capture leading whitespace (spaces and tabs) so we can re-apply original indentation to replaced code (at least crudely first line for now)
            leading_whitespace = re.match(r'^(\s*)', line_content)
            indent = leading_whitespace.group(1) if leading_whitespace else ''

            print(f"===REFACTOR:Try refactor line {line_num} in file {file_path} num_lines {num_lines}")
            # Refactor code
            if replace_with is not None and replace_with!='':
                # Simple regex replace, no AI needed
                modified_code = re.sub(needle, replace_with, line_content)
            else:
                # Pass to AI to refactor
                modified_code = refactor_code(line_content, sTask, autogen_user_proxy, autogen_coder)
            if modified_code!=line_content:
                print(f"===REFACTOR:Replacing line {line_num} in file {file_path} num_lines {num_lines}")
                print(f"========START:")
                print(f"modified_code = {modified_code}")
                print(f"========END")

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
                ######print(f"===REFACTOR:modified_lines[-1] is {modified_lines[-1]}")
                #print(f"##################################################LEN:{len(modified_lines)}")
                if modified_lines and modified_lines[-1] == '':
                    modified_lines.pop()
                if modified_lines and modified_lines[-1] == '':
                    modified_lines.pop()
                #print(f"##################################################LEN:{len(modified_lines)}")
                add_debug_markers = False
                if len(modified_lines)>0:
                    # Append to the first and last some debug text
                    if add_debug_markers:
                        modified_lines[0] = "/*<refactor>*/" + modified_lines[0]
                        modified_lines[-1] = modified_lines[-1] + "/*</refactor>*/"
                    #for i in range(len(modified_lines)):
                    #    print(f"LINE:{i} {modified_lines[i]}")
                

                # This accounts for the modified code having a different number of lines
                # Replace original line(s) with modified lines
                #lines[line_num - 1:line_num] = modified_lines

                # Calculate the slice range for the original lines to be replaced
                original_lines_start = line_num - 1
                original_lines_end = original_lines_start + num_lines
                print(f"===REFACTOR:original_lines_start {original_lines_start}, original_lines_end {original_lines_end}, num_lines {num_lines}")

                # Replace the original line(s) with modified lines
                lines[original_lines_start:original_lines_end] = modified_lines

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
