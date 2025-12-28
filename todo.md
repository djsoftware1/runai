# runai todo list

* runai — https://github.com/djsoftware1/runai
* (c) David Joffe / DJ Software 2023-2025 - Business Source License (BSL 1.1). See LICENSE


High:
* Issue with CRLF
* Correctly handle different newline cases? E.g. sometimes if replacing in a .cpp 'git diff --stat' shows hundreds of changes but there are only a few ... think it's newline format issues ... but is inconsistent and maybe platform-dependent and filetype-dependent and git setting dependent - see what's going on. Should we rather try detect the file type (eg NL or NL/CR etc.) on file open?

* [done] Refactoring should exclude our own e.g. 'output_files'/'__output_files__'/.output_files_runai folder?

* Idea: feed output from one into next more arbitrarily/easily

* Idea: 'plugins' or 'extensions' type of thing where can do custom configurable 'pre' and 'post' actions? For example after a build we might want to check say compiler error logs and try automatically fix issues someday ... could be either custom scripts or custom AI actions or custom file actions or something else .. should be able to have feedback loops too? e.g. 'fix until builds' or 'implement this todo list'queue
* Todo 'queues'?

* headless / docker run?

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
 