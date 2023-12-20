# Copyright (C) 2023 David Joffe / DJ Software
import re
import os
"""
--------------------------------------------------------------------------------
coder (to user_proxy):

```cpp
# filename: djQuaternion.cpp

#include <cmath>
"""

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

    # Regular expression to find code blocks and filenames
    #pattern = r"```(.*?)// filename: (.*?)\n(.*?)```"
    #matches = re.findall(pattern, ai_output, re.DOTALL)
    # Regular expression to find code blocks and filenames (filename is optional)
    #pattern = r"```(.*?)\n(// filename: (.*?)\n)?(.*?)```"
    pattern = r"```(.*?)\n([/#][/#]? filename: (.*?)\n)?(.*?)```"
    matches = re.findall(pattern, ai_output, re.DOTALL)

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Return array of created files (if any) else return empty array
    ret_created_files = []
    for match in matches:
        language, _, filename, content = match
        # Strip whitespace and unwanted characters from filename
        filename = filename.strip().replace('/', os.sep)
        if not filename:
            filename = "outfile.txt"  # Default filename if not provided

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

        # Write the content to the file
        with open(file_path, 'w') as file:
            file.write(content)

        ret_created_files.append(file_path)
        #print(f"File created: {file_path}")
    return ret_created_files

