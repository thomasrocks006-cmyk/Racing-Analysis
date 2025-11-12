"""
State Manager - Tracks workflow and task states.
"""

import logging
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any

from .types import Task, TaskStatus

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages state for workflows and tasks.

    Tracks workflow progress, task status, and provides query capabilities.
    """

    def __init__(self):
        """Initialize state manager."""
        self.workflows: dict[str, dict[str, Any]] = {}
        self.tasks: dict[str, dict[str, Task]] = defaultdict(dict)

    def create_workflow(self, name: str) -> str:
        """
        Create a new workflow.

        Args:
            name: Workflow name

        Returns:
            Workflow ID
        """
        workflow_id = str(uuid.uuid4())

        self.workflows[workflow_id] = {
            "id": workflow_id,
            "name": name,
            "status": "running",
            "created_at": datetime.now(),
            "completed_at": None,
            "task_count": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
        }

        logger.info(f"Created workflow {name} with ID {workflow_id}")
        return workflow_id

    def register_task(self, workflow_id: str, task: Task):
        """
        Register a task with a workflow.

        Args:
            workflow_id: ID of the workflow
            task: Task to register
        """
        if not task.task_id:
            task.task_id = str(uuid.uuid4())

        self.tasks[workflow_id][task.task_id] = task
        self.workflows[workflow_id]["task_count"] += 1

        logger.debug(f"Registered task {task.task_id} for workflow {workflow_id}")

    def update_task(self, workflow_id: str, task: Task):
        """
        Update task status.

        Args:
            workflow_id: ID of the workflow
            task: Updated task
        """
        if task.task_id in self.tasks[workflow_id]:
            self.tasks[workflow_id][task.task_id] = task

            # Update workflow counters
            if task.status == TaskStatus.COMPLETED:
                self.workflows[workflow_id]["completed_tasks"] += 1
            elif task.status == TaskStatus.FAILED:
                self.workflows[workflow_id]["failed_tasks"] += 1

    def complete_workflow(self, workflow_id: str):
        """
        Mark workflow as completed.

        Args:
            workflow_id: ID of the workflow
        """
        if workflow_id in self.workflows:
            self.workflows[workflow_id]["status"] = "completed"
            self.workflows[workflow_id]["completed_at"] = datetime.now()

            logger.info(f"Workflow {workflow_id} completed")

    def fail_workflow(self, workflow_id: str, error: str):
        """
        Mark workflow as failed.

        Args:
            workflow_id: ID of the workflow
            error: Error message
        """
        if workflow_id in self.workflows:
            self.workflows[workflow_id]["status"] = "failed"
            self.workflows[workflow_id]["error"] = error
            self.workflows[workflow_id]["completed_at"] = datetime.now()

            logger.error(f"Workflow {workflow_id} failed: {error}")

    def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """
        Get status of a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns:
            Workflow status dictionary
        """
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}

        workflow = self.workflows[workflow_id].copy()

        # Add task details
        tasks = []
        for task in self.tasks[workflow_id].values():
            tasks.append(task.to_dict())

        workflow["tasks"] = tasks

        return workflow

    def list_active_workflows(self) -> list[dict[str, Any]]:
        """
        List all active workflows.

        Returns:
            List of active workflow status dictionaries
        """
        return [wf for wf in self.workflows.values() if wf["status"] == "running"]

    def get_task_status(self, workflow_id: str, task_id: str) -> Task | None:
        """
        Get status of a specific task.

        Args:
            workflow_id: ID of the workflow
            task_id: ID of the task

        Returns:
            Task object or None if not found
        """
        return self.tasks[workflow_id].get(task_id)
