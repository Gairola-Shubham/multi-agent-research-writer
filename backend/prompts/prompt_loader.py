import os
from typing import Any, Dict, Optional


class PromptError(Exception):
    """Base exception for prompt-related errors."""

    pass


class PromptNotFoundError(PromptError):
    """Raised when a prompt file cannot be found."""

    pass


class PromptLoader:
    """Utility to load, cache, and format external prompts."""

    def __init__(self, prompt_dir: Optional[str] = None):
        if prompt_dir is None:
            # Default to the directory where this file resides
            self.prompt_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.prompt_dir = os.path.abspath(prompt_dir)

        self._cache: Dict[str, str] = {}

    def get_raw_prompt(self, name: str) -> str:
        """Load a raw prompt from a file and cache it.

        Args:
            name: The name of the prompt (e.g., 'planner' or 'planner.md').

        Returns:
            The raw string content of the prompt file.

        Raises:
            PromptNotFoundError: If the file does not exist.
            PromptError: If the file cannot be read.
        """
        # Ensure we look for a .md extension
        if not name.endswith(".md"):
            filename = f"{name}.md"
            cache_key = name
        else:
            filename = name
            cache_key = name[:-3]

        if cache_key in self._cache:
            return self._cache[cache_key]

        path = os.path.join(self.prompt_dir, filename)
        if not os.path.exists(path):
            raise PromptNotFoundError(f"Prompt file not found at: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self._cache[cache_key] = content
            return content
        except Exception as e:
            raise PromptError(f"Failed to read prompt file at {path}: {e}") from e

    def load(self, name: str, **kwargs: Any) -> str:
        """Load a prompt and format it using Python's format().

        Args:
            name: The name of the prompt.
            **kwargs: Placeholders to format the prompt.

        Returns:
            The formatted prompt string.

        Raises:
            PromptNotFoundError: If the file does not exist.
            PromptError: If formatting fails.
        """
        raw_prompt = self.get_raw_prompt(name)
        if not kwargs:
            return raw_prompt
        try:
            return raw_prompt.format(**kwargs)
        except KeyError as e:
            raise PromptError(
                f"Missing required format placeholder for prompt '{name}': {e}"
            ) from e
        except ValueError as e:
            raise PromptError(f"Error formatting prompt '{name}': {e}") from e

    def clear_cache(self) -> None:
        """Clear the prompt cache."""
        self._cache.clear()


# Optional is imported at the top

# Singleton instance of PromptLoader pointing to the prompts folder
prompt_loader = PromptLoader()


def load_prompt(name: str, **kwargs: Any) -> str:
    """Convenience function to load and format a prompt."""
    return prompt_loader.load(name, **kwargs)
