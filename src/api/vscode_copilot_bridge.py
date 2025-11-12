"""
GitHub Copilot Multi-Agent Bridge - Python Client

Access GitHub Copilot programmatically using vscode.lm API through VS Code extension.
This DOES use your 1500 premium requests from GitHub Copilot Pro Plus!

The extension must be running for this to work.
"""

import json
import subprocess
import time
from typing import Any

import requests


class VSCodeCopilotAPI:
    """
    Access GitHub Copilot through VS Code extension bridge.

    USES YOUR GITHUB COPILOT PRO PLUS PREMIUM REQUESTS (1500/month)!

    This works by:
    1. VS Code extension runs HTTP server on localhost:3737
    2. Extension uses vscode.lm.selectChatModels({ vendor: 'copilot' })
    3. Python sends requests to the extension's server
    4. Extension forwards to Copilot and returns response
    """

    def __init__(self, base_url: str = "http://localhost:3737"):
        """Initialize Copilot API client."""
        self.base_url = base_url
        self.session = requests.Session()

    def health_check(self) -> dict[str, Any]:
        """Check if extension bridge is running."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "message": "VS Code Copilot Bridge is running",
                    **data,
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Server returned {response.status_code}",
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "offline",
                "message": (
                    "VS Code extension not running. "
                    "Run command: 'Copilot Bridge: Start Server' in VS Code"
                ),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error checking health: {e}",
            }

    def chat(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str = "claude-sonnet-4.5",  # Premium model (4.5, not 3.5!)
        timeout: int = 60,
    ) -> dict[str, Any]:
        """
        Send a chat request to GitHub Copilot using PREMIUM models.

        Default: Claude Sonnet 4.5 (premium tier)
        Free tier: gpt-4o, gpt-4.1
        Premium tier: claude-sonnet-4.5 (THIS IS 4.5, NOT 3.5!)

        THIS USES 1 PREMIUM REQUEST from your 1500/month allocation!

        Args:
            prompt: User message
            system_prompt: Optional system message
            model: Model to use (default: claude-sonnet-4.5 for premium)
            timeout: Request timeout in seconds

        Returns:
            Response dict with content

        Example:
            >>> api = VSCodeCopilotAPI()
            >>> response = api.chat("What is gradient boosting?")
            >>> print(response["content"])
        """
        try:
            payload = {"prompt": prompt, "model": model}
            if system_prompt:
                payload["system_prompt"] = system_prompt

            response = self.session.post(
                f"{self.base_url}/copilot/chat",
                json=payload,
                timeout=timeout,
            )

            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return {
                    "success": False,
                    "error": "http_error",
                    "message": f"HTTP {response.status_code}: {response.text}",
                }

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "connection_error",
                "message": (
                    "Cannot connect to VS Code extension. "
                    "Make sure the extension is running. "
                    "Run: 'Copilot Bridge: Start Server' in VS Code"
                ),
            }
        except Exception as e:
            return {
                "success": False,
                "error": "unknown_error",
                "message": str(e),
            }


class VSCodeCopilotAgent:
    """Individual agent using GitHub Copilot through VS Code extension."""

    def __init__(self, name: str, system_prompt: str = ""):
        self.name = name
        self.system_prompt = system_prompt
        self.api = VSCodeCopilotAPI()

    def chat(self, prompt: str) -> dict[str, Any]:
        """Send message as this agent (uses 1 premium request)."""
        return self.api.chat(prompt, system_prompt=self.system_prompt)


def ask_copilot(question: str) -> str:
    """
    Quick helper to ask GitHub Copilot a question.

    Uses your premium requests through VS Code extension!
    """
    api = VSCodeCopilotAPI()
    response = api.chat(question)

    if response.get("success"):
        return response.get("content", "")
    else:
        return f"Error: {response.get('message', 'Unknown error')}"


# Module-level info
print(
    "\n" + "=" * 80 + "\n"
    "✅ GITHUB COPILOT MULTI-AGENT BRIDGE\n"
    "=" * 80 + "\n"
    "This module provides programmatic access to GitHub Copilot via VS Code extension.\n\n"
    "Requirements:\n"
    "  1. VS Code with GitHub Copilot extension installed\n"
    "  2. Copilot Multi-Agent Bridge extension installed\n"
    "  3. Bridge server running (auto-starts on VS Code launch)\n\n"
    "Usage:\n"
    "  from src.api.vscode_copilot_bridge import VSCodeCopilotAPI\n"
    "  api = VSCodeCopilotAPI()\n"
    "  response = api.chat('Your question')\n\n"
    "USES YOUR 1500 PREMIUM REQUESTS/MONTH from GitHub Copilot Pro Plus!\n"
    "=" * 80 + "\n"
)
