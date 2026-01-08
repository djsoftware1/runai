# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2025-2026 - Business Source License (BSL 1.1). See LICENSE
#
# dummy backend to help testing that basically successfully pretends to do the task (so we can test application flow and output and so on) but just immediately returns a success string locally with no real AI (and no token spending ;) involved ...
#
# Note: If my memory is serving me correct, this is the first real code in runai actually first auto-produced by runai itself!
# (Note, not the first time I've used its output to help write code, but the first time the code produced was actually used as-is in runai itself .. I have used the output to start other projects)
# djoffe.com david@MSI MINGW64 /c/runai/run_ai/backends (main)
# $ runai  -t "For my run AI project I hvae generic base class Backend with function do_task(self, task:str), create and give me a Python class in file dummy2.py that acts as a dummy backend for testing that successfully returns some string to help with testing the framework but it basically echos back the string with something indicating like Hey I am the dummy backend and did the following task" create -o dummy2.py

from run_ai.backends.base import Backend

class DummyBackend(Backend):
    def __init__(self, ai_settings):
        super().__init__(ai_settings)        
        print(f"debug:runai-dummy-backend-init")

    def do_task(self, task: str) -> str:
        # dj2026-01 echo mode? return exact task string 'as is'!
        if getattr(self.ai_settings, 'echo_mode', False):
            #[debug?verbose]print(task,end='')
            return task

        teststring="""
Here is sample runai test output to test codeblock extraction:
```cpp
// filename: runai_teststring.cpp
#include <iostream>

int main() {
    std::cout << "runai test. Hello. How can we help cure aging?" << std::endl;
    return 0;
}
```

```
This is a test block to test runai codeblock extraction simple
```

```sh
This is a test block to test runai codeblock extraction sh
```

```md filename=README.md
# This is a runai test readme
Hello readme. Let us help cure aging!
```

```md
# This is a runai test unnamed markdown file

Hello runai. Let us help cure aging!
```

```md  filename  =  spaces_runai.md
# This is a fake runai test markdown file

Hello markdown. Let us help cure aging!
```

```php
This is test PHP codeblock to test codeblock extraction
some stuff here.```
Some text.

```cpp
This is a test block to test runai codeblock extraction
```

```cpp filename=fake_filename.cpp
This is a test block to test runai codeblock extraction
```

```cpp
//fake0.cpp
This is a test block to test runai codeblock extraction 2
```

```cpp
// runai.test.1.cpp
This is a test block to test runai codeblock extraction 3
```

```cpp runai_test2.cpp
This is a test block to test runai codeblock extraction 4
```

```cpp
// filename:    runai_test5.cpp
This is a test block to test runai codeblock extraction 5
```

```cpp
// filename: runai_test5.cpp
This is a test block to test runai codeblock extraction 6
```

```python
// filename: runai_test5.py
This is a test block to test runai codeblock extraction 7
```
End of runai test output.
    """
        #print(teststring)

        newline_char = "\n"
        return f"Hey, I am the dummy backend and did the following task:[{newline_char}{newline_char}'{task}'{newline_char}{newline_char}Codeblock test string:{newline_char}{teststring}"
