# runai todo list

* runai — https://github.com/djsoftware1/runai

(c) David Joffe / DJ Software 2023-2026 - Business Source License (BSL 1.1). See LICENSE

* [Done] task: prefix, project name etc. --ls?
-> files to send

* Personas stuff

# IDEAS

* shorten: task_output_directory/outfiles_final: output_runai/2026-01-01 02-14-53/outfiles_final

* A --ls or some-such to send current folder listing (likewise a basic 'shell mode' type of thing? limited shell mode with restrictions for security (configurable) to help you do things like let it auto figure out what to try to do, say, fix build errors)
* A --chat mode?
* A command-line option or other setting (eg env var) that lets it output the task text just before the AI output, instead of just the AI output, to official stdout for piping/saving etc.
* Ability to customize/change the env var prefix? e.g. a meta-prefix like "RUNAI_PREFIX=DJ_" then it looks for settings under "DJ_MODEL" etc. instead of RUNAI_MODEL etc. for all the env var settings?
* 'Pro' tier etc.
* Add --run-to that corresponds with --start-from, and or --do-line N only so say you have 9 panes in RunAI Studio and want to use 
* Be able to feed tasklists in loops to keep busy (and auto-generate 'what to do next here'? plus review code and auto-generate eg find not yet done todos, bugs, security issues or risks in code, or idea generating for next new fetaure)
* Auto convert to PDF / Word etc. (possibly Pro)
* [mostly done with -a --attach] Add ability to send images and other documents as atachments

----------

## RunAI Studio

* 'Set model globally' that calls set or 'export' RUNAI_MODEL? Plus easy ways to set model etc. per pane
* A $pane1 or $1 type variable (and/or $panename1 etc.?) that lets you send commands centrally like 'runai -tf task$1.txt' or 'task$pane1.txt' or some-such that allows. Likewise could have N tasks like N molecules and use --start-from (and add )
* Custom pane env vars? eg RUNAI_PANE_MODEL1??? or is current sufficient
* aider integration? open interpreter? self operating computer? etc. babygpt?
* Auto stuff like 'build' loops?
* Lexicography loops?
* Longevity demo / example multi-pane
* 'chat with AI' about term?
* build error helper stuff and colors and 'open in'
* Be able to feed tasklists in loops to keep busy (and auto-generate 'what to do next here'? plus review code and auto-generate eg find not yet done todos, bugs, security issues or risks in code, or idea generating for next new feature)

----------

* keep tasklog
say with date?
* runai --history ? or --logs? show tasks

* design -> main functionality could/should move toward being a package or module (with configurable backends) and the main.py terminal integration a thin/thinnish wrapper using thats

* add --clear-cache or --clearcache arg (note if run from anywhere on command line should find correct cache location)


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





## Auto suggested to-sort ideas (some already done):

 ### New Feature Suggestions
1. **Add support for environment variable configuration** - Implement a feature that allows users to set the model and API keys via environment variables for better security.
2. **Implement task logging enhancements** - Create a more structured logging mechanism that saves task inputs, outputs, and timestamps in a consistent format.
3. **Integrate caching for repeated tasks** - Introduce a caching layer to store results of previously executed tasks to speed up execution for identical requests.
4. **User-defined template support for output** - Allow users to define templates for formatting the output files generated from AI tasks.
5. **Support for multiple file types** - Enhance file handling to support types beyond just Python files (like Markdown, HTML, etc.).
6. **Add completion suggestions** - Implement a suggestion mechanism for auto-completing task descriptions based on previous tasks run.
7. **Version control integration** - Automate version control operations (like commits and branch management) post-task execution for clarity in project updates.
8. **Batch processing optimizations** - Introduce an option to process certain tasks in parallel for efficiency.
9. **Error handling enhancements** - Improve error handling with more descriptive logs and suggestions for resolving common issues.
10. **Auto-generate documentation** - Automatically generate a README or documentation file based on the tasks executed and outputs generated.

### Automation Tasks with Aider and Runai
1. **Implement environment variable support** - "Create an environment variable loader function to set model and API keys from environment variables."
2. **Design structured logging** - "Develop a structured logging system for task execution that records inputs, outputs, and timestamps in a CSV format."
3. **Implement caching system** - "Add a mechanism to cache results of previous tasks to skip execution for identical requests."
4. **Create output formatting options** - "Allow users to define output file templates that format AI responses based on user preferences."
5. **Expand file handling to multiple types** - "Enhance file handling to also support Markdown and HTML files in addition to Python files."
6. **Implement task suggestion feature** - "Add a feature that provides completion suggestions for task descriptions based on historical user tasks."
7. **Integrate with Git for version control** - "Automate Git commit and branch creation based on the tasks executed and changes made during task completion."
8. **Optimize for parallel batch processing** - "Refactor the process to allow for parallel execution of batch tasks for improved speed."
9. **Enhance error reporting** - "Implement enhanced error reporting that provides clear logs and possible solutions for common issues."
10. **Auto-generate project documentation** - "Create a feature that generates a documentation file summarizing executed tasks and outputs for user review."

These suggestions focus on enhancing the capability and usability of the current implementation while also addressing potential user needs for improved performance, security, and ease of use.I can help you generate a list of tasks based on common areas of improvement in codebases and features that generally add value. However, I can't directly review specific code or README files. Instead, here's a set of example tasks that you might consider for your project:

1. **Implement Input Validation**: "Add comprehensive input validation for all user inputs in the application to enhance robustness."

2. **Automate Dependency Management**: "Set up a tool to automatically update dependencies and generate alerts for outdated packages."

3. **Add Unit Tests**: "Create unit tests for all major functions to ensure reliability and facilitate future development."

4. **Enhance Documentation**: "Improve the README file with examples of common use cases and installation steps for better user guidance."

5. **Implement Logging**: "Introduce a logging mechanism to capture errors and important events for easier debugging."

6. **Improve Error Handling**: "Refactor the code to implement better error handling strategies that provide user-friendly messages."

7. **Create a CI/CD Pipeline**: "Set up a Continuous Integration/Continuous Deployment pipeline to automate testing and deployment."

8. **Optimize Performance**: "Analyze the code for performance bottlenecks and apply optimizations where necessary."

9. **Introduce Configuration Management**: "Implement a configuration management system to allow the app to be easily configured without code changes."

10. **Review Code for Best Practices**: "Conduct a code review for adherence to best practices and suggest improvements."

11. **Add Feature Flags**: "Introduce feature flags to allow for more flexible deployment of new features."

12. **Implement User Authentication**: "Add a user authentication feature to secure access to the application."

13. **Build a Docker Container**: "Create a Dockerfile to containerize the application for easier deployment."

14. **Add a Dashboard for Monitoring**: "Develop a dashboard that monitors key metrics and logs in real time."

15. **Automate Code Formatting**: "Integrate a code formatting tool to ensure consistent formatting throughout the codebase."

* Do everything dual in djchat-engine and runai?

shell -ls mode list files, folders and limited shell commands

ADD A DELAY BEFORE RUNNING
Vision support
Screenshot processing
-> do more -> ocr

runai "shell mode" where the AI can run commands maybe in a loop ... 

* shell mode: ' maybe it should work like you give the  runai project-related a list of commands it 'may execute' or somesuch ? eg 'ls, cd (with top-level max don't go beyond) , make o  cmake cat' ... ?

ls
cat
head
tail
grep
rg
sed
awk
wc
tree
stat

git status
git diff
git log

make
cmake
ctest
ninja

--readonly

* handle groq? GROQ_API_KEY etc. 
* cloud-related tasks

--batcat
--temperature
maxtokens

* 'Server mode' where e.g. chatGPT can connect? think carefully about design .. probably separate add-on, maybe Pro etc.

Available commands (observe-only):

  pwd                     Show current directory
  ls [path]               List directory contents
  tree [path] [depth]     Show directory tree (limited depth)
  cat <file>              Display file contents
  grep <pattern> [path]   Search text
  stat <path>             Show file metadata
  git status              Show git working tree status
  git diff                Show uncommitted changes

Type 'help <command>' for details.

'debug and verbosity are not the same thing' - todo sort/finalize debug vs verbosity vs dev info etc. for simpler default output



* stress-test exceptions eg 404 type errors, no credit messages etc.
