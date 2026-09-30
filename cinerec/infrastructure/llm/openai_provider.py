import json
from typing import AsyncGenerator
from openai import AsyncOpenAI

class OpenAIFallbackProvider:
    """A generic OpenAI-compatible fallback provider for Groq or OpenRouter."""
    def __init__(self, api_key: str, base_url: str, default_model: str):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=5.0)
        self.default_model = default_model
        
    async def chat_stream(
        self, 
        messages: list[dict], 
        system_instruction: str, 
        model: str | None = None,
        tools: list[dict] | None = None
    ) -> AsyncGenerator[dict, None]:
        
        final_messages = [{"role": "system", "content": system_instruction}] + messages
        
        kwargs = {
            "model": model or self.default_model,
            "messages": final_messages,
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
            
        response = await self.client.chat.completions.create(**kwargs)
        
        tool_call_name = ""
        tool_call_args = ""
        is_tool_call = False
        
        async for chunk in response:
            delta = chunk.choices[0].delta
            
            # If tool calls are starting/streaming
            if delta.tool_calls:
                is_tool_call = True
                tc = delta.tool_calls[0]
                if tc.function.name:
                    tool_call_name += tc.function.name
                if tc.function.arguments:
                    tool_call_args += tc.function.arguments
            elif delta.content and not is_tool_call:
                yield {"type": "text_delta", "content": delta.content}
                
        if is_tool_call:
            yield {"type": "tool_call", "name": tool_call_name, "arguments": tool_call_args}

