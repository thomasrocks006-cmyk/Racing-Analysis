"""
Central Coordinator - The Brain of the Orchestration System

GitHub Copilot acts as the coordinator, delegating tasks to specialized agents
and managing the overall workflow.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .agent_pool import AgentPool
from .executor import ParallelExecutor
from .result_aggregator import ResultAggregator
from .state_manager import StateManager
from .task_router import TaskRouter
from .types import Task, TaskResult, WorkflowConfig

logger = logging.getLogger(__name__)


class Coordinator:
    """
    Central orchestration controller.

    Responsibilities:
    - Decompose high-level requests into tasks
    - Route tasks to optimal agents
    - Execute tasks in parallel where possible
    - Aggregate and validate results
    - Maintain workflow state
    """

    def __init__(self, config_path: Optional[Path] = None, log_level: str = "INFO"):
        """
        Initialize coordinator.

        Args:
            config_path: Path to orchestration config (agents.yml)
            log_level: Logging level
        """
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.agent_pool = AgentPool(config_path)
        self.task_router = TaskRouter(self.agent_pool)
        self.executor = ParallelExecutor(self.agent_pool)
        self.state_manager = StateManager()
        self.result_aggregator = ResultAggregator()

        self.logger.info("Coordinator initialized successfully")

    async def execute_workflow(
        self,
        workflow_name: str,
        tasks: List[Union[str, Dict[str, Any]]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a predefined workflow with tasks.

        Args:
            workflow_name: Name of workflow (e.g., 'parallel_feature_implementation')
            tasks: List of task descriptions or task dicts
            context: Additional context for all tasks

        Returns:
            Aggregated results with metadata
        """
        workflow_id = self.state_manager.create_workflow(workflow_name)
        self.logger.info(f"Starting workflow: {workflow_name} (ID: {workflow_id})")

        try:
            # Parse tasks
            task_objects = self._parse_tasks(tasks, context)

            # Route tasks to agents
            routed_tasks = await self.task_router.route_tasks(task_objects)
            self.logger.info(f"Routed {len(routed_tasks)} tasks to agents")

            # Update state
            for task in routed_tasks:
                self.state_manager.register_task(workflow_id, task)

            # Execute tasks in parallel where possible
            results = await self.executor.execute_parallel(
                routed_tasks, workflow_id, self.state_manager
            )

            # Aggregate results
            aggregated = self.result_aggregator.aggregate(results, workflow_name)

            # Mark workflow complete
            self.state_manager.complete_workflow(workflow_id)

            self.logger.info(
                f"Workflow {workflow_name} completed successfully. "
                f"Tasks: {len(results)}, Success: {aggregated['success_count']}"
            )

            return aggregated

        except Exception as e:
            self.logger.error(f"Workflow {workflow_name} failed: {e}")
            self.state_manager.fail_workflow(workflow_id, str(e))
            raise

    async def execute_task(
        self,
        description: str,
        task_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        preferred_agent: Optional[str] = None,
    ) -> TaskResult:
        """
        Execute a single task.

        Args:
            description: Task description
            task_type: Type of task (auto-detected if not provided)
            context: Additional context
            preferred_agent: Force specific agent (optional)

        Returns:
            Task result
        """
        task = Task(
            description=description,
            task_type=task_type,
            context=context or {},
            preferred_agent=preferred_agent,
        )

        # Route to agent
        agent_name = await self.task_router.route_single_task(task)
        task.assigned_agent = agent_name

        # Execute
        agent = self.agent_pool.get_agent(agent_name)
        result = await agent.execute(task)

        return result

    def decompose_request(self, request: str, max_tasks: int = 10) -> List[Task]:
        """
        Decompose a high-level request into executable tasks.

        This is where Copilot's repo understanding shines - it can
        intelligently break down complex requests into specific tasks.

        Args:
            request: High-level user request
            max_tasks: Maximum number of tasks to create

        Returns:
            List of decomposed tasks
        """
        # TODO: Implement intelligent decomposition
        # For now, return a simple single-task breakdown
        return [Task(description=request, task_type="general")]

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a running workflow."""
        return self.state_manager.get_workflow_status(workflow_id)

    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows."""
        return self.state_manager.list_active_workflows()

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics for all agents."""
        return self.agent_pool.get_stats()

    def _parse_tasks(
        self, tasks: List[Union[str, Dict[str, Any]]], context: Optional[Dict[str, Any]]
    ) -> List[Task]:
        """Parse task inputs into Task objects."""
        parsed = []

        for task in tasks:
            if isinstance(task, str):
                parsed.append(Task(description=task, context=context or {}))
            elif isinstance(task, dict):
                parsed.append(
                    Task(
                        description=task.get("description", ""),
                        task_type=task.get("type"),
                        context={**(context or {}), **task.get("context", {})},
                        preferred_agent=task.get("agent"),
                        dependencies=task.get("dependencies", []),
                    )
                )
            else:
                raise ValueError(f"Invalid task type: {type(task)}")

        return parsed

    async def close(self):
        """Clean up resources."""
        await self.agent_pool.close_all()
        self.logger.info("Coordinator closed")
