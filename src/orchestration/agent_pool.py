"""
Agent Pool - Manages all available AI agents.
"""

import logging
from pathlib import Path
from typing import Any

import yaml

from .agents.base_agent import BaseAgent
from .agents.claude_agent import ClaudeAgent
from .agents.glm_agent import GLMAgent
from .agents.gpt4_agent import GPT4Agent
from .agents.gpt5_agent import GPT5Agent
from .types import AgentConfig

logger = logging.getLogger(__name__)


class AgentPool:
    """
    Manages the pool of available AI agents.

    Responsibilities:
    - Load agent configurations
    - Initialize agent connections
    - Track agent availability and stats
    - Provide agents for task execution
    """

    def __init__(self, config_path: Path | None = None):
        """
        Initialize agent pool.

        Args:
            config_path: Path to agents.yml config file
        """
        self.agents: dict[str, BaseAgent] = {}
        self.configs: dict[str, AgentConfig] = {}
        self.stats: dict[str, dict[str, Any]] = {}

        if config_path is None:
            config_path = Path("configs/orchestration/agents.yml")

        self._load_configs(config_path)
        self._initialize_agents()

        logger.info(f"Agent pool initialized with {len(self.agents)} agents")

    def _load_configs(self, config_path: Path):
        """Load agent configurations from YAML."""
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
            # Load default configs
            self._load_default_configs()
            return

        with open(config_path) as f:
            config_data = yaml.safe_load(f)

        for name, config in config_data.get("agents", {}).items():
            self.configs[name] = AgentConfig(
                name=name,
                provider=config["provider"],
                model=config["model"],
                api_key=config["api_key"],
                max_tokens=config.get("max_tokens", 4096),
                temperature=config.get("temperature", 0.7),
                capabilities=config.get("capabilities", []),
                strengths=config.get("strengths", []),
                weaknesses=config.get("weaknesses", []),
                cost_per_token=config.get("cost_per_token", 0.0),
                rate_limit_rpm=config.get("rate_limit_rpm"),
                enabled=config.get("enabled", True),
            )

            # Initialize stats tracking
            self.stats[name] = {
                "tasks_completed": 0,
                "tasks_failed": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_execution_time": 0.0,
            }

    def _load_default_configs(self):
        """Load default agent configurations."""
        # Default GPT-5 config
        self.configs["gpt5"] = AgentConfig(
            name="gpt5",
            provider="openai",
            model="gpt-4",  # Placeholder
            api_key="",
            max_tokens=4096,
            capabilities=["code_generation", "debugging", "testing"],
            strengths=["coding", "algorithms", "api_integration"],
            enabled=False,  # Disabled until API key provided
        )

        # Default Claude config
        self.configs["claude"] = AgentConfig(
            name="claude",
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            api_key="",
            max_tokens=8192,
            capabilities=["analysis", "documentation", "architecture"],
            strengths=["reasoning", "long_context", "documentation"],
            enabled=False,
        )

        # Default GPT-4 config
        self.configs["gpt4"] = AgentConfig(
            name="gpt4",
            provider="openai",
            model="gpt-4",
            api_key="",
            max_tokens=8192,
            capabilities=["general", "analysis", "reasoning", "research"],
            strengths=["natural_language", "problem_solving", "creative_tasks"],
            enabled=False,
        )

        # Default GLM config
        self.configs["glm"] = AgentConfig(
            name="glm",
            provider="glm",
            model="glm-4-plus",
            api_key="",
            max_tokens=4096,
            capabilities=["code_generation", "analysis", "chinese_language"],
            strengths=["coding", "cost_effective", "large_context"],
            enabled=False,
        )

    def _initialize_agents(self):
        """Initialize agent instances from configs."""
        for name, config in self.configs.items():
            if not config.enabled:
                logger.info(f"Skipping disabled agent: {name}")
                continue

            try:
                if config.provider == "openai":
                    # Use GPT-4 for models starting with gpt-4, otherwise GPT-5
                    if config.model.startswith("gpt-4"):
                        self.agents[name] = GPT4Agent(config)
                    else:
                        self.agents[name] = GPT5Agent(config)
                elif config.provider == "anthropic":
                    self.agents[name] = ClaudeAgent(config)
                elif config.provider == "glm":
                    self.agents[name] = GLMAgent(config)
                # Add more agent types as needed
                else:
                    logger.warning(f"Unknown provider for {name}: {config.provider}")

            except Exception as e:
                logger.error(f"Failed to initialize agent {name}: {e}")

    def get_agent(self, name: str) -> BaseAgent:
        """Get an agent by name."""
        if name not in self.agents:
            raise ValueError(f"Agent not found: {name}")
        return self.agents[name]

    def get_available_agents(self) -> list[str]:
        """Get list of available agent names."""
        return list(self.agents.keys())

    def get_agents_by_capability(self, capability: str) -> list[str]:
        """Get agents that have a specific capability."""
        return [
            name
            for name, config in self.configs.items()
            if capability in config.capabilities and name in self.agents
        ]

    def update_stats(self, agent_name: str, result: Any):
        """Update statistics for an agent after task completion."""
        if agent_name not in self.stats:
            return

        stats = self.stats[agent_name]

        if result.success:
            stats["tasks_completed"] += 1
        else:
            stats["tasks_failed"] += 1

        if result.tokens_used:
            stats["total_tokens"] += result.tokens_used

        if result.cost:
            stats["total_cost"] += result.cost

        # Update average execution time
        total_tasks = stats["tasks_completed"] + stats["tasks_failed"]
        current_avg = stats["avg_execution_time"]
        stats["avg_execution_time"] = (
            current_avg * (total_tasks - 1) + result.execution_time
        ) / total_tasks

    def get_stats(self) -> dict[str, Any]:
        """Get statistics for all agents."""
        return {
            "agents": self.stats,
            "total_agents": len(self.agents),
            "enabled_agents": sum(1 for c in self.configs.values() if c.enabled),
        }

    async def close_all(self):
        """Close all agent connections."""
        for agent in self.agents.values():
            try:
                await agent.close()
            except Exception as e:
                logger.error(f"Error closing agent: {e}")
