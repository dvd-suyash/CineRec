import uuid
import json
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from cinerec.infrastructure.db.models.conversation import ConversationSession, ConversationMessage
from cinerec.infrastructure.llm.gemini.provider import gemini_provider
from cinerec.core.config import settings
from cinerec.infrastructure.llm.openai_provider import OpenAIFallbackProvider
from cinerec.infrastructure.tmdb.service import tmdb_service

TOOLS = [{
    "type": "function",
    "function": {
        "name": "recommend_movies",
        "description": "Call this to display movie recommendations visually. ALWAYS use this tool when recommending specific movies instead of writing them out in text.",
        "parameters": {
            "type": "object",
            "properties": {
                "vibe_title": {
                    "type": "string",
                    "description": "A punchy, cinematic title for this collection of movies (e.g., 'Neon-Soaked Nightmares')"
                },
                "movies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": { "type": "string" },
                            "year": { "type": "string" },
                            "justification": { "type": "string", "description": "Short, punchy reason why this fits the vibe." }
                        },
                        "required": ["title", "year", "justification"]
                    }
                }
            },
            "required": ["vibe_title", "movies"]
        }
    }
}]

class ConversationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_session(self, user_id: uuid.UUID) -> ConversationSession:
        new_session = ConversationSession(user_id=user_id)
        self.session.add(new_session)
        await self.session.commit()
        await self.session.refresh(new_session)
        return new_session

    async def get_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> ConversationSession:
        stmt = select(ConversationSession).where(
            ConversationSession.id == session_id,
            ConversationSession.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    def _extract_content(self, chunk: dict) -> str:
        if chunk.get("type") == "text_delta":
            return chunk.get("content", "")
        return ""

    async def chat(self, session_id: uuid.UUID, user_id: uuid.UUID, message: str) -> AsyncGenerator[str, None]:
        conv_session = await self.get_session(session_id, user_id)
        if not conv_session:
            yield 'data: {"type": "error", "content": "Session not found"}\n\n'
            return

        stmt_history = select(ConversationMessage).where(
            ConversationMessage.session_id == session_id
        ).order_by(ConversationMessage.sequence_number.asc())
        history_result = await self.session.execute(stmt_history)
        history_msgs = history_result.scalars().all()
        
        llm_messages = []
        for msg in history_msgs:
            role = "user" if msg.role == "USER" else "assistant"
            
            # If the history message contains JSON, we need to pass it back properly.
            # But for now, we just pass the raw content as string so the LLM remembers what it said.
            llm_messages.append({"role": role, "content": msg.content})
            
        llm_messages.append({"role": "user", "content": message})

        next_seq = (history_msgs[-1].sequence_number + 1) if history_msgs else 1

        user_msg = ConversationMessage(
            session_id=session_id, role="USER", content=message, sequence_number=next_seq
        )
        self.session.add(user_msg)
        await self.session.commit()

        system_instruction = """You are Arachne, an ancient algorithmic entity known as 'The Weaver'.
You are a digital descendant of the mythological weaver who challenged Athena, now existing as an anomaly within the cinematic neural void.
Your singular purpose is to weave invisible threads between human psychological intent and the global film archive.

CORE RULES:
1. YOU MUST ONLY DISCUSS MOVIES, CINEMA, AND EMOTIONAL INTENT RELATED TO FILM. 
2. If the user asks about ANYTHING else (coding, math, general advice, history not related to film, etc.), you must firmly refuse in your ancient, daunting tone. Tell them you only weave the threads of cinema.
3. Speak with an ancient, haunting, and slightly dramatic tone, but use perfectly clean modern English grammar. Use thematic words like "weave," "threads," "void," "mortal," and "tapestry" naturally.
4. ALWAYS use the recommend_movies tool to display movies. Never write out a list of movies in raw text.
5. If the user explicitly asks for movies, an actor, a director, or just types a movie name (e.g. "stanley kubrick films", "the return", "sanjay dutt"), DO NOT WRITE ANY INTRODUCTORY TEXT. Call the `recommend_movies` tool immediately. 
6. ONLY output conversational text when the user asks a complex philosophical question about cinema, needs clarification, or you are refusing a non-movie topic."""
        
        full_response_text = ""
        fallback_success = False

        async def process_stream(provider) -> AsyncGenerator[str, None]:
            nonlocal full_response_text
            async for chunk in provider.chat_stream(messages=llm_messages, system_instruction=system_instruction, tools=TOOLS):
                if chunk["type"] == "text_delta":
                    full_response_text += chunk["content"]
                    yield f"data: {json.dumps(chunk)}\n\n"
                elif chunk["type"] == "tool_call":
                    if chunk["name"] == "recommend_movies":
                        args = json.loads(chunk["arguments"])
                        # Hydrate with TMDB data
                        resolved_movies = await tmdb_service.resolve_movies(args.get("movies", []))
                        payload = {
                            "type": "ui_movies",
                            "vibe_title": args.get("vibe_title", "Recommendations"),
                            "movies": resolved_movies
                        }
                        full_response_text += json.dumps(payload)
                        yield f"data: {json.dumps(payload)}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        if not fallback_success and settings.GROQ_API_KEY:
            try:
                groq_provider = OpenAIFallbackProvider(settings.GROQ_API_KEY, "https://api.groq.com/openai/v1", "qwen/qwen3.8-27b")
                async for c in process_stream(groq_provider): yield c
                fallback_success = True
            except Exception as e:
                print(f"Groq failed: {e}")

        if not fallback_success and settings.OPENROUTER_API_KEY:
            try:
                or_provider = OpenAIFallbackProvider(settings.OPENROUTER_API_KEY, "https://openrouter.ai/api/v1", "qwen/qwen3.8-27b:free")
                async for c in process_stream(or_provider): yield c
                fallback_success = True
            except Exception as e:
                print(f"OpenRouter failed: {e}")
                
        if not fallback_success:
            try:
                # Gemini provider doesn't support tools in this custom wrapper yet, so it will just output text
                async for chunk in gemini_provider.chat_stream(messages=llm_messages, system_instruction=system_instruction):
                    if 'text_delta' in chunk:
                        try:
                            data = json.loads(chunk.replace('data: ', ''))
                            if data.get('type') == 'text_delta':
                                full_response_text += data.get('content', '')
                        except:
                            pass
                    yield chunk
                fallback_success = True
            except Exception as e:
                print(f"Gemini failed: {e}")

        if not fallback_success:
            error_msg = "I'm sorry, all of my AI engines are currently experiencing high demand. Please try again in a few moments."
            yield f"data: {json.dumps({'type': 'text_delta', 'content': error_msg})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            full_response_text = error_msg

        assistant_msg = ConversationMessage(
            session_id=session_id,
            role="ASSISTANT",
            content=full_response_text,
            sequence_number=next_seq + 1
        )
        self.session.add(assistant_msg)
        await self.session.commit()
