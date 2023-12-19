import re
import os

def create_files_from_ai_output(ai_output, output_directory='output_files'):
    """
    Parses the AI output string for filenames and content, and creates files with that content.

    :param ai_output: String containing the AI output.
    :param output_directory: Directory where files will be created.
    """
    # Regular expression to find code blocks and filenames
    pattern = r"```(.*?)// filename: (.*?)\n(.*?)```"
    matches = re.findall(pattern, ai_output, re.DOTALL)

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for match in matches:
        language, filename, content = match
        # Strip whitespace and unwanted characters from filename
        filename = filename.strip().replace('/', os.sep)

        # Create full path for the file
        file_path = os.path.join(output_directory, filename)

        # Write the content to the file
        with open(file_path, 'w') as file:
            file.write(content)

        print(f"File created: {file_path}")

