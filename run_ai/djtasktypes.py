# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2023-2025 - Business Source License (BSL 1.1). See LICENSE
#
# Main task types

from enum import Enum

class djTaskType(Enum):
    chat = "chat"
    refactor = "refactor"
    create = "create"
    # Edit is current a synonym for modify which feels OK to me for now but think more about it - dj2025
    edit = "edit"
    modify = "modify"
    build = "build"
    #test = "test"
    #deploy = "deploy"
    #monitor = "monitor"
    #delete = "delete" 
