"""
Parallel Executor - Executes tasks in parallel with dependency management.
"""

import asyncio
import logging
import time
from typing import Any

from .agent_pool import AgentPool
from .state_manager import StateManager
from .types import Task, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class ParallelExecutor:
    """
    Executes tasks in parallel while respecting dependencies.

    Uses asyncio to run independent tasks concurrently across multiple agents.
    """

    def __init__(self, agent_pool: AgentPool, max_concurrent: int = 5):
        """
        Initialize executor.

        Args:
            agent_pool: Pool of available agents
            max_concurrent: Maximum concurrent tasks
        """
        self.agent_pool = agent_pool
        self.max_concurrent = max_concurrent

    async def execute_parallel(
        self, tasks: list[Task], workflow_id: str, state_manager: StateManager
    ) -> list[TaskResult]:
        """
        Execute tasks in parallel with dependency management.

        Args:
            tasks: List of tasks to execute
            workflow_id: ID of the workflow
            state_manager: State manager for tracking

        Returns:
            List of task results
        """
        results = []
        task_map = {task.task_id: task for task in tasks}
        completed = set()

        # Build dependency graph
        dependency_graph = self._build_dependency_graph(tasks)

        # Execute tasks in waves based on dependencies
        while len(completed) < len(tasks):
            # Find tasks ready to execute (no pending dependencies)
            ready_tasks = [
                task
                for task in tasks
                if task.task_id not in completed
                and all(dep in completed for dep in task.dependencies)
            ]

            if not ready_tasks:
                # Check if we're deadlocked
                if len(completed) < len(tasks):
                    remaining = [t for t in tasks if t.task_id not in completed]
                    logger.error(
                        f"Dependency deadlock detected. "
                        f"Remaining tasks: {[t.task_id for t in remaining]}"
                    )
                break

            # Execute ready tasks in parallel (up to max_concurrent)
            batch_size = min(len(ready_tasks), self.max_concurrent)
            batch = ready_tasks[:batch_size]

            logger.info(
                f"Executing batch of {len(batch)} tasks "
                f"(total ready: {len(ready_tasks)})"
            )

            # Execute batch
            batch_results = await asyncio.gather(
                *[
                    self._execute_task(task, workflow_id, state_manager)
                    for task in batch
                ],
                return_exceptions=True,
            )

            # Process results
            for task, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Task {task.task_id} failed: {result}")
                    result = TaskResult(
                        task=task, success=False, output=None, error=str(result)
                    )

                results.append(result)
                completed.add(task.task_id)

                # Update agent stats
                if result.agent_name:
                    self.agent_pool.update_stats(result.agent_name, result)

        return results

    async def _execute_task(
        self, task: Task, workflow_id: str, state_manager: StateManager
    ) -> TaskResult:
        """
        Execute a single task.

        Args:
            task: Task to execute
            workflow_id: ID of the workflow
            state_manager: State manager

        Returns:
            Task result
        """
        logger.info(f"Executing task {task.task_id} with agent {task.assigned_agent}")

        # Update state
        task.status = TaskStatus.RUNNING
        state_manager.update_task(workflow_id, task)

        start_time = time.time()

        try:
            # Get agent
            agent = self.agent_pool.get_agent(task.assigned_agent)

            # Execute task
            result = await agent.execute(task)
            result.execution_time = time.time() - start_time

            # Update state
            task.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
            state_manager.update_task(workflow_id, task)

            return result

        except Exception as e:
            logger.error(f"Task execution failed: {e}")

            # Update state
            task.status = TaskStatus.FAILED
            state_manager.update_task(workflow_id, task)

            return TaskResult(
                task=task,
                success=False,
                output=None,
                error=str(e),
                agent_name=task.assigned_agent,
                execution_time=time.time() - start_time,
            )

    def _build_dependency_graph(self, tasks: list[Task]) -> dict[str, list[str]]:
        """
        Build dependency graph from tasks.

        Args:
            tasks: List of tasks

        Returns:
            Dictionary mapping task IDs to dependent task IDs
        """
        graph = {}

        for task in tasks:
            if task.task_id:
                graph[task.task_id] = task.dependencies

        return graph
