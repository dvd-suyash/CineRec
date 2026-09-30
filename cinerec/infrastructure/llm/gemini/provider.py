import json
from typing import AsyncGenerator, Optional
from google import genai
from google.genai import types
from cinerec.core.config import settings

class GeminiProvider:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY.get_secret_value())
        self.model = "gemini-1.5-flash"

    async def chat_stream(
        self, 
        messages: list[dict], 
        system_instruction: str, 
    ) -> AsyncGenerator[str, None]:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )

        formatted_contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            formatted_contents.append(
                types.Content(role=role, parts=[types.Part.from_text(msg["content"])])
            )

        response = await self.client.aio.models.generate_content_stream(
            model=self.model,
            contents=formatted_contents,
            config=config
        )
        
        async for chunk in response:
            if chunk.text:
                yield f"data: {json.dumps({'type': 'text_delta', 'content': chunk.text})}\n\n"
        
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

gemini_provider = GeminiProvider()
