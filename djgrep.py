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
