# runai: DJ Software Task Execution and Automation Framework

* [runai homepage](https://djoffe.com/dj-software/runai/)

A kind of integrated 'AI extension' of your terminal or command prompt

General AI/LLM-driven task execution and automation tool for tasks such as code refactoring (or many other tasks, including non-coding-related tasks), supporting AutoGen.

“Any project you’re working on, runai becomes another tool in your terminal.”

**Use also straight from VS Code and Cursor terminal:**

![runai screenshot by David Joffe and icon symbol](https://djoffe.com/dj-software/runai/media/runai_crop_center_logo.png)

**Cross-platform:** Integrates into command-line for Windows command prompt, git bash, Linux, or macOS terminal.

Supports either OpenAI, or your own custom AI instances (for example your own LiteLLM server(s)).

**Example:**

```
runai -t "Write a Python script that can check daily for updated exchange rate for USD, EUR"
```
Use `-t "task"` to specify task to be done.

## Help and Examples - Getting Started

```runai -h``` **Show full main usage help**

```runai --version``` **Show version**

```runai --showsettings``` **Just show settings and exit**

**Example:**
```
runai --gpt4 -t "Repeat the word coffee five times"

runai -t "Repeat the word coffee five times, then help cure aging"
```

### Common settings quick-reference
```
runai -h  show full help  --showsettings  just show settings  --version  show version number  --dryrun 
      -t "TASK"  task instructions for LLM to do  -tf "TaskFile" task file to load (default autotasks.txt)
      -m "MODEL" select model  -p "PROJECT-NAME"  -4 use gpt-4  --o1-mini  --o1-preview
      -f "FOLDER"  set work-folder   subcommands (refactor,build,create,createfrom,modify) ...
      -i "InputFile" to batch-run task on all lines, with substitution. default=input.txt
```
```
USAGE: runai (or python main.py) [taskfile] [targetfolder] [settings.py]
```

You can use "--showsettings" to just check the settings before run! For example:
```
runai --showsettings refactor -w main.py
```

### Subcommands Help

* **create**: Create new file(s) mode: `runai create`

* **refactor**: Refactor existing files mode: `runai refactor`

Use `runai __subcommand__ -h` to show usage help for subcommands (create,refactor,build,createfrom,modify)
```
runai create -h
=> usage: main.py create [-h] [-o OUT [OUT ...]]

runai refactor -h
=> usage: runai refactor [-h] [-r FIND_REGEX] [--find-text FIND_TEXT]
   [-w WILDCARDS [WILDCARDS ...]][--replace-with REPLACE_WITH] [-s SEND [SEND ...]]
```

Try a simple test like this to see if it's working: 
```
runai -4 -t "Hi, can you help me?"
```

### Selecting Model

Options for selecting the model to use:

```
   -m "model" OR --model "model" - use "model"
   -m "ollama/deepseek-r1:8b"
   -m "openai/gpt-4o-mini"
   -m "lmstudio/phi-3"
   -m "gemini/gemini-2.5-flash"
   -m "anthropic/claude-3-haiku"
   -m "xai/grok-3-mini"
   -m "gpt-4.1-mini"
   -m "gpt-4.1-nano"
   -m "gpt-4.1"
   -4 or --gpt4 - use gpt4
   -3 or --gpt3 - use gpt3 (deprecated)
   --o1-mini - use o1-mini
   --o1-preview - use o1-preview
```

**Example:** `runai --openai -t "Write a short story about cats"`

### Project Name

Use --project or -p to specify a project name, which will be used when auto-generating output such as automatically-generated output files and folder name.

```sh
runai -p "coding" -t "Write a C++ vec3d class"

runai -p "Thesis" -t "Help me brainstorm ideas on my thesis research about the following subject: ..."
```

Generated output will be placed under a subfolder of the given project name.

### Selecting Backend

Options for selecting the backend

```
   --openai Use OpenAI backend directly (without AutoGen) for tasks

   --djchat Use djchat/djchatbot backend (without AutoGen) if available
```

#### Testing

```
   --dummy Special 'dummy' backend for testing

   --echo Echo mode: Dummy backend just sends back task string as "result" for testing
```

**Note:** For some tasks, this tool can modify files, so use with caution. Always backup all your data first, work in a 'sandbox' copy, and check all ch ananges. Test things first. Use at own risk.

## License

runai is source-available software licensed under the Business Source License (BSL) 1.1.

Free for personal, educational, research, and evaluation use.
Commercial use requires a separate license.

See the [LICENSE](LICENSE.md) file for details.

## Installation

First, either download runai (as a zip), or clone this GitHub repo: `$ git clone https://github.com/djsoftware1/runai`

Then install requirements (you may use an env, though may be useful to install globally to more easily run "runai" from anywhere on command line):

```
pip install -r requirements.txt
```

To run:

```
$ runai

Or (old way): python main.py
```

If you follow the instructions here to add this to your system PATH, then you can just type "runai" from anywhere. (Otherwise, use "./runai" or a full path to run.)

If using OpenAI, then place your configuration with API key in OAI_CONFIG_LIST


### PATH Setup

runai "works best" if you optionally add to your system PATH - then you can just type "runai" on the command line from any folder to run - potentially very powerful.

On Windows you can use the system Environment Variables dialog to add runai to PATH. (git bash _should_ automatically 'inherit' this for its PATH.)

For Linux/macOS (or also git bash), add a line like this in e.g. your **.bashrc** or zshrc startup file to add it to PATH on bash startup:

``` sh
    export PATH="/c/src/runai:$PATH"
```
(If, for example, you did 'git clone' this project into your, say, "/c/src" folder.)

("runai" is just a small wrapper for 'python main.py'.)



## Simple Test

Try a simple test like this to see if it's working: 
```
    runai -4 -t "Hi, can you help me ?"
```

## Show Settings and Exit

```
runai -c
runai --showsettings

OR e.g. with a task settings:

runai --showsettings refactor -w "*.cpp" "*.h"

runai -t mytask.txt --showsettings refactor -w "*.cpp" "*.h"

# Straight-forward non-AI replace:
runai  refactor -w "main.py" -r "findme" --replace-with "foo"

etc.
```

### Task files and runai.autotask.txt

By default, it looks for a file named "runai.autotask.txt" in the folder you run it, and if found, automatically loads the task from that file.

Or, you can specify a task file with "-tf" or "--taskfile" (or task string with -t).

If no autotask found, and no task or taskfile passed as parameter, it will ask for a task.

## Custom LiteLLM Server:

It is recommended to use a separate Python environment for litellm to avoid dependency issues.

```
# Optional if want to run local AI server:
$ pip install litellm (or: python3 -m pip install litellm)

And possibly also:

$ pip install litellm[proxy]
```

Then e.g. 'ollama pull codellama' and 'litellm --model ollama/codellama'

Some kinds of tasks don't require AI at all, and are just done locally, e.g. a refactor straightforward regex replace.

## Multi-line input replacements

If feeding an input list, you can use "{$1}" in the task string to replace it with the line contents, for example if your input lines are:

```
Vec2d
Vec3d
Matrix4d
```

You can use e.g. "Generate a class called {$1} with implementation" etc.

The special variable "{$line}" can be replaced with the original line number of the input file.

* {$line} Replace with current input line number in task string for multi-line input
* {$date} Replace with current date (UTC) in task string
* {$time} Replace with current time (UTC) in task string
* {$datetime} Replace with current date and time (UTC) in task string (YYYY-MM-DD HH-MM-SS)

## To try force use of GPT3, GPT4, o1-mini or other preferred model:

OpenAI/AutoGen tasks: Provided your OAI_CONFIG_LIST is set up correctly with GPT3 and GPT4 you can use the command-line parameters described above under the 'Help' section to select any preferred model.


Design thoughts on main task types:

## Main Task Types:

1. **Code Generation**
   - Add new code, such as classes, functions, or entire modules.
   - Example: Automatically generate a new Vec3d class in vec3d.h/cpp files.

2. **Code Enhancement**
   - Extend existing files by adding new functionalities, methods, or classes.
   - Implement stubs or abstract methods.
   - Example: Add new methods to an existing class or implement TODOs.

3. **Code Refactoring**
   - Modify existing code to improve structure, performance, readability, or maintainability without changing its external behavior.
   - Example: Refactor specific patterns, optimize algorithms, or update to newer syntax.

```
# Use "--showsetttings" to just check the settings before run
runai --showsettings refactor -w main.py
runai refactor -w src/MyFile.cpp

runai --showsettings refactor -w "*.cpp" "*.h"
runai refactor -w "*.cpp" "*.h"

runai refactor -w src/MyFile.cpp

```

4. **Build and Test Automation**
   - Compile code, run build processes, and execute automated tests.
   - Analyze build logs and test reports for errors or warnings.
   - Example: Run unit tests, integration tests, and analyze results.

5. **Code Analysis and Linting**
   - Perform static code analysis for potential issues.
   - Enforce coding standards and style guides.
   - Example: Run linters and format code according to PEP 8 for Python.

6. **Documentation Generation**
   - Auto-generate documentation from code comments and docstrings.
   - Keep documentation in sync with code changes.
   - Example: Generate API documentation using tools like Doxygen or Sphinx.

7. **Dependency Management**
   - Update or manage external libraries and dependencies.
   - Ensure compatibility and security of dependencies.
   - Example: Update packages to the latest versions while ensuring compatibility.

8. **Version Control Operations**
   - Automate commits, merges, branches, and other version control operations.
   - Handle version tagging and release management.
   - Example: Auto-commit changes after successful tests and linting.

9. **Deployment and Release Automation**
   - Automate the deployment of code to production or staging environments.
   - Manage release cycles and deployment schedules.
   - Example: Automatically deploy code to a staging server after passing CI/CD pipelines.


## Examples

```
    runai -4 -tf /c/runai/tasks/copyright/task.txt -f ./cppcode_folder/ -s /c/runai/tasks/copyright/settings.py refactor -w "*.cpp"
```

## Notes on caching

Note that AutoGen caches results, and sometimes this may cause issues where something appears to not work when it is working. Try remove the cache ('rm -rf .cache') at times and see if that helps.

## About

Multi-purpose automation framework, optionally with AutoGen multi-agents, for AI/LLM and other task automation, created by David Joffe @davidjoffe (beta/early dev)

Other potential names: dj-runAI, or djrun, or perhaps 'dj-run-tasks' (to reflect that not all tasks are AI-based).

## Copyright

This project Copyright (C) David Joffe and [DJ Software](https://djoffe.com/dj-software/) 2023-2026

"**DJ Software**" is just short for "David Joffe Software", and is a name I created to place some of my software under (and of 1. a potential entity, and 2. of this [GitHub organization "djsoftware1" I created for DJ Software](https://github.com/djsoftware1/)).

See also [djoffe.com/dj-software/](https://djoffe.com/dj-software/)

- [David Joffe](https://davidjoffe.github.io/)

