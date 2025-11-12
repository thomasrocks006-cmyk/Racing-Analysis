"""GitHub Copilot API Wrapper for programmatic access to premium requests.

Note: This requires the GitHub Copilot extension to be active in VS Code.
It uses the Continue extension's API which provides unified access to multiple AI models.
"""

import concurrent.futures
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class GitHubCopilotAPI:
    """Client for GitHub Copilot API.

    Uses Continue extension (already configured) or direct OpenAI/Anthropic APIs.
    This provides the same multi-model access using your existing setup.
    """

    def __init__(
        self,
        provider: str = "openai",  # "openai", "anthropic", "glm"
        model: str | None = None,
    ):
        """Initialize API client with specified provider."""
        self.provider = provider

        # Set default models and get API keys
        if provider == "openai":
            self.model = model or "gpt-4o"  # GPT-4o (latest with vision)
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.api_url = "https://api.openai.com/v1/chat/completions"
        elif provider == "anthropic":
            self.model = model or "claude-sonnet-4-5"
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            self.api_url = "https://api.anthropic.com/v1/messages"
        elif provider == "glm":
            self.model = model or "glm-4-plus"
            self.api_key = os.getenv("GLM_API_KEY")
            self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def chat(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Send a chat request to the AI provider."""
        if not self.api_key:
            return {
                "success": False,
                "error": "missing_api_key",
                "message": f"API key for {self.provider} not found in environment",
            }

        try:
            if self.provider == "anthropic":
                return self._chat_anthropic(
                    prompt, system_prompt, temperature, max_tokens
                )
            else:
                return self._chat_openai_compatible(
                    prompt, system_prompt, temperature, max_tokens
                )

        except requests.ConnectionError:
            return {
                "success": False,
                "error": "connection_error",
                "message": f"Could not connect to {self.provider} API",
            }
        except requests.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            return {
                "success": False,
                "error": error_data.get("error", {}).get("type", "http_error"),
                "message": error_data.get("error", {}).get("message", str(e)),
                "status_code": e.response.status_code,
            }
        except Exception as e:
            return {"success": False, "error": "unknown_error", "message": str(e)}

    def _chat_openai_compatible(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int | None,
    ) -> dict[str, Any]:
        """Handle OpenAI-compatible APIs (OpenAI, GLM)."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(
            self.api_url, json=payload, headers=headers, timeout=60
        )
        response.raise_for_status()
        data = response.json()

        return {
            "success": True,
            "content": data["choices"][0]["message"]["content"],
            "model": data["model"],
            "provider": self.provider,
        }

    def _chat_anthropic(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int | None,
    ) -> dict[str, Any]:
        """Handle Anthropic API."""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens or 4096,
        }
        if system_prompt:
            payload["system"] = system_prompt

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        response = requests.post(
            self.api_url, json=payload, headers=headers, timeout=60
        )
        response.raise_for_status()
        data = response.json()

        return {
            "success": True,
            "content": data["content"][0]["text"],
            "model": data["model"],
            "provider": self.provider,
        }

    def list_models(self) -> dict[str, Any]:
        """List available models for current provider."""
        models = {
            "openai": ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            "anthropic": ["claude-sonnet-4-5", "claude-3-haiku-20240307"],
            "glm": ["glm-4-plus", "glm-4-air"],
        }
        return {
            "provider": self.provider,
            "models": models.get(self.provider, []),
        }

    def health_check(self) -> bool:
        """Check if API key is configured."""
        return self.api_key is not None


class CopilotAgent:
    """Represents a single AI agent with specific role."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        provider: str = "openai",
        model: str | None = None,
    ):
        """Initialize agent with specific role."""
        self.name = name
        self.system_prompt = system_prompt
        self.api = GitHubCopilotAPI(provider=provider, model=model)
        self.conversation_history: list[dict[str, str]] = []

    def chat(self, message: str) -> dict[str, Any]:
        """Send message to this agent."""
        response = self.api.chat(prompt=message, system_prompt=self.system_prompt)

        self.conversation_history.append({"role": "user", "content": message})

        if response.get("success"):
            self.conversation_history.append(
                {"role": "assistant", "content": response.get("content", "")}
            )

        return response

    def reset(self):
        """Clear conversation history."""
        self.conversation_history = []


class MultiAgent:
    """Manages multiple Copilot agents for collaborative analysis."""

    def __init__(self, agents: list[CopilotAgent]):
        """Initialize multi-agent system."""
        self.agents = agents

    def analyze(self, query: str, max_concurrent: int = 3) -> dict[str, dict[str, Any]]:
        """Send query to all agents concurrently."""
        results = {}

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_concurrent
        ) as executor:
            future_to_agent = {
                executor.submit(agent.chat, query): agent for agent in self.agents
            }

            for future in concurrent.futures.as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    response = future.result()
                    results[agent.name] = response
                except Exception as e:
                    results[agent.name] = {
                        "success": False,
                        "error": "execution_error",
                        "message": str(e),
                    }

        return results

    def synthesize(
        self, query: str, analysis_results: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """Use first agent to synthesize results from all agents."""
        if not self.agents:
            return {"success": False, "error": "no_agents"}

        synthesis_prompt = f"Original question: {query}\n\nAnalyses:\n\n"
        for agent_name, result in analysis_results.items():
            if result.get("success"):
                synthesis_prompt += f"{agent_name}: {result['content']}\n\n"

        synthesis_prompt += (
            "Synthesize these analyses into comprehensive recommendation."
        )

        return self.agents[0].api.chat(prompt=synthesis_prompt)

    @staticmethod
    def create_racing_analysts(provider: str = "openai") -> "MultiAgent":
        """Create 3 specialized agents for racing analysis."""
        agents = [
            CopilotAgent(
                name="FeatureEngineer",
                system_prompt="You are an expert data scientist specializing in feature "
                "engineering for horse racing prediction models.",
                provider=provider,
            ),
            CopilotAgent(
                name="ModelArchitect",
                system_prompt="You are an expert ML engineer specializing in gradient "
                "boosting models for sports prediction.",
                provider=provider,
            ),
            CopilotAgent(
                name="DomainExpert",
                system_prompt="You are a horse racing analyst with deep knowledge of racing "
                "strategy and performance factors.",
                provider=provider,
            ),
        ]

        return MultiAgent(agents)

    @staticmethod
    def create_code_reviewers(provider: str = "openai") -> "MultiAgent":
        """Create 3 specialized code review agents."""
        agents = [
            CopilotAgent(
                name="SecurityReviewer",
                system_prompt="You are a security expert reviewing code for vulnerabilities.",
                provider=provider,
            ),
            CopilotAgent(
                name="PerformanceReviewer",
                system_prompt="You are a performance optimization expert.",
                provider=provider,
            ),
            CopilotAgent(
                name="QualityReviewer",
                system_prompt="You are a code quality expert.",
                provider=provider,
            ),
        ]

        return MultiAgent(agents)

    @staticmethod
    def create_custom(agent_configs: list[dict[str, str]]) -> "MultiAgent":
        """Create custom multi-agent system."""
        agents = [
            CopilotAgent(name=config["name"], system_prompt=config["system_prompt"])
            for config in agent_configs
        ]
        return MultiAgent(agents)
