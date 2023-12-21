# Copyright (C) 2023 David Joffe / DJ Software

#refactor_wildcard = ["*.cpp", "*.h"]
refactor_wildcard = "*.cpp"
#refactor_wildcard = "*.h"
refactor_wildcards = ["*.cpp", "*.h"]

refactor_codetype = "cpp"
#refactor_matches = "^[ \t]*tStrAppend"
refactor_matches = "tStrAppend("
#refactor_matches = "tStrAppend("
#refactor_matches = "{.*tStrAppend.*}"
# Don't change the actual function itself
refactor_negmatches =["void tStrAppend\(", "^\s*//"]
# "^\s*//" means Skip instances in comment lines in this case:
# e.g.
# // tStrAppend("Hello", "World");
#^\s*//

#refactor_matches = " tStrAppend"

# prompts to try: You are a C++ refactoring expert, give code only no explanations. Refactor to not use printf-style formatting tStrAppend just plain string functions in C++:
