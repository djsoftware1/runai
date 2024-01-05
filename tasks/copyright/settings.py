# Copyright (C) 2023-2024 David Joffe / DJ Software

do_refactor = True

#refactor_wildcard = ["*.cpp", "*.h"]
refactor_wildcard = "*.cpp"
#refactor_wildcard = "*.h"
refactor_codetype = "cpp"
refactor_wildcards = ["*.cpp", "*.h", "*.php", "*.py"]
#refactor_wildcards=["*.php"]

# Don't change the actual function itself
#refactor_matches = "^[^\n]*Copyright [^\n]*\n"
refactor_matches = "Copyright "
#refactor_multiline_matches = []
# If already includes latest year don't even send it
refactor_negmatches =["2024"]
