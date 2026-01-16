# runai — https://github.com/djsoftware1/runai
# (c) David Joffe / DJ Software 2025-2026 - Business Source License (BSL 1.1). See LICENSE
#
# runai OpenAI Backend class - directly send task to OpenAI backend.
# (This is not to be confused with the OpenAI under AutoGen backend options.)
# dj2025-03

from run_ai.backends.base import Backend
#import openai
from colorama import Fore, Style

from openai import OpenAI

class OpenAIBackend(Backend):
    def __init__(self, ai_settings):
        super().__init__(ai_settings)
        if len(self.ai_settings.model) == 0:
            self.ai_settings.model = 'gpt-4o-mini'
            #print(f"DEBUG[runai:OAI] model not set, using default: {self.ai_settings.model}")
        #print(f"DEBUG[runai:OAI] {ai_settings.model} {ai_settings.model_spec}")

        if self.ai_settings.model_spec:
            self.client = OpenAI(
                base_url=self.ai_settings.model_spec["base_url"],
                api_key=self.ai_settings.model_spec["api_key"],
            )
            model = self.ai_settings.model_spec.get("model")
            if model:
                self.ai_settings.model = model
        else:
            # fallback: legacy/default behavior
            self.client = OpenAI()

    def _build_responses_input(self, task: str):
        """
        Build OpenAI Responses API input supporting attachments.

        Returns either:
          - a string (legacy)
          - or a list of input items (multimodal)
        """
        attachments = getattr(self.ai_settings, "attachments", None) or []
        if not attachments:
            return task

        content = []
        # Primary user text
        if task and len(task) > 0:
            content.append({"type": "input_text", "text": task})

        # Attachments
        for a in attachments:
            kind = a.get("kind")
            mime_type = a.get("mime_type") or "application/octet-stream"
            filename = a.get("filename") or "attachment"
            data_b64 = a.get("data_base64")

            if not data_b64:
                continue

            if kind == "image":
                # OpenAI Responses API expects a data URL for base64 images
                data_url = f"data:{mime_type};base64,{data_b64}"
                content.append({
                    "type": "input_image",
                    "image_url": data_url
                })
            else:
                # Although curently ollama does not seem to support file, I assume there is a good chance it might in future ... this might 'automatically' then start working on ollama etc.. ..
                """
                The real rule (undocumented but enforced)
                For documents:
                You must upload the file first, then reference it by file_id.
                Inline base64 works for:
                images
                audio (certain models)
                It does not work for PDFs
                NB NB NB: Files accumulate! todo still
                """
                uploaded = self.client.files.create(
                    file=open(filename, "rb"),
                    purpose="assistants"   # still used by Responses internally
                )
                file_id = uploaded.id


                # show files uploaded ... need a way to delete (todo)
                files = self.client.files.list()
                print(f"NUMBER OF FILES: {len(files.data)}")
                for f in files.data:
                    print("!! FILE:")
                    print(f.id, f.filename, f.bytes, f.created_at)


                # Generic file attachment (PDF/Word/etc.)
                # Note: model support varies; this at least sends the bytes in a standard way.
                content.append({
                    "type": "input_file",
                    "file_id": file_id
                    #"file_data": data_b64,
                    #"filename": filename
                })

        return [
            {
                "role": "user",
                "content": content
            }
        ]

    def do_task(self, task: str) -> str:
        # Implement the logic to interact with OpenAI API
        #print(f"BACKEND[OAI]:do_task: MODEL {self.ai_settings.model} SPEC {self.ai_settings.model_spec}")
        if len(self.ai_settings.model) == 0:
            self.ai_settings.model = 'gpt-4o-mini'
            print(f"do_task: OpenAI model not set, using default: {self.ai_settings.model}")
        model = self.ai_settings.model
        # The message "OpenAI model" is confusing if you are using say "ollama/deepseek-1:8b"
        # it just means OpenAI BACKEND which can work local ollama etc.
        print(f"[OAI-backend] MODEL:{self.ai_settings.model} task:{task}")

        # --- tool selection (CRITICAL PART) ---
        # some tools require ... without this we get an error if we get "Error code: 400 - {'error': {'message': "Deep research models require at least one of 'web_search_preview', 'mcp', or 'file_search' tools."
        # todo later make 'tools selection' more user configurable so it can be customized better per task .. 
        tools = None
        if model == "o3-deep-research":
            tools = [
                {
                    "type": "web_search_preview"
                }
            ]        
        input_payload = self._build_responses_input(task)

        # Call the OpenAI API with the task
        response = self.client.responses.create(
            model=model,#"gpt-4o",#todo model
            input=input_payload,
            tools=tools
        )
        self.response = response.output_text
        # This was saying "OpenAI response" but that's confusing if we using this OpenAI but with local backend like "ollama/deepseek-r1:8b"
        print(f"{Style.DIM}{model} response:{response}{Style.RESET_ALL}")
        print(response.output_text)
        return response.output_text
