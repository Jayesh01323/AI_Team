"""
Base class for all LLM-based engineering stages.

Encapsulates prompt loading, provider selection, generation,
metadata recording, error handling, and context updates.
"""

from abc import abstractmethod
from collections.abc import Callable
from typing import Any

from brain.prompts.loader import load_prompt
from brain.stages.base import Stage
from core.exceptions import ProviderError
from core.logging import get_logger
from models.project_context import ProjectContext
from providers.base import AIProvider
from providers.factory import create_provider

logger = get_logger(__name__)

# Type alias for provider factory function
ProviderFactory = Callable[[], AIProvider]


class LLMStage(Stage):
    """Base class for stages that use an LLM for generation."""

    max_tokens: int = 8192

    def __init__(
        self,
        provider_factory: ProviderFactory | None = None,
        max_tokens: int | None = None,
    ):
        """
        Initialize the LLM stage.

        Args:
            provider_factory: Optional factory function to create AI providers.
                             If None, uses the global create_provider() function.
                             This enables dependency injection for testing.
            max_tokens: Maximum tokens in the response. If None, defaults to self.max_tokens (8192).
        """
        self._provider_factory = provider_factory or create_provider
        if max_tokens is not None:
            self.max_tokens = max_tokens

    @property
    @abstractmethod
    def prompt_template_name(self) -> str:
        """Return the name of the prompt template to use."""
        ...

    @abstractmethod
    def get_prompt_kwargs(self, context: ProjectContext) -> dict[str, Any]:
        """Return the keyword arguments for the prompt template."""
        ...

    @abstractmethod
    def parse_response(self, response_text: str, context: ProjectContext) -> Any:
        """Parse the LLM response text into a structured model."""
        ...

    @abstractmethod
    def update_context(
        self, context: ProjectContext, parsed_output: Any
    ) -> ProjectContext:
        """Update the ProjectContext with the parsed output."""
        ...

    def execute(self, context: ProjectContext) -> ProjectContext:
        """
        Execute the LLM-based stage.

        Loads the prompt, calls the provider, parses the response,
        and updates the context.
        """
        # 1. Load prompt
        kwargs = self.get_prompt_kwargs(context)
        prompt = load_prompt(self.prompt_template_name, **kwargs)

        # 2. Get provider (using injected factory or default)
        provider = self._provider_factory()

        # 3. Start stage (metadata)
        context.start_stage(
            self.name,
            provider_name=provider.name(),
            model=provider.name(),  # Using name as model for now
        )

        try:
            # 4. Generate
            logger.debug(f"Stage '{self.name}' sending prompt to {provider.name()}")
            result = provider.generate(prompt, max_tokens=self.max_tokens)

            # 5. Parse response
            parsed_output = self.parse_response(result.text, context)

            # 6. Update context
            context = self.update_context(context, parsed_output)

            # 7. Complete stage (metadata)
            context.complete_stage(
                self.name,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
            )
            return context

        except Exception as e:
            logger.error(f"LLMStage '{self.name}' failed: {e!s}")
            context.fail_stage(self.name, str(e))
            raise ProviderError(f"Stage '{self.name}' failed: {e!s}") from e

