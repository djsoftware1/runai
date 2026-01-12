# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2023-2026 - Business Source License (BSL 1.1). See LICENSE

# run_ai/cli.py
# command-line interface

# Wrap and call the main main in run_ai/main.py which we now moved from top level - dj2026-01
from .main import main
def entry():
    main()
