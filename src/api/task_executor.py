"""
Multi-Agent Task Executor
Like GitHub Copilot Chat's multi-agent execution - create a task and agents work simultaneously

Uses OpenAI, Anthropic, or GLM APIs (GitHub Copilot has no REST API for programmatic access)
"""

import concurrent.futures
import json
import time
from dataclasses import dataclass
from datetime import datetime

from .copilot_api import CopilotAgent, GitHubCopilotAPI


@dataclass
class TaskResult:
    """Result from a single agent's task execution."""

    agent_name: str
    success: bool
    output: str
    execution_time: float
    error: str | None = None


@dataclass
class Task:
    """Represents a task that multiple agents can work on."""

    id: str
    description: str
    subtasks: list[dict[str, str]]  # [{"agent": "name", "task": "description"}]
    created_at: datetime
    results: list[TaskResult] | None = None
    synthesis: str | None = None


class TaskExecutor:
    """
    Execute tasks with multiple agents working simultaneously.
    Similar to GitHub Copilot Chat's multi-agent task execution.

    Uses OpenAI, Anthropic, or GLM APIs.
    (GitHub Copilot Pro Plus premium requests are for VS Code chat only, not REST API)
    """

    def __init__(self, provider: str = "openai", max_agents: int = 5):
        """Initialize task executor."""
        self.provider = provider
        self.max_agents = max_agents
        self.tasks: dict[str, Task] = {}
        self.api = GitHubCopilotAPI(provider=provider)

    def create_task(
        self,
        description: str,
        subtasks: list[dict[str, str]] | None = None,
    ) -> Task:
        """
        Create a new task with subtasks for agents.

        Args:
            description: Overall task description
            subtasks: List of {"agent": "AgentName", "task": "What to do"}
                     If None, will auto-decompose the task

        Returns:
            Task object with unique ID

        Example:
            >>> executor = TaskExecutor(provider="openai")
            >>> task = executor.create_task(
            ...     "Build a feature engineering pipeline for racing",
            ...     subtasks=[
            ...         {"agent": "Architect", "task": "Design the pipeline architecture"},
            ...         {"agent": "Developer", "task": "Write the core feature extraction code"},
            ...         {"agent": "Tester", "task": "Create unit tests"},
            ...     ]
            ... )
        """
        task_id = f"task_{int(time.time() * 1000)}"

        # Auto-decompose if subtasks not provided
        if subtasks is None:
            subtasks = self._auto_decompose(description)

        task = Task(
            id=task_id,
            description=description,
            subtasks=subtasks,
            created_at=datetime.now(),
        )

        self.tasks[task_id] = task
        return task

    def _auto_decompose(self, description: str) -> list[dict[str, str]]:
        """Use AI to automatically decompose task into subtasks."""
        prompt = f"""Break down this task into 3-5 subtasks that can be done in parallel:

Task: {description}

Return ONLY a JSON array of objects with "agent" (role name) and "task" (what they should do).
Example: [{{"agent": "Researcher", "task": "Research best practices"}}, ...]
"""

        response = self.api.chat(prompt, temperature=0.3)

        if response.get("success"):
            try:
                # Try to extract JSON from response
                content = response["content"]
                # Find JSON array in response
                start = content.find("[")
                end = content.rfind("]") + 1
                if start >= 0 and end > start:
                    subtasks = json.loads(content[start:end])
                    return subtasks
            except Exception:
                pass

        # Fallback to default decomposition
        return [
            {"agent": "Planner", "task": f"Plan approach for: {description}"},
            {"agent": "Implementer", "task": f"Implement solution for: {description}"},
            {
                "agent": "Reviewer",
                "task": f"Review and suggest improvements for: {description}",
            },
        ]

    def execute_task(self, task: Task, max_concurrent: int | None = None) -> Task:
        """
        Execute task with all agents working simultaneously.

        Args:
            task: Task to execute
            max_concurrent: Max concurrent agents (default: self.max_agents)

        Returns:
            Updated task with results
        """
        max_concurrent = max_concurrent or self.max_agents

        print(f"[TaskExecutor] Executing task: {task.description}")
        print(f"[TaskExecutor] {len(task.subtasks)} agents working simultaneously...")

        # Create agents for each subtask
        agents = []
        for subtask in task.subtasks:
            agent = CopilotAgent(
                name=subtask["agent"],
                system_prompt=f"You are {subtask['agent']}. Focus on your specific task.",
                provider=self.provider,
            )
            agents.append((agent, subtask["task"]))

        # Execute all agents concurrently
        results = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_concurrent
        ) as executor:
            future_to_agent = {
                executor.submit(self._execute_agent, agent, task_desc): (
                    agent.name,
                    task_desc,
                )
                for agent, task_desc in agents
            }

            for future in concurrent.futures.as_completed(future_to_agent):
                agent_name, task_desc = future_to_agent[future]
                try:
                    result = future.result()
                    results.append(result)
                    status = "✅" if result.success else "❌"
                    print(f"  {status} {agent_name}: {result.execution_time:.2f}s")
                except Exception as e:
                    results.append(
                        TaskResult(
                            agent_name=agent_name,
                            success=False,
                            output="",
                            execution_time=0,
                            error=str(e),
                        )
                    )
                    print(f"  ❌ {agent_name}: Failed - {e}")

        task.results = results

        # Synthesize results
        print("[TaskExecutor] Synthesizing agent outputs...")
        task.synthesis = self._synthesize_results(task)

        return task

    def _execute_agent(self, agent: CopilotAgent, task: str) -> TaskResult:
        """Execute a single agent's task."""
        start_time = time.time()

        response = agent.chat(task)
        execution_time = time.time() - start_time

        return TaskResult(
            agent_name=agent.name,
            success=response.get("success", False),
            output=response.get("content", ""),
            execution_time=execution_time,
            error=response.get("message") if not response.get("success") else None,
        )

    def _synthesize_results(self, task: Task) -> str:
        """Synthesize all agent results into final output."""
        # Build synthesis prompt
        prompt = f"Task: {task.description}\n\n"
        prompt += "Agent Outputs:\n\n"

        for result in task.results or []:
            if result.success:
                prompt += f"## {result.agent_name}\n{result.output}\n\n"

        prompt += "\nSynthesize these outputs into a cohesive, actionable result:"

        response = self.api.chat(prompt, temperature=0.5)
        return response.get("content", "Synthesis failed")

    def get_task(self, task_id: str) -> Task | None:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def list_tasks(self) -> list[Task]:
        """List all tasks."""
        return list(self.tasks.values())


# Convenience function for quick task execution
def execute_multi_agent_task(
    description: str,
    subtasks: list[dict[str, str]] | None = None,
    provider: str = "openai",
    max_agents: int = 5,
) -> Task:
    """
    Quick function to create and execute a multi-agent task.

    Uses OpenAI, Anthropic, or GLM APIs (not GitHub Copilot - it has no REST API).

    Args:
        description: Task description
        subtasks: Optional list of {"agent": "name", "task": "description"}
        provider: AI provider ("openai", "anthropic", "glm")
        max_agents: Max concurrent agents

    Returns:
        Completed Task with results and synthesis

    Example:
        >>> task = execute_multi_agent_task(
        ...     "Build a racing model feature pipeline",
        ...     subtasks=[
        ...         {"agent": "FeatureEngineer", "task": "Design feature extraction"},
        ...         {"agent": "DataEngineer", "task": "Design data pipeline"},
        ...         {"agent": "Validator", "task": "Create validation tests"},
        ...     ],
        ...     provider="openai"  # or "anthropic" or "glm"
        ... )
        >>> print(task.synthesis)
    """
    executor = TaskExecutor(provider=provider, max_agents=max_agents)
    task = executor.create_task(description, subtasks)
    return executor.execute_task(task)
