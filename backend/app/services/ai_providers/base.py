"""Base AI Provider — Abstract interface for all AI providers."""
from abc import ABC, abstractmethod
from typing import Optional


class BaseAIProvider(ABC):
    """Abstract base class that all AI providers must implement."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name

    @abstractmethod
    def generate_outline(
        self,
        prompt: str,
        genre: str,
        language: str,
        num_chapters: int,
        writing_style: str = "contemporary",
        tone: str = "balanced",
        pov: str = "third_person",
    ) -> dict:
        """Generate a structured novel outline."""
        pass

    @abstractmethod
    def generate_chapter(
        self,
        outline: dict,
        chapter_num: int,
        chapter_outline: dict,
        previous_summaries: list,
        language: str = "th",
        writing_style: str = "contemporary",
        tone: str = "balanced",
        pov: str = "third_person",
        target_length: int = 3000,
    ) -> str:
        """Generate a single chapter's content."""
        pass

    @abstractmethod
    def summarize_chapter(self, content: str, language: str = "th") -> str:
        """Generate a concise summary of a chapter for context management."""
        pass

    @abstractmethod
    def rewrite_text(self, text: str, instruction: str, language: str = "th") -> str:
        """Rewrite selected text based on instruction."""
        pass

    @abstractmethod
    def expand_text(self, text: str, target_length: int, language: str = "th") -> str:
        """Expand text to target length with more detail."""
        pass

    @abstractmethod
    def suggest_continuation(self, text: str, language: str = "th") -> str:
        """Suggest continuation text from where the user stopped."""
        pass

    @abstractmethod
    def generate_characters(self, prompt: str, genre: str, language: str = "th") -> list:
        """Auto-generate character suggestions from novel prompt."""
        pass

    def _get_system_prompt(self, language: str, **kwargs) -> str:
        """Get the system prompt based on language and settings."""
        from app.services.prompt_templates import get_system_prompt
        return get_system_prompt(language, **kwargs)
