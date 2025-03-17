@rem Copyright (C) David Joffe (and DJ Software) 2023-2025
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

@echo running python "%~dp0main.py" %*
python "%~dp0main.py" %*
