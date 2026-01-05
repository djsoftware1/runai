@rem Copyright (C) David Joffe (and DJ Software) 2023-2026
@rem Helper to runai from anywhere on command line. 
@rem 
@rem Make sure this folder is in your system PATH, then you can run runai from anywhere on command line.
@rem ------------------------------------------------------
@rem This is a small wrapper to call python main.py (purpose as the "runai" shell script but for Windows.)
@rem ------------------------------------------------------
@rem todo check if unicode filenames and paramers supported or if we must do anything special like utf8 settings in .bat files
@rem http://github.com/djsoftware1/runai
@rem -----------------------------------------------------------------------


@rem debug info (commented out for production)
@rem DEBUG @echo path %~dp0
@rem DEBUG @echo arguments %*

@rem Basically we are just a thin wrapper to make it easy to call from anywhere

set "CMD_DIR=%~dp0"
set "ROOT_DIR=%CMD_DIR%\.."
set CMD_DIR="%~$PATH:0"
set cmdpathsearch=%~dp$PATH:0

@echo bin-win/runai.cmd Folder:
@echo cd=%cd%
@echo dp0=%~dp0
@echo fileName=%~nx0
@echo f0 %~f0 %~p0
@echo pathsearch=%~$PATH:0
@rem Do this to work around for-each 
@echo cmdpathsearch=%~dp$PATH:0
@rem  ~$PATH:I   - searches the directories listed in the PATH
@rem environment variable and expands %I to the
@rem fully qualified name of the first one found.
@rem If the environment variable name is not
@rem defined or the file is not found by the
@rem search, then this modifier expands to the
@rem empty string
@echo CmdCmdLine=%CmdCmdLine%
@echo ROOT_DIR=%ROOT_DIR%
@echo CMD_DIR=%CMD_DIR%
@echo running python "%cmdpathsearch%\..\main.py" %*
@rem @pause

@echo off
setlocal

python "%cmdpathsearch%\..\main.py" %*


