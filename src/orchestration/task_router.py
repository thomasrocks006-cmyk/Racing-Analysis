"""
Task Router - Intelligently routes tasks to optimal agents.
"""

import logging
from typing import Any

from .agent_pool import AgentPool
from .types import Task, TaskType

logger = logging.getLogger(__name__)


class TaskRouter:
    """
    Routes tasks to optimal agents based on task type and agent capabilities.

    Uses a scoring system to select the best agent for each task.
    """

    def __init__(self, agent_pool: AgentPool):
        """
        Initialize task router.

        Args:
            agent_pool: Pool of available agents
        """
        self.agent_pool = agent_pool

        # Task type to agent preference mapping
        self.routing_matrix = {
            TaskType.CODE_GENERATION: {"gpt5": 9, "gemini": 7, "claude": 6},
            TaskType.CODE_REVIEW: {"claude": 10, "gpt5": 7},
            TaskType.DOCUMENTATION: {"claude": 10, "gpt5": 7},
            TaskType.ANALYSIS: {"claude": 10, "deepseek": 8, "gpt5": 7},
            TaskType.TESTING: {"gpt5": 9, "claude": 7},
            TaskType.REFACTORING: {"gpt5": 8, "claude": 8},
            TaskType.RESEARCH: {"claude": 10, "deepseek": 9},
            TaskType.DEBUGGING: {"gpt5": 9, "claude": 7},
            TaskType.DATA_PROCESSING: {"gemini": 8, "gpt5": 7},
            TaskType.MATH_STATS: {"deepseek": 9, "claude": 8},
            TaskType.ARCHITECTURE: {"claude": 10, "gpt5": 7},
        }

    async def route_tasks(self, tasks: list[Task]) -> list[Task]:
        """
        Route multiple tasks to agents.

        Args:
            tasks: List of tasks to route

        Returns:
            List of tasks with assigned agents
        """
        routed = []

        for task in tasks:
            agent_name = await self.route_single_task(task)
            task.assigned_agent = agent_name
            routed.append(task)

        return routed

    async def route_single_task(self, task: Task) -> str:
        """
        Route a single task to the best agent.

        Args:
            task: Task to route

        Returns:
            Name of the selected agent
        """
        # If preferred agent specified and available, use it
        if task.preferred_agent:
            available = self.agent_pool.get_available_agents()
            if task.preferred_agent in available:
                logger.info(f"Using preferred agent {task.preferred_agent} for task")
                return task.preferred_agent

        # Detect task type if not specified
        if not task.task_type:
            task.task_type = self._detect_task_type(task.description)

        # Get agent scores for this task type
        scores = self._get_agent_scores(task.task_type)

        # Select best available agent
        available_agents = self.agent_pool.get_available_agents()
        best_agent = None
        best_score = -1

        for agent, score in scores.items():
            if agent in available_agents and score > best_score:
                best_agent = agent
                best_score = score

        if not best_agent:
            # Fallback to first available agent
            if available_agents:
                best_agent = available_agents[0]
                logger.warning(f"No optimal agent found, using fallback: {best_agent}")
            else:
                raise RuntimeError("No agents available")

        logger.info(
            f"Routed {task.task_type} task to {best_agent} (score: {best_score})"
        )
        return best_agent

    def _detect_task_type(self, description: str) -> TaskType:
        """
        Detect task type from description using keyword matching.

        Args:
            description: Task description

        Returns:
            Detected task type
        """
        desc_lower = description.lower()

        # Keyword patterns for each task type
        patterns = {
            TaskType.CODE_GENERATION: [
                "implement",
                "create",
                "build",
                "generate code",
                "write function",
                "develop",
                "code",
                "algorithm",
            ],
            TaskType.CODE_REVIEW: [
                "review",
                "audit",
                "check",
                "validate",
                "inspect code",
            ],
            TaskType.DOCUMENTATION: [
                "document",
                "write docs",
                "readme",
                "explain",
                "describe",
            ],
            TaskType.ANALYSIS: [
                "analyze",
                "investigate",
                "examine",
                "study",
                "research",
            ],
            TaskType.TESTING: [
                "test",
                "unit test",
                "integration test",
                "pytest",
                "coverage",
            ],
            TaskType.REFACTORING: [
                "refactor",
                "restructure",
                "reorganize",
                "clean up",
                "improve",
            ],
            TaskType.DEBUGGING: ["debug", "fix bug", "troubleshoot", "error", "issue"],
            TaskType.MATH_STATS: [
                "calculate",
                "statistical",
                "mathematical",
                "probability",
                "optimize",
                "algorithm design",
            ],
            TaskType.ARCHITECTURE: [
                "design",
                "architecture",
                "system design",
                "blueprint",
                "structure",
            ],
        }

        # Check each pattern
        for task_type, keywords in patterns.items():
            if any(keyword in desc_lower for keyword in keywords):
                return task_type

        # Default to general
        return TaskType.GENERAL

    def _get_agent_scores(self, task_type: str | TaskType) -> dict[str, int]:
        """
        Get agent scores for a task type.

        Args:
            task_type: Type of task

        Returns:
            Dictionary of agent names to scores
        """
        if isinstance(task_type, str):
            try:
                task_type = TaskType(task_type)
            except ValueError:
                task_type = TaskType.GENERAL

        return self.routing_matrix.get(task_type, {"gpt5": 5, "claude": 5})
