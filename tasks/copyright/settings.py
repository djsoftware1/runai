# Copyright (C) 2023 David Joffe / DJ Software

#refactor_wildcard = ["*.cpp", "*.h"]
refactor_wildcard = "*.cpp"
#refactor_wildcard = "*.h"
refactor_codetype = "cpp"
refactor_wildcards = ["*.cpp", "*.h"]

# Don't change the actual function itself
#refactor_matches = "^[^\n]*Copyright [^\n]*\n"
refactor_matches = "Copyright "
#refactor_multiline_matches = []