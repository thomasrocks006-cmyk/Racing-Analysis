"""
Result Aggregator - Combines results from multiple agents.
"""

import logging
from datetime import datetime
from typing import Any

from .types import TaskResult

logger = logging.getLogger(__name__)


class ResultAggregator:
    """
    Aggregates results from multiple task executions.

    Combines outputs, calculates statistics, and formats final results.
    """

    def aggregate(
        self, results: list[TaskResult], workflow_name: str
    ) -> dict[str, Any]:
        """
        Aggregate task results.

        Args:
            results: List of task results
            workflow_name: Name of the workflow

        Returns:
            Aggregated results dictionary
        """
        total_tasks = len(results)
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        # Calculate statistics
        total_time = sum(r.execution_time for r in results)
        total_tokens = sum(r.tokens_used or 0 for r in results)
        total_cost = sum(r.cost or 0.0 for r in results)

        # Group by agent
        agent_stats = self._calculate_agent_stats(results)

        # Build aggregated output
        aggregated = {
            "workflow": workflow_name,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tasks": total_tasks,
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": len(successful) / total_tasks if total_tasks > 0 else 0,
            },
            "performance": {
                "total_execution_time": round(total_time, 2),
                "avg_execution_time": round(total_time / total_tasks, 2)
                if total_tasks > 0
                else 0,
                "total_tokens": total_tokens,
                "total_cost": round(total_cost, 4),
            },
            "agent_stats": agent_stats,
            "results": [r.to_dict() for r in results],
            "errors": [
                {"task_id": r.task.task_id, "agent": r.agent_name, "error": r.error}
                for r in failed
            ],
        }

        # Add convenience fields
        aggregated["success_count"] = len(successful)
        aggregated["failed_count"] = len(failed)
        aggregated["outputs"] = [r.output for r in successful]

        logger.info(
            f"Aggregated {total_tasks} results: "
            f"{len(successful)} successful, {len(failed)} failed"
        )

        return aggregated

    def _calculate_agent_stats(
        self, results: list[TaskResult]
    ) -> dict[str, dict[str, Any]]:
        """
        Calculate statistics per agent.

        Args:
            results: List of task results

        Returns:
            Dictionary of agent statistics
        """
        agent_stats: dict[str, dict[str, Any]] = {}

        for result in results:
            if not result.agent_name:
                continue

            if result.agent_name not in agent_stats:
                agent_stats[result.agent_name] = {
                    "tasks_executed": 0,
                    "successful": 0,
                    "failed": 0,
                    "total_time": 0.0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                }

            stats = agent_stats[result.agent_name]
            stats["tasks_executed"] += 1

            if result.success:
                stats["successful"] += 1
            else:
                stats["failed"] += 1

            stats["total_time"] += result.execution_time
            stats["total_tokens"] += result.tokens_used or 0
            stats["total_cost"] += result.cost or 0.0

        # Calculate averages
        for agent, stats in agent_stats.items():
            if stats["tasks_executed"] > 0:
                stats["avg_time"] = round(
                    stats["total_time"] / stats["tasks_executed"], 2
                )
                stats["success_rate"] = round(
                    stats["successful"] / stats["tasks_executed"], 2
                )

        return agent_stats
