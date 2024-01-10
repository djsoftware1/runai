High:
* Issue with CRLF
* Correctly handle different newline cases? E.g. sometimes if replacing in a .cpp 'git diff --stat' shows hundreds of changes but there are only a few ... think it's newline format issues ... but is inconsistent and maybe platform-dependent and filetype-dependent and git setting dependent - see what's going on. Should we rather try detect the file type (eg NL or NL/CR etc.) on file open?

* [done] Refactoring should exclude our own e.g. 'output_files'/'__output_files__'/.output_files_runai folder?

* Refactor and other tasks should allow a list of matching regexes or strings
* Refactor should have an option to make a backup somewhere of file content before it modifies it (currently it's advised you run on a copy of your files)

* Better built-in batching of tasks? (Or to what extent can one solve this by consecutive calls to runai?)
* analyze git diff detailed?
* buildtest automated with AI
* allow it to 'browse' -> exec function? [cf. robot building-> same]
* integrate text-to-speech
* integrate speech-to-text for voice command input
* [image]
* Take folder struture as input template for output?
e.g. 'use this folder as basis but create new different project from it'
* 'send' or 'sendfile(s)' command? to send along with task
* non-recursive option for refactor / search and replace
* non-regex option for refactor / search and replace
* customizable 'extension' system for generic 'actions'?
* [claude.ai integration?]
* future/nice-to-have? Option to just directly interface with AIs without autogen if desired
 