# Copyright (C) 2023 David Joffe / DJ Software

do_refactor=True

refactor_wildcard = "*.cpp"
refactor_wildcards = ["*.cpp", "*.h"]

# todo also snprintf etc.
refactor_codetype = "cpp"
#refactor_matches = "^[ \t]*tStrAppend"
# Some go over multiple lines
refactor_matches = "printf\([^\)]+\);"
refactor_matches = "([^\n]*printf\([^\)\n]+\);\n)+"
# Within small local scopes or function scopes to see:

refactor_wildcards = ["*.cpp", "*.h"]

refactor_matches = "printf\("


refactor_negmatches =["^\s*//", "//.*printf", "//.*printf\("]
