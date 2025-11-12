"""
GitHub Copilot Premium - Important Clarification

GitHub Copilot Pro Plus provides 1500 premium requests/month for VS Code Chat interface.
There is NO programmatic REST API for GitHub Copilot.

For multi-agent task execution, use:
- OpenAI API (src/api/copilot_api.py with provider="openai")
- Anthropic API (src/api/copilot_api.py with provider="anthropic")
- GLM API (src/api/copilot_api.py with provider="glm")

Your GitHub Copilot premium requests are for the VS Code chat you're using now!
"""

from typing import Any


class GitHubCopilotPremiumAPI:
    """
    Explanation class - GitHub Copilot does not have a programmatic REST API.

    Use OpenAI or Anthropic APIs for multi-agent execution instead.
    Your 1500 premium requests are for VS Code chat interface.
    """

    def __init__(self):
        """Initialize with warning message."""
        print(
            "\n" + "=" * 80 + "\n"
            "⚠️  IMPORTANT: GitHub Copilot Premium API Not Available\n"
            "=" * 80 + "\n"
            "GitHub Copilot Pro Plus (1500 premium requests/month) is for:\n"
            "  - VS Code Chat interface (this conversation)\n"
            "  - Inline code completions\n"
            "  - NOT for programmatic REST API access\n\n"
            "For multi-agent execution, use the already-configured:\n"
            "  - OpenAI API (gpt-4o, o1-mini)\n"
            "  - Anthropic API (claude-sonnet-4-5)\n"
            "  - GLM API (glm-4-plus)\n\n"
            "These are in: src/api/copilot_api.py\n"
            "=" * 80 + "\n"
        )

    def chat(self, prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
        """Returns error message explaining no REST API available."""
        return {
            "success": False,
            "error": "no_rest_api",
            "message": (
                "GitHub Copilot does not provide a public REST API. "
                "Use OpenAI or Anthropic for programmatic access. "
                "Your premium requests are for VS Code chat interface."
            ),
        }

    def health_check(self) -> dict[str, Any]:
        """Returns status explaining the limitation."""
        return {
            "status": "not_applicable",
            "message": "GitHub Copilot has no REST API for programmatic access",
            "recommendation": "Use OpenAI API (src/api/copilot_api.py with provider='openai')",
        }


class GitHubCopilotAgent:
    """Placeholder - GitHub Copilot has no REST API."""

    def __init__(self, name: str, system_prompt: str = ""):
        self.name = name
        self.system_prompt = system_prompt
        print(
            f"\n⚠️  Agent '{name}': GitHub Copilot has no REST API.\n"
            f"   Use OpenAI or Anthropic for multi-agent execution.\n"
        )

    def chat(self, prompt: str) -> dict[str, Any]:
        """Returns error message."""
        return {
            "success": False,
            "error": "no_rest_api",
            "message": "GitHub Copilot has no REST API. Use OpenAI/Anthropic instead.",
        }


def ask_github_copilot(question: str) -> str:
    """
    Placeholder function - GitHub Copilot has no programmatic API.

    Use this VS Code chat instead!
    Or use OpenAI/Anthropic APIs for programmatic access.
    """
    return (
        "GitHub Copilot has no REST API for programmatic access. "
        "Use OpenAI or Anthropic APIs instead (src/api/copilot_api.py)."
    )
