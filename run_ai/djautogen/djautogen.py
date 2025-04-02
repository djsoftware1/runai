#dj2025-04
import autogen

from .settings import djAutoGenSettings

class djAutoGen:
    def __init__(self, settings: djAutoGenSettings):
        self.settings = settings
        print("djAutoGen: init")
        # these are not settings they are objects created in the backend:
        self.coder = None
        self.autogen_coder = None
        self.assistant = None
        self.manager = None
        self.user_proxy = None

    def InitAutoGen(self):
        """
        Initialize AutoGen settings and objects.
        """
        print("INIT: Creating AutoGenBackend")
        # Initialize the AutoGen settings and objects here
        # This is where you would set up the coder, autogen_coder, assistant, manager, and user_proxy
        # For now, we'll just print a message indicating that the initialization is complete
        print("AutoGen initialized with settings:", self.settings.__dict__)
        #input('debug press a key')
        return

        # create an AssistantAgent named "assistant"
        self.assistant = autogen.AssistantAgent(
            name="assistant",
            llm_config={
                "cache_seed": self.settings.use_cache_seed,  # seed for caching and reproducibility
                #"config_list": config_list,  # a list of OpenAI API configurations
                # above line for OPENAI and this below line for our LOCAL LITE LLM:
                "config_list": config_list_localgeneral,  # a list of OpenAI API configurations
                "temperature": 0,  # temperature for sampling
            },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
        )
        # Create a coder agent
        self.coder = autogen.AssistantAgent(
            name="coder",
            llm_config=llm_config_coder_openai if self.settings.use_openai else llm_config_localcoder
        )
        # create a UserProxyAgent instance named "user_proxy"
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            ########### ollama-testing:
            #llm_config=llm_config_coder_openai if use_openai else llm_config_localcoder,
            #llm_config=llm_config_localgeneral if use_openai else llm_config_localgeneral,
            #code_execution_config=code_execution_enabled,
            max_consecutive_auto_reply=self.settings.max_consecutive_auto_replies,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            #code_execution_config=code_execution_enabled,
            code_execution_config=False,
            #code_execution_config={
            #    "work_dir": "__coding__",
            #    "use_docker": False,  # set to True or image name like "python:3" to use docker
            #},
        )

        """
        if coder_only:
            # the assistant receives a message from the user_proxy, which contains the task description
            #user_proxy.initiate_chat(
            coder.initiate_chat(
                coder,
                message=f"Please do the following task: {task}",
            )
        else:
            # the assistant receives a message from the user_proxy, which contains the task description
            user_proxy.initiate_chat(
                assistant,
                message=f"Please do the following task: {task}",
            )
        """

        if not self.settings.NoGroup:
            print("=== Creating groupchat and manager")
            self.groupchat = autogen.GroupChat(agents=[self.user_proxy, self.coder, self.assistant], messages=[])
            self.manager = autogen.GroupChatManager(groupchat=self.groupchat, llm_config=llm_config_localgeneral)
        else:
            print("=== no groupchat or manager")
            self.groupchat = None
            self.manager = None
        
