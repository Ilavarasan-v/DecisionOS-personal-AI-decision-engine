from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """
    Base interface for AI reasoning providers.

    Concrete providers such as OpenAI, Gemini, and Groq
    will implement this interface.
    """

    @abstractmethod
    def generate_explanation(
        self,
        decision_context: dict[str, Any],
    ) -> str:
        """
        Generate a human-readable explanation for a decision.
        """
        raise NotImplementedError