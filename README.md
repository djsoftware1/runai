## DJ Software Task Execution Framework

General AI-driven automation helper framework for tasks like code refactoring (or many other tasks, including non-coding-related tasks) using autogen.

Optionally integrates into command-line (with a small amount of setup) on Mac, git bash for Windows, or Linux.

This can be configured to use either OpenAI, or your own custom AI instances (for example your own LiteLLM server(s)).

To install requirements (you may either do this in an env, or though is more useful to install globally to allow to easily run "runai" anywhere from command line):

```
pip install -r requirements.txt
```

To run:

```
python agent.py
```

If using OpenAI, then place your configuration with API key in OAI_CONFIG_LIST

To set it up to run globally from anywhere on your command-line:

```
# python3 -m pip install -r requirements.txt
```

Works best if you optionally add to system path like so in e.g. your bashrc or zshrc, then you can call it from anywhere with just 'runai':

```
export PATH="/Users/YourUsername/runai:$PATH"
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

```
# Optional if want to run local AI server:
# python3 -m pip install litellm
```

Then e.g. 'ollama pull codellama' and 'litellm --model ollama/codellama'

Some kinds of tasks don't require AI at all, and are just done locally, e.g. a refactor straightforward regex replace.

## Forcing use of GPT3 or GPT4 etc.:

Provided your OAI_CONFIG_LIST is set up correctly with GPT3 and GPT4 you can use:

```
# runai --gpt3
# runai --gpt4
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

This project Copyright (C) David Joffe 2023-2024

