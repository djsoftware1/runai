# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2023-2025 - Business Source License (BSL 1.1). See LICENSE
#
# runai backend for my own 'chatbot' / 'robot' module (with text to speech functionality allowing voice output) ...
# dj2025-03

import os
from run_ai.backends.base import Backend

import importlib
# todo temp for voice/speech:
import time
# NB: Not all users wil have djchatbot/djchat installed, so we need to check for it
def try_import_backend(name: str):
    try:
        #return importlib.import_module(f"run_ai.backends.{name}_backend")
        return importlib.import_module(f"user_modules.{name}")
    except ImportError:
        return None
djchatbot = try_import_backend("chat.djchatbot")

class djChatBackend(Backend):
    def __init__(self, ai_settings):
        super().__init__(ai_settings)
        self.ai_settings = ai_settings
        self.chatbot = None
        self.profile = None
        self.userconfig=None
        if djchatbot:
            print("have_djchat: CREATING djchatbot backend")
            self.userconfig = djchatbot.djUserConfig()
            self.profile = djchatbot.djAIProfile()
            #self.userconfig.load_config()
            #self.userconfig.load_config(settings.config_path)
            api_key=''
            # Load key from environment variable
            api_key = os.getenv("OPENAI_API_KEY")
            organization=''
            max_tokens=1024
            #ai_base_url=''
            debuglevel=2

            self.userconfig.model = 'gpt-4'
            if len(self.ai_settings.model) > 0:
                self.userconfig.model = self.ai_settings.model
            #self.userconfig.model = ''
            # TODO: Pass in and use user model override

            # todo resolve duplication?
            system_prompt='You are a custom djchatbot backend assistant.',
            print(f"profile.system_prompt:{self.profile.system_prompt}")
            #self.profile.system_prompt = system_prompt

            # todo allow URL override for eg local models
            ai_base_url = 'https://api.openai.com/v1/chat/completions'

            # hmm might get rid of this get_library_path ..
            def get_library_path(app_name='djchat'):
                home = os.path.expanduser('~')
                library_path = os.path.join(home, 'Library', 'Application Support', app_name)
                # Ensure the directory exists
                if not os.path.exists(library_path):
                    os.makedirs(library_path)
                return library_path

            print(f"get_library_path: {get_library_path()}")
            #def dj_get_log_path():
            #return os.path.join(get_library_path(), 'djbot_log.xml')
            
            # where to put log ... user dirs? app dir? run dir? user choice?
            log_path = os.path.join(get_library_path(), 'runai.djchat_log.xml')

            # Create the djchatbot instance
            self.chatbot = djchatbot.djAIChatbot(api_key, organization, ai_base_url, self.userconfig.model, self.profile.system_prompt, max_tokens, self.userconfig, debuglevel, log_path)
        else:
            print("djchat: No djchatbot backend available")

    def do_task(self, task: str) -> str:
        self.error = '' # Reset error message (if there was on previous round)
        if (self.chatbot is None):
            self.error = "djchatbot backend not available"
            return "No djchatbot backend available"
        
        print("[djchat-backend]DEBUG:runai-djchat: do_task")
        # This is where you would implement the logic to perform the task using the djChat backend
        # For now, we'll just return a placeholder response
        response = self.chatbot.send_message(task)
        self.response = response
        #Example RESPONSE: {'id': 'chatcmpl-BGauKYjCABXsiRj7aKG5RBb9Ru2hL', 'object': 'chat.completion', 'created': 1743294820, 'model': 'gpt-4-0613', 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'Hi, Hi, Hi', 'refusal': None, 'annotations': []}, 'logprobs': None, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 16, 'completion_tokens': 6, 'total_tokens': 22, 'prompt_tokens_details': {'cached_tokens': 0, 'audio_tokens': 0}, 'completion_tokens_details': {'reasoning_tokens': 0, 'audio_tokens': 0, 'accepted_prediction_tokens': 0, 'rejected_prediction_tokens': 0}}, 'service_tier': 'default', 'system_fingerprint': None}
        # Example response content: 'Hi, Hi, Hi'
        # Check if we have a valid response first
        if not response:
            self.error = "Null response from djChat backend."
            print(f"djchat:Error: {self.error}")
            return ''
        print(f"LOG:runai-djchat: do_task RESPONSE: {response}")
        # Show typeof response
        print(f"[djchat-backend]DEBUG:runai-djchat: do_task type(response): {type(response)}")
        if 'choices' not in response or len(response['choices']) == 0:
            print("[djchat-backend]DEBUG:runai-djchat: do_task ERROR: No choices in response")
            self.error = 'No choices in response from djChat backend'
            print(f"djchat:Error: {self.error}")
            return ''
        
        # Check if the response has the expected structure
        if 'message' not in response['choices'][0] or 'content' not in response['choices'][0]['message']:
            print("[djchat-backend]DEBUG:runai-djchat: do_task ERROR: Fail to find message in response")
            
            self.error = 'djchat:Fail to find message in response'
            print(f"djchat:Error: {self.error}")

            print("Error: Invalid response format from djChat backend.")
            return ''
                
        ret = response['choices'][0]['message']['content']
        

        # paste-start from chat client - dj2026-01
        bot_message = ret
        #if self.chatbot.sound is not None:
            #self.chatbot.sound.text_to_speech("Hi, my name is Cat girl", -1, '', 'f')#current_config.profile.get_field('preferred_voicetype'))
            #self.chatbot.sound.text_to_speech(ret, -1, '', 'f')#current_config.profile.get_field('preferred_voicetype'))
        #if self.debug_level>=1:
        print("-----------------------------------------------------------")
        print(f"[chat]BOT: {ret}")
        print("-----------------------------------------------------------")
        # CHAT HISTORY
        """
        {"role": "user", "content" : "How are you?"},
        {"role": "assistant", "content" : "I am doing well"},
        {"role": "user", "content" : "What are the top 5 sites in Pretoria?"}]
        """
        # Add the user input and response to the chat history
        # We need a way to keep track of which are user messages and which are the AI's responses
        # Though in future this may be extended to be AI to AI conversations, so keep that in mind
        # We must JSON-escape the messages in the history
        self.chatbot.chat_history.add_message("user", task)#prompt)
        self.chatbot.chat_history.add_message("assistant", bot_message)
        # Function to count the number of words in a string for eg history len stuff and context window size
        def count_words(text):
            # Split the text into words based on spaces
            words = text.split()
            # Return the number of words
            return len(words)

        history_words = count_words(self.chatbot.chat_history.get_context())
        #if self.debug_level>=2:
        #    print(f"[HISTORY-LEN:{history_words} words {len(self.chat_history.get_context())}]")
        #print(self.chat_history.get_context())
        # If the chat history gets longer than N messages trim it
        # Maximum length of chat history
        # todo in future this could try be smarter like us count words and max tokens and context window size to determine how much history to trim
        max_history_len = 20
        # Trim the chat history if it's too long
        self.chatbot.chat_history.trim_history(max_history_len)


        #dt = datetime.datetime.now()
        #formatted_datetime = dt.strftime("%Y-%m-%d %H-%M-%S")
        with open('query.log', 'a', encoding='utf-8', errors="replace") as f:
            f.write(f"<bot>\n{bot_message}\n</bot>\n")
        with open('query.xml', 'a', encoding='utf-8', errors="replace") as f:
            f.write(f"<response>\n{bot_message}\n</response>\n")

        #return response_json
        # paste-end from chat client - dj2026-01




        
        print(f"SUCCESS:runai-djchat: do_task ret: {ret}")

        # Hmm (dj2025-03) not sure about autospeak stuff but on first test, it is working!
        auto_speak = True
        if auto_speak and self.chatbot.sound!=None:
            print("[djchat-backend]DEBUG:auto speak result")
            print(f"result={ret}")
            self.chatbot.sound.text_to_speech(ret, -1, '', 'f')#self.userconfig.lang, self.profile.get_field('preferred_voicetype'))
            # the longer the reply the longer we wait to finish .. that's crude .. more correct is a background daemon.
            # todo low-priority but handle background sound in this mode? process launches and immediately closes ... 
            time.sleep(8)
            # this could do something like 'wait until no playing sounds' in a sleep 1 loop
        else:
            print("[djchat-backend]NO SOUND")
        #f"Task '{task}' executed using djChat backend."
        return ret
    
