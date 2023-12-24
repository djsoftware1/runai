# Copyright (C) 2023 David Joffe / DJ Software
import re
import os
import sys
from globals import g_ai_output_saved_last_code_block
import globals
"""
--------------------------------------------------------------------------------
coder (to user_proxy):

```cpp
# filename: djQuaternion.cpp

#include <cmath>
"""

# global variable to save last code block from AI
#g_ai_output_saved_last_code_block = None

# Return array of created files (if any) else return empty array
def create_files_from_ai_output(ai_output, output_directory='output_files'):
    """
    Parses the AI output string for filenames and content, and creates files with that content.

    :param ai_output: String containing the AI output.
    :param output_directory: Directory where files will be created.
    """

    # [dj2023-12] That confusing-looking "/#][/#]?" is a regex trick to match either "//" or "#" because it is I think supposed to return:
    # "// filename.cpp
    # but my ollama/mistral instance is returning it like:
    # "# filename.cpp
    # so I added the optional "#" to the regex to match both where it had been "// filename" I made it "[/#][/#]? filename"


    """
    NOTE: For auto-capturing output it sometimes returns like so instead of "```" causing auto-capture AI output to fail:
    For example:
    '''cpp
    std::wstring g_sAppPath = L"";
    '''
    should become
    ```cpp
    std::wstring g_sAppPath = L"";
    ```
    """
    # Regex to replace triple single quotes with optional language specifier (like 'cpp') with triple backticks
    # This regex looks for triple single quotes possibly followed by a language specifier
    # and replaces them with triple backticks.
    corrected_output = re.sub(r"^\s*'''(?:\w+)?\s*|\s*'''\s*$", "```", ai_output, flags=re.MULTILINE)
    ai_output = corrected_output
    #ai_output = ai_output.replace("'''", "```")

    # Regular expression to find code blocks and filenames
    #pattern = r"```(.*?)// filename: (.*?)\n(.*?)```"
    #matches = re.findall(pattern, ai_output, re.DOTALL)
    # Regular expression to find code blocks and filenames (filename is optional)
    #pattern = r"```(.*?)\n(// filename: (.*?)\n)?(.*?)```"
    pattern = r"```(.*?)\n([/#][/#]? filename: (.*?)\n)?(.*?)```"
    matches = re.findall(pattern, ai_output, re.DOTALL)

    global g_ai_output_saved_last_code_block

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Return array of created files (if any) else return empty array
    ret_created_files = []
    for match in matches:
        language, _, filename, content = match
        # Strip whitespace and unwanted characters from filename
        filename = filename.strip().replace('/', os.sep)

        extension = 'txt'  # Default extension if not provided
        if language=='cpp':
            extension = 'cpp'
        elif language=='python':
            extension = 'py'
        elif language=='javascript':
            extension = 'js'
        elif language=='html':
            extension = 'html'
        elif language=='css':
            extension = 'css'
        elif language=='json':
            extension = 'json'
        elif language=='xml':
            extension = 'xml'
        elif language=='markdown':
            extension = 'md'
        elif language=='bash':
            extension = 'sh'
        elif language=='csharp':
            extension = 'cs'
        elif language=='java':
            extension = 'java'
        elif language=='php':
            extension = 'php'
        elif language=='ruby':
            extension = 'rb'
        elif language=='sql':
            extension = 'sql'
        elif language=='swift':
            extension = 'swift'
        elif language=='typescript':
            extension = 'ts'
        elif language=='vbnet':
            extension = 'vb'
        elif language=='c':
            extension = 'c'
        elif language=='go':
            extension = 'go'
        elif language=='kotlin':
            extension = 'kt'
        elif language=='r':
            extension = 'r'
        elif language=='rust':
            extension = 'rs'
        elif language=='scala':
            extension = 'scala'
        elif language=='dart':
            extension = 'dart'
        elif language=='lua':
            extension = 'lua'
        elif language=='perl':
            extension = 'pl'
        elif language=='powershell':
            extension = 'ps1'
        elif language=='haskell':
            extension = 'hs'
        elif language=='elixir':
            extension = 'ex'
        elif language=='clojure':
            extension = 'clj'
        elif language=='fsharp':
            extension = 'fs'
        elif language=='groovy':
            extension = 'groovy'
        elif language=='ocaml':
            extension = 'ml'
        elif language=='pascal':
            extension = 'pas'
        elif language=='racket':
            extension = 'rkt'
        elif language=='scheme':
            extension = 'scm'
        elif language=='erlang':
            extension = 'erl'
        elif language=='julia':
            extension = 'jl'
        elif language=='fortran':
            extension = 'f'
        elif language=='nim':
            extension = 'nim'
        elif language=='crystal':
            extension = 'cr'
        elif language=='reason':
            extension = 're'
        elif language=='v':
            extension = 'v'
        elif language=='haxe':
            extension = 'hx'
        elif language=='d':
            extension = 'd'
        elif language=='perl6':
            extension = 'p6'
        elif language=='elm':
            extension = 'elm'
        elif language=='pure':
            extension = 'pure'
        elif language=='julia':
            extension = 'jl'
        elif language=='coffeescript':
            extension = 'coffee'
        elif language=='ocaml':
            extension = 'ml'
        elif language=='perl':
            extension = 'pl'
        elif language=='h':
            extension = 'h'
        elif language=='hpp':
            extension = 'h'
        elif language=='c++':
            extension = 'cpp'
        elif language=='csv':
            extension = 'csv'


        if not filename:
            filename = "outfile." + extension  # Default filename if not provided

        # Strip whitespace and unwanted characters from filename
        filename = filename.strip().replace('/', os.sep)
        # Create full path for the file
        file_path = os.path.join(output_directory, filename)

        # Check if file exists and modify filename accordingly
        # by adding a number in parentheses
        file_counter = 1
        file_base, file_extension = os.path.splitext(file_path)
        while os.path.exists(file_path):
            file_path = f"{file_base}({file_counter}){file_extension}"
            file_counter += 1

        # Create full path for the file
        #file_path = os.path.join(output_directory, filename)

        if content is not None and content!='':
            globals.g_ai_output_saved_last_code_block = content
        #g_ai_output_saved_last_code_block = "["+content+"]"
        with open('DEBUGLOG.txt', 'a', encoding='utf-8') as file1:
            file1.write("\n<CAPTURE1>\n")
            file1.write(content)
            file1.write("</CAPTURE1>\n")
        #    file1.write("\n<CAPTURE2>g_ai_output_saved_last_code_block=\n")
        #    file1.write(globals.g_ai_output_saved_last_code_block)
        #    file1.write("\n</CAPTURE2>\n")

        # Write the content to the file, this is the important stuff like the code we want
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        # Write the content to the filename in append mode and in current directory so e.g. if we are getting XML dictionary for many entries the output arrives in here appended each entry
        # This behaviour needs some fine-tuning/cleaning up etc. but it's a start
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(content)

        ret_created_files.append(file_path)
        #print(f"File created: {file_path}")
    return ret_created_files

