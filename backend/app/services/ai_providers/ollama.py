"""Ollama Llama 3 8B AI Provider."""
import json
import logging

import httpx

from app.config import settings
from app.services.ai_providers.base import BaseAIProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseAIProvider):
    """AI Provider using Ollama with Llama 3 8B, enhanced with good prompts."""

    def __init__(self, model_name: str = None):
        super().__init__(model_name or settings.OLLAMA_MODEL)
        self.base_url = settings.OLLAMA_HOST

    def _generate(self, system_prompt: str, user_prompt: str,
                  temperature: float = 0.9, num_ctx: int = 8192) -> str:
        """Core generation via Ollama HTTP API (sync for Celery)."""
        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "system": system_prompt,
                    "prompt": user_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_ctx": num_ctx,
                        "top_p": 0.95,
                        "repeat_penalty": 1.1,
                    },
                },
            )
            response.raise_for_status()
            return response.json().get("response", "")

    def generate_outline(self, prompt, genre, language, num_chapters,
                         writing_style="contemporary", tone="balanced", pov="third_person") -> dict:
        """Generate outline with Llama 3 — uses structured prompting for 8B model."""
        system = self._get_system_prompt(language, role="outline_generator")

        # Enhanced prompt for smaller model — more explicit structure
        user_prompt = f"""Create a detailed novel outline.

Story concept: {prompt}
Genre: {genre}
Chapters: {num_chapters}
Style: {writing_style}
Tone: {tone}
POV: {pov}
Language: {"Thai" if language == "th" else "English" if language == "en" else "Mixed"}

IMPORTANT: Respond ONLY with valid JSON. No explanation, no markdown.

{{"title": "Novel Title", "synopsis": "2-3 paragraph synopsis", "themes": ["theme1"], "chapters": [{{"number": 1, "title": "Chapter Title", "summary": "What happens", "key_events": ["event1"], "characters_involved": ["char1"], "mood": "mood"}}]}}"""

        result = self._generate(system, user_prompt, temperature=0.7, num_ctx=4096)

        try:
            # Extract JSON
            if "```" in result:
                result = result.split("```")[1].split("```")[0]
                if result.startswith("json"):
                    result = result[4:]
            # Find JSON object
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except (json.JSONDecodeError, IndexError):
            pass

        logger.warning("Ollama: Failed to parse outline JSON")
        return {
            "title": "Untitled Novel",
            "synopsis": prompt,
            "chapters": [
                {"number": i + 1, "title": f"Chapter {i + 1}", "summary": "", "key_events": [], "mood": tone}
                for i in range(num_chapters)
            ],
        }

    def generate_chapter(self, outline, chapter_num, chapter_outline, previous_summaries,
                         language="th", writing_style="contemporary", tone="balanced",
                         pov="third_person", target_length=3000) -> str:
        """Generate chapter with enhanced context injection for 8B model."""
        system = self._get_system_prompt(language, role="chapter_writer",
                                          writing_style=writing_style, tone=tone, pov=pov)

        # Compact context for smaller context window
        context = ""
        if previous_summaries:
            context = "\n\nPrevious chapters summary:\n"
            for s in previous_summaries[-3:]:  # Last 3 only for 8B
                context += f"Ch.{s['chapter']}: {s['summary'][:200]}\n"

        user_prompt = f"""Write chapter {chapter_num} of the novel.

Title: {outline.get('title', 'Untitled')}
Synopsis: {outline.get('synopsis', '')[:500]}

This chapter:
- Title: {chapter_outline.get('title', f'Chapter {chapter_num}')}
- Plot: {chapter_outline.get('summary', '')}
- Key events: {', '.join(chapter_outline.get('key_events', []))}
- Mood: {chapter_outline.get('mood', tone)}
{context}

Instructions:
- Write approximately {target_length} words
- Use {pov} perspective
- Style: {writing_style}, Tone: {tone}
- Start with a compelling hook
- End with intrigue or cliffhanger
- Write ONLY the chapter content, no headers or metadata
- Language: {"Thai" if language == "th" else "English"}"""

        return self._generate(system, user_prompt, temperature=0.9, num_ctx=8192)

    def summarize_chapter(self, content: str, language: str = "th") -> str:
        system = "You are a precise summarizer. Be concise."
        prompt = f"Summarize in 3-4 sentences, focusing on key events and character development:\n\n{content[:2000]}"
        return self._generate(system, prompt, temperature=0.3, num_ctx=4096)

    def rewrite_text(self, text: str, instruction: str, language: str = "th") -> str:
        system = self._get_system_prompt(language, role="editor")
        prompt = f"Rewrite the following text according to this instruction:\n\nOriginal:\n{text}\n\nInstruction: {instruction}"
        return self._generate(system, prompt, temperature=0.9)

    def expand_text(self, text: str, target_length: int, language: str = "th") -> str:
        system = self._get_system_prompt(language, role="editor")
        prompt = f"Expand this text to approximately {target_length} words with more detail, dialogue, and atmosphere:\n\n{text}"
        return self._generate(system, prompt, temperature=1.0)

    def suggest_continuation(self, text: str, language: str = "th") -> str:
        system = self._get_system_prompt(language, role="continuation")
        prompt = f"Continue writing from here (200-300 words):\n\n...{text[-800:]}"
        return self._generate(system, prompt, temperature=1.0, num_ctx=4096)

    def generate_characters(self, prompt: str, genre: str, language: str = "th") -> list:
        system = self._get_system_prompt(language, role="character_designer")
        user_prompt = f"""Create 3-5 characters for a {genre} novel.

Story: {prompt}

Respond ONLY with valid JSON array:
[{{"name": "Name", "age": 25, "role": "protagonist", "appearance": "description", "personality": "traits", "background": "history"}}]"""

        result = self._generate(system, user_prompt, temperature=0.8, num_ctx=4096)
        try:
            start = result.find("[")
            end = result.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except (json.JSONDecodeError, IndexError):
            pass
        return []
