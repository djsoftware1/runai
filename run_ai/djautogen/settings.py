"""
■ runtask.autogen_task.send_files: []
■ runtask.autogen_task.out_files: [] ((? ■ task.modify.send_files: [])
● AutoGen settings:
■ no_autogen_user_proxy: True
■ NoGroup: True  If True do not create autogen GroupChat and GroupChatManager
■ use_cache_seed: 24  random seed for caching and reproducibility
■ code_execution_enabled: False  Enable AutoGen agent code execution [currently always off]
■ coder_only: True
■ max_consecutive_auto_replies: 0
"""

class djAutoGenSettings:
    """
    AutoGen settings:
    """
    def __init__(self):#, system_prompt):
        #self.system_prompt = system_prompt
        self.no_autogen_user_proxy = True
        self.NoGroup = True  # If True do not create autogen GroupChat and GroupChatManager
        self.use_cache_seed = 24  # random seed for caching and reproducibility
        self.code_execution_enabled = False
        self.coder_only = True
        self.max_consecutive_auto_replies = 0

