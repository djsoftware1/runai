# Copyright (C) 2023-2025 David Joffe and DJ Software
# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2023-2026 - Business Source License (BSL 1.1). See LICENSE

# Create autogen settings instance ... not 100% sure if ideal and/or correct place so might move again but ok for now .. dj2025
from run_ai.djautogen.settings import djAutoGenSettings

autogen_settings = djAutoGenSettings()

# dj2026-01 see DESIGN-NOTES.md ... todo consolidate and refactor ..

# RunAI settings ... still thinking about what should go where
class djSettings:
    def __init__(self):

        # BACKEND RELATED:

        # system or runai instance related

        # See DESIGN-NOTES.md in-progress thoughts on below: dj2026-01
        #self.user_select_preferred_model = ''
        #self.model = ''
        self.backend = ''

