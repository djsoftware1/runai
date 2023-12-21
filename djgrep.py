# Copyright (C) 2023 David Joffe / DJ Software
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

def grep_multiline2(filename, pattern):
    """Searches for a pattern in a file and returns line numbers with full line matches."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='cp1252') as file:
            content = file.read()

    #matches = list(re.finditer(pattern, content, re.MULTILINE))
    matches = list(re.finditer(pattern, content, re.DOTALL))
    print(f"Found {len(matches)} matches for pattern '{pattern}' in file {filename}")

    lines = content.split('\n')
    match_info = []
    for match in matches:
        start_index = match.start()
        end_index = match.end()

        # Find the start and end of the line(s)
        line_start = content.rfind('\n', 0, start_index) + 1
        line_end = content.find('\n', end_index)
        line_end = len(content) if line_end == -1 else line_end

        # Extract the full line(s)
        full_line = content[line_start:line_end]

        # Determine line numbers and count of lines matched
        line_number_start = content.count('\n', 0, start_index) + 1
        line_number_end = content.count('\n', 0, end_index) + 1
        num_lines = line_number_end - line_number_start + 1

        match_info.append((line_number_start, full_line, num_lines))

    return match_info


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
