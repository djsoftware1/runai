# runai Gemini Backend class
#
# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2025-2026 - Business Source License (BSL 1.1). See LICENSE
#
# run_ai/backends/gemini.py
# dj2026-01


# dj2026-01 Although Gemini is 'OpenAI-compatible' it works a bit differently and uses this specific URL currently ..
# so we create a GeminiBackend even though it itself uses the OpenAIBackend

from run_ai.backends.base import Backend
from colorama import Fore, Style
from openai import OpenAI
import os

# I'm not 100% sure if it's better to derive from our openai backend or just have a new clean backend that uses the openAI api directly here but differently ..
# I think the latter is cleaner and less likely to lead to unexpected side effects, though may be a bit more work to implement additional things it's probably better.

class GeminiBackend(Backend):
    def __init__(self, ai_settings):
        super().__init__(ai_settings)
        
        # Set a sensible default if none provided
        if not self.ai_settings.model or len(self.ai_settings.model) == 0:
            self.ai_settings.model = 'gemini-2.5-flash'

        if self.ai_settings.model_spec:
            # Clean the model name (remove 'gemini/' prefix if present)
            if "/" in self.ai_settings.model:
                self.ai_settings.model = self.ai_settings.model.split("/")[-1]

            self.client = OpenAI(
                # Use v1beta path for the OpenAI-compatible layer
                base_url=self.ai_settings.model_spec.get("base_url", "https://generativelanguage.googleapis.com/v1beta/openai/"),
                api_key=self.ai_settings.model_spec.get("api_key", os.getenv("GEMINI_API_KEY")),
            )
        else:
            # Fallback using standard env vars
            self.client = OpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=os.getenv("GEMINI_API_KEY")
            )

    def _build_responses_input(self, task: str):
        attachments = getattr(self.ai_settings, "attachments", None) or []
        
        # If no attachments, just return a simple message list
        if not attachments:
            return [{"role": "user", "content": task}]

        content = []
        if task:
            content.append({"type": "text", "text": task}) # 'text', not 'input_text'

        for a in attachments:
            kind = a.get("kind")
            data_b64 = a.get("data_base64")
            if not data_b64: continue

            if kind == "image":
                mime_type = a.get("mime_type") or "image/jpeg"
                content.append({
                    "type": "image_url", # 'image_url', not 'input_image'
                    "image_url": {"url": f"data:{mime_type};base64,{data_b64}"}
                })
            else:
                # Standard OpenAI Chat doesn't support 'input_file' blocks.
                # For Gemini compatibility, you might need to handle 
                # document text extraction here or omit it.
                pass

        return [{"role": "user", "content": content}]
    
    
    """
    def _build_responses_input(self, task: str):
        attachments = getattr(self.ai_settings, "attachments", None) or []
        if not attachments:
            return task

        content = []
        if task and len(task) > 0:
            content.append({"type": "input_text", "text": task})

        for a in attachments:
            kind = a.get("kind")
            mime_type = a.get("mime_type") or "application/octet-stream"
            filename = a.get("filename") or "attachment"
            data_b64 = a.get("data_base64")
            if not data_b64:
                continue

            if kind == "image":
                data_url = f"data:{mime_type};base64,{data_b64}"
                content.append({
                    "type": "input_image",
                    "image_url": data_url
                })
            else:
                content.append({
                    "type": "input_file",
                    "filename": filename,
                    "file_data": data_b64
                    #"mime_type": mime_type
                })

        return [
            {
                "role": "user",
                "content": content
            }
        ]
    """
    
    def do_task(self, task: str) -> str:
        model = self.ai_settings.model
        print(f"[Gemini-Backend] MODEL:{model} task:{task}")

        try:
            # Change 'input' to 'messages'
            messages = self._build_responses_input(task)

            # Use the standard Chat Completions API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages, # Changed from input=input_payload
            )

            # Access the content via choices[0].message.content
            output_text = response.choices[0].message.content
            
            print(f"{Style.DIM}{model} response: {output_text}{Style.RESET_ALL}")
            return output_text

        except Exception as e:
            error_msg = f"Error in GeminiBackend: {str(e)}"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
            return error_msg
    
    """
    def do_task(self, task: str) -> str:
        model = self.ai_settings.model
        print(f"[Gemini-Backend] MODEL:{model} task:{task}")

        tools = None
        
        try:
            input_payload = self._build_responses_input(task)

            # Use Responses API for consistency with OpenAIBackend and to support attachments
            response = self.client.responses.create(
                model=model,
                input=input_payload,
                tools=tools
            )

            output_text = response.output_text
            
            # Print for debug/visibility in CLI
            print(f"{Style.DIM}{model} response: {output_text}{Style.RESET_ALL}")
            
            return output_text

        except Exception as e:
            error_msg = f"Error in GeminiBackend: {str(e)}"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
            return error_msg
    """
