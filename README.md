## runai: DJ Software Task Execution and Automation Framework

* [runai homepage](https://djoffe.com/dj-software/runai/)

General AI/LLM-driven task execution and automation tool for tasks such as code refactoring (or many other tasks, including non-coding-related tasks), supporting AutoGen.

Cross-platform: Optionally integrates into command-line (with a small amount of setup) on Mac, git bash for Windows, or Linux.

This can be configured to use either OpenAI, or your own custom AI instances (for example your own LiteLLM server(s)).

**Caution:** For some tasks, this can modify files. Always backup all your data first, work in a 'sandbox' copy, and check all changes. Always test first. The author(s) of this software are not liable for any use of this tool.

## Terms of Use

* Not open source.
* Free to use for personal, non-commercial use only. For commercial use and organizations (such as government institutions), a support and licensing fee required.

* [License, EULA and disclaimers](https://github.com/djsoftware1/runai/blob/main/LICENSE.md)

## Installation

To install requirements (you may either do this in an env, or though is more useful to install globally to allow to easily run "runai" anywhere from command line):

```
pip install -r requirements.txt
```

To run:

```
$ runai

Or (old way): python main.py
```

If you follow the instructions here to add this to your system PATH, then you can just type "runai" from anywhere. (Otherwise, use "./runai" or a full path to run.)

Example:
```
$ runai -4 -t "Give me a Python script that can check daily for updated exchange rate for Rand, USD, EUR"
      
-4          (optionally select to try use "gpt-4" model)
-t "TASK"   (pass it a task to run on commandline)
```


If using OpenAI, then place your configuration with API key in OAI_CONFIG_LIST

To set it up to run globally from anywhere on your command-line:

```
$ python3 -m pip install -r requirements.txt
```

### PATH Setup


Works best if you optionally add to your system PATH - then you can just type "runai" on the command line from any folder to run - potentially very powerful.

On Windows you can use the system Environment Variables dialog to add runai to PATH.

For git bash, or Linux/macOS, add a line like this in e.g. your **.bashrc** or zshrc startup file - this will add it to PATH each time one runs bash:

```
    export PATH="/c/src/runai:$PATH"
```
(If, for example, you did 'git clone' this project into your, say, "/c/src" folder.)

("runai" is just a small wrapper for 'python main.py'.) I installed as follows:

1. Pick a folder and 'git clone' the repo into it, e.g.:
1. $ cd /c/src    (this can be anywhere you like on your system)
1. $ git clone https://github.com/djsoftware1/runai       (then pip install -r requirements.txt etc.)
1. $ nano ~/.bashrc (to edit .bashrc startup file, and add a line "**export PATH=$PATH:/c/src/runai**")
1. Do any custom configuration, e.g. set up your OAI_CONFIG_LIST add your OpenAI keys

## Simple Test

Try a simple test like this to see if it's working: 
```
    runai -4 -t "Hi, can you help me ?"
```

## Show Version

```
runai --version
```

## Show Settings and Exit

```
runai --showsettings

OR e.g. with a task settings:

runai --showsettings refactor -w "*.cpp" "*.h"

runai -t mytask.txt --showsettings refactor -w "*.cpp" "*.h"

# Straight-forward non-AI replace:
runai  refactor -w "main.py" -r "findme" --replace-with "foo"

etc.
```

By default automatically looks for 'autotask.txt' in current folder, if not found and not passed as parameter will ask for task.

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

## To try force use of GPT3 or GPT4, or other preferred model:

OpenAI/AutoGen tasks: Provided your OAI_CONFIG_LIST is set up correctly with GPT3 and GPT4 you can use these command-line parameters to select gpt-3 and gpt-4:


```
# runai --gpt3
# runai --gpt4

Other options for selecting your preferred model:

runai -m "MODEL" OR: runai --model "MODEL"
runai --o1-mini
runai --o1-preview
```


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

## License

Commercial/restricted

## Examples

    runai -4 -tf /c/runai/tasks/copyright/task.txt -f ./cppcode_folder/ -s /c/runai/tasks/copyright/settings.py refactor -w "*.cpp"

## About

Multi-purpose automation framework, optionally with AutoGen multi-agents, for AI/LLM and other task automation, created by David Joffe @davidjoffe (beta/early dev)

Other potential names: dj-Run-AI, or perhaps 'dj-run-tasks' (to reflect that not all tasks are AI-based).

## Copyright

This project Copyright (C) David Joffe and [DJ Software](https://djoffe.com/dj-software/) 2023-2025

"**DJ Software**" is just short for "David Joffe Software", and is a name I created to place some of my software under (and of 1. a potential entity, and 2. of this [GitHub organization I created for DJ Software, @djsoftware1](https://github.com/djsoftware1/).

See also [djoffe.com/dj-software/](https://djoffe.com/dj-software/)

- David Joffe
