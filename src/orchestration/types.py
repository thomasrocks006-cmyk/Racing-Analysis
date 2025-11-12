"""
Type definitions for orchestration system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Union


class TaskType(str, Enum):
    """Types of tasks that can be routed to agents."""

    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    TESTING = "testing"
    REFACTORING = "refactoring"
    RESEARCH = "research"
    DEBUGGING = "debugging"
    DATA_PROCESSING = "data_processing"
    MATH_STATS = "math_stats"
    ARCHITECTURE = "architecture"
    GENERAL = "general"


class TaskStatus(str, Enum):
    """Status of a task in the workflow."""

    PENDING = "pending"
    ROUTING = "routing"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a single executable task."""

    description: str
    task_type: Optional[str] = None
    context: dict = field(default_factory=dict)
    preferred_agent: Optional[str] = None
    assigned_agent: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    task_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "task_type": self.task_type,
            "assigned_agent": self.assigned_agent,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
        }


@dataclass
class TaskResult:
    """Result from executing a task."""

    task: Task
    success: bool
    output: Any
    error: Optional[str] = None
    agent_name: Optional[str] = None
    execution_time: float = 0.0
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task": self.task.to_dict(),
            "success": self.success,
            "output": str(self.output) if self.output else None,
            "error": self.error,
            "agent_name": self.agent_name,
            "execution_time": self.execution_time,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "metadata": self.metadata,
        }


@dataclass
class AgentConfig:
    """Configuration for an AI agent."""

    name: str
    provider: str  # openai, anthropic, google, deepseek
    model: str
    api_key: str
    max_tokens: int = 4096
    temperature: float = 0.7
    capabilities: List[TaskType] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    cost_per_token: float = 0.0
    rate_limit_rpm: Optional[int] = None
    enabled: bool = True


@dataclass
class WorkflowConfig:
    """Configuration for a workflow."""

    name: str
    description: str
    tasks: List[dict]
    parallel: bool = True
    max_concurrent: int = 5
    timeout: int = 300  # seconds
    retry_failed: bool = False
