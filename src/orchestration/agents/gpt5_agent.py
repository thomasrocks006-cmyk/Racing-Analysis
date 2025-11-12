"""
GPT-5 Agent - OpenAI GPT-5 Codex integration.
"""

import time
from typing import Any

from openai import AsyncOpenAI

from ..types import AgentConfig, Task, TaskResult
from .base_agent import BaseAgent


class GPT5Agent(BaseAgent):
    """
    Agent for OpenAI GPT-5 Codex model.

    Strengths:
    - Advanced code generation
    - Complex algorithm implementation
    - Debugging and optimization
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize GPT-5 agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=config.api_key)

        self.logger.info(f"GPT-5 agent initialized: {config.model}")

    async def execute(self, task: Task) -> TaskResult:
        """
        Execute task using GPT-5.

        Args:
            task: Task to execute

        Returns:
            Task result
        """
        self.logger.info(f"Executing task with GPT-5: {task.description[:50]}...")

        start_time = time.time()

        try:
            # Build prompt
            prompt = self._build_prompt(task)

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert coding assistant. "
                        "Provide clear, efficient, and well-documented code.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )

            # Extract result
            output = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
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
                    "finish_reason": response.choices[0].finish_reason,
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
        """Close OpenAI client."""
        await self.client.close()
        self.logger.info("GPT-5 agent closed")
