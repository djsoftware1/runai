import os
import re
import fnmatch
import autogen

def find_files(directory, pattern):
    """Recursively finds all files in a directory matching the pattern."""
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def grep_file(filename, needle):
    """Searches for a needle in a file and returns line numbers and lines."""
    with open(filename, 'r') as file:
        lines = file.readlines()

    return [(index + 1, line) for index, line in enumerate(lines) if needle in line]

def refactor_code(original_code, task):
    """Sends code to autogen for refactoring and returns the modified code."""
    # Integration with autogen will depend on your setup
    # This is a placeholder for the actual implementation
    # You should replace this with the actual call to autogen
    modified_code = autogen.refactor_code(original_code, task)
    return modified_code

def Refactor(in_folder, wildcard, needle, sTask):
    file_list = find_files(in_folder, wildcard)

    for file_path in file_list:
        occurrences = grep_file(file_path, needle)

        if not occurrences:
            continue  # Skip files without the needle

        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line_num, line_content in occurrences:
            # Refactor code
            modified_code = refactor_code(line_content, sTask)

            # Replace original code with modified code
            lines[line_num - 1] = modified_code

        out_folder = "out_folder"  # Define your output folder
        out_file_path = os.path.join(out_folder, os.path.relpath(file_path, in_folder))
        os.makedirs(os.path.dirname(out_file_path), exist_ok=True)

        # Save the modified file
        with open(out_file_path, 'w') as file:
            file.writelines(lines)

# Example usage
#Refactor("input_folder", "*.cpp", "needle", "Refactor this line to...")
