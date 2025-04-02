
from settings import djAutoGenSettings

class djAutoGen:
    def __init__(self, settings: djAutoGenSettings):
        self.settings = settings
        print("INIT: Creating AutoGenBackend")
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
        # Initialize the AutoGen settings and objects here
        # This is where you would set up the coder, autogen_coder, assistant, manager, and user_proxy
        # For now, we'll just print a message indicating that the initialization is complete
        print("AutoGen initialized with settings:", self.settings.__dict__)
        
