"""
GLM Agent - Zhipu AI GLM integration.
"""

import time
from typing import Any, Dict

import aiohttp

from ..types import AgentConfig, Task, TaskResult
from .base_agent import BaseAgent


class GLMAgent(BaseAgent):
    """
    Agent for Zhipu AI GLM model.

    Strengths:
    - Cost-effective Chinese language processing
    - Large context windows (128K)
    - Good for coding tasks and analysis
    - Competitive pricing
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize GLM agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.session = None

        self.logger.info(f"GLM agent initialized: {config.model}")

    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def execute(self, task: Task) -> TaskResult:
        """
        Execute task using GLM.

        Args:
            task: Task to execute

        Returns:
            Task result
        """
        self.logger.info(f"Executing task with GLM: {task.description[:50]}...")

        start_time = time.time()

        try:
            await self._ensure_session()

            # Build OpenAI-compatible request
            payload = {
                "model": self.config.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert software architect and analyst. "
                        "Provide thorough, well-reasoned analyses and solutions.",
                    },
                    {"role": "user", "content": self._build_prompt(task)},
                ],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "stream": False,
            }

            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }

            # Call GLM API
            async with self.session.post(
                self.api_url, json=payload, headers=headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"GLM API error {response.status}: {error_text}")

                result = await response.json()

            # Extract result
            output = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)
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
                    "finish_reason": result["choices"][0].get("finish_reason"),
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
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
        self.logger.info("GLM agent closed")

    def _estimate_cost(self, tokens: int) -> float:
        """
        Estimate cost for GLM tokens.

        GLM pricing (approximate):
        - Input: $0.0005 per 1K tokens
        - Output: $0.001 per 1K tokens
        """
        # Rough estimate - GLM is generally more cost-effective than OpenAI
        return (tokens / 1000) * 0.00075
