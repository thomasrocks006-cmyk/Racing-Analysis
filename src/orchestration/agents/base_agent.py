"""
Base Agent - Abstract interface for all AI agents.
"""

import logging
from abc import ABC, abstractmethod

from ..types import AgentConfig, Task, TaskResult

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.

    Each agent implementation (GPT-5, Claude, etc.) must implement this interface.
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize agent with configuration.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.name = config.name
        self.logger = logging.getLogger(f"{__name__}.{self.name}")

    @abstractmethod
    async def execute(self, task: Task) -> TaskResult:
        """
        Execute a task.

        Args:
            task: Task to execute

        Returns:
            Task result
        """
        pass

    @abstractmethod
    async def close(self):
        """Close agent connection and clean up resources."""
        pass

    def _build_prompt(self, task: Task) -> str:
        """
        Build prompt from task.

        Args:
            task: Task to build prompt for

        Returns:
            Formatted prompt string
        """
        prompt_parts = [f"Task: {task.description}"]

        if task.task_type:
            prompt_parts.append(f"Type: {task.task_type}")

        if task.context:
            context_str = "\n".join(f"- {k}: {v}" for k, v in task.context.items())
            prompt_parts.append(f"Context:\n{context_str}")

        return "\n\n".join(prompt_parts)

    def _estimate_cost(self, tokens: int) -> float:
        """
        Estimate cost for token usage.

        Args:
            tokens: Number of tokens used

        Returns:
            Estimated cost in USD
        """
        return tokens * self.config.cost_per_token
