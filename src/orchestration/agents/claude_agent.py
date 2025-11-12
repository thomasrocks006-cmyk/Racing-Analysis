"""
Claude Agent - Anthropic Claude integration.
"""

import time

from anthropic import AsyncAnthropic

from ..types import AgentConfig, Task, TaskResult
from .base_agent import BaseAgent


class ClaudeAgent(BaseAgent):
    """
    Agent for Anthropic Claude model.

    Strengths:
    - Long context analysis
    - Clear documentation and explanations
    - Architectural design
    - Code review
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize Claude agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Initialize Anthropic client
        self.client = AsyncAnthropic(api_key=config.api_key)

        self.logger.info(f"Claude agent initialized: {config.model}")

    async def execute(self, task: Task) -> TaskResult:
        """
        Execute task using Claude.

        Args:
            task: Task to execute

        Returns:
            Task result
        """
        self.logger.info(f"Executing task with Claude: {task.description[:50]}...")

        start_time = time.time()

        try:
            # Build prompt
            prompt = self._build_prompt(task)

            # Call Anthropic API
            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system="You are an expert software architect and analyst. "
                "Provide thorough, well-reasoned analyses and solutions.",
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract result
            output = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost = self._estimate_cost(tokens_used)

            execution_time = time.time() - start_time

            self.logger.info(
                f"Task completed in {execution_time:.2f}s, "
                f"tokens: {tokens_used}, cost: ${cost:.4f}"
            )

            return TaskResult(
                task=task,
                success=True,
                output=output,
                agent_name=self.name,
                execution_time=execution_time,
                tokens_used=tokens_used,
                cost=cost,
                metadata={
                    "model": self.config.model,
                    "stop_reason": response.stop_reason,
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Task execution failed: {e}")

            return TaskResult(
                task=task,
                success=False,
                output=None,
                error=str(e),
                agent_name=self.name,
                execution_time=execution_time,
            )

    async def close(self):
        """Close Anthropic client."""
        await self.client.close()
        self.logger.info("Claude agent closed")
