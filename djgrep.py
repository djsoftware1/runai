# Copyright (C) 2023-2024 David Joffe / DJ Software
import re

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

def grep_multiline(filename, pattern):
    """Searches for a multiline pattern in a file and returns line numbers with matches."""
    # Getting encoding errors reading some files so first try utf8 if that fails try cp1252 etc. - probably have to refine this further
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='cp1252') as file:
            content = file.read()

    # Find all matches of the pattern
    matches = list(re.finditer(pattern, content, re.DOTALL))
    print(f"Found {len(matches)} matches for pattern {pattern} in file {filename}")

    # Determine line numbers for each match
    lines = content.split('\n')
    match_info = []
    for match in matches:
        start_index = match.start()
        line_count = content.count('\n', 0, start_index) + 1
        match_info.append((line_count, match.group()))

    return match_info


"""
The function should:
    1. Expand to a full line if the match is less than one line.
    2. Stay as one line if the match is exactly one line.
    3. Expand to include the beginning and end of lines if the match spans multiple lines.
"""
def grep_multiline2(filename, pattern):
    """Searches for a pattern in a file and returns line numbers with full line matches."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='cp1252') as file:
            content = file.read()

    matches = list(re.finditer(pattern, content, re.DOTALL))
    print(f"Found {len(matches)} matches for pattern '{pattern}' in file {filename}")

    match_info = []
    for match in matches:
        start_index = match.start()
        end_index = match.end()

        # Find the start and end of the line(s)
        line_start = content.rfind('\n', 0, start_index) + 1
        line_end = content.find('\n', end_index)
        line_end = len(content) if line_end == -1 else line_end

        # Adjust if the match is less than a full line
        if content[start_index:line_end].find('\n') == -1:
            # If match is on a single line but doesn't start at the line's beginning
            if content[line_start:start_index].strip() != "":
                # Extend to the full line
                line_start = content.rfind('\n', 0, start_index) + 1
            # If match is on a single line but doesn't end at the line's end
            if content[end_index:line_end].strip() != "":
                # Extend to the full line
                line_end = content.find('\n', end_index)
                line_end = len(content) if line_end == -1 else line_end

        # Extract the full line(s)
        full_line = content[line_start:line_end]
        #debug#print(f"!!!!!!full_line: " + full_line)

        # Determine line numbers
        line_number_start = content.count('\n', 0, start_index) + 1
        line_number_end = content.count('\n', 0, line_end) + 1
        #debug#print(f"!!!!!!line_number_start: {line_number_start}-{line_number_end}")

        match_info.append((line_number_start, full_line, line_number_end - line_number_start + 1))

    return match_info

"""
# Test the function
filename = 'your_file.cpp'
pattern = "tStrAppend\\("
matched_lines = grep_multiline2(filename, pattern)
for match in matched_lines:
    print(match)
"""


"""
# Example usage
pattern = r'/\*.*?\*/'  # Regular expression for C++ block comments
filename = 'example.cpp'
matches = grep_multiline(filename, pattern)
for line_num, match in matches:
    print(f"Match at line {line_num}:")
    print(match)
    print("-----")
"""
