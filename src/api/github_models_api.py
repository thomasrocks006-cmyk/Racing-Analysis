#!/usr/bin/env python3
"""
GitHub Models API - Direct Access to GitHub's AI Models

This is a PUBLIC REST API from GitHub that provides access to:
- GPT-4o, GPT-4o-mini
- Claude 3.5 Sonnet
- Llama 3.1, Mistral, etc.

FREE TIER: 15 requests/minute, 150 requests/day
This is SEPARATE from your Copilot premium requests.

Docs: https://docs.github.com/en/github-models
"""

import os
from typing import Any

import requests


class GitHubModelsAPI:
    """
    Access GitHub's Models API - a real REST API for AI models.

    This is separate from Copilot but uses the same GitHub authentication.
    FREE tier: 15 req/min, 150 req/day
    """

    def __init__(self, github_token: str | None = None):
        """Initialize with GitHub token."""
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN required. Get from: gh auth token")

        self.base_url = "https://models.github.com"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.github_token}",
                "Content-Type": "application/json",
            }
        )

    def chat(
        self,
        prompt: str,
        model: str = "gpt-4o",
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """
        Send a chat request to GitHub Models API.

        Args:
            prompt: User message
            model: Model to use (gpt-4o, gpt-4o-mini, claude-3.5-sonnet, etc.)
            system_prompt: Optional system message
            temperature: Response randomness

        Returns:
            Response dict with content
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                },
                timeout=60,
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "content": data["choices"][0]["message"]["content"],
                    "model": data.get("model", model),
                    "usage": data.get("usage", {}),
                    "provider": "github-models",
                }
            else:
                return {
                    "success": False,
                    "error": f"http_{response.status_code}",
                    "message": response.text,
                }

        except Exception as e:
            return {
                "success": False,
                "error": "request_failed",
                "message": str(e),
            }

    def list_models(self) -> list[str]:
        """List available models."""
        # GitHub Models currently supports these
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "claude-3.5-sonnet",
            "llama-3.1-405b",
            "llama-3.1-70b",
            "mistral-large",
            "mistral-small",
        ]

    def health_check(self) -> dict[str, Any]:
        """Check if API is accessible."""
        try:
            # Try a simple request
            response = self.chat("Hello", model="gpt-4o-mini")
            if response.get("success"):
                return {
                    "status": "healthy",
                    "message": "GitHub Models API working",
                    "available_models": len(self.list_models()),
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": response.get("message", "Unknown error"),
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }


class GitHubModelsAgent:
    """Individual agent using GitHub Models API."""

    def __init__(
        self,
        name: str,
        system_prompt: str = "",
        model: str = "gpt-4o",
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.api = GitHubModelsAPI()

    def chat(self, prompt: str) -> dict[str, Any]:
        """Send message as this agent."""
        return self.api.chat(
            prompt,
            model=self.model,
            system_prompt=self.system_prompt,
        )


def quick_test():
    """Quick test of GitHub Models API."""
    print("Testing GitHub Models API...")
    print("=" * 80)

    api = GitHubModelsAPI()

    # Health check
    print("\n1. Health Check:")
    health = api.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Message: {health['message']}")

    # List models
    print("\n2. Available Models:")
    for model in api.list_models():
        print(f"   - {model}")

    # Test request
    print("\n3. Test Request (gpt-4o-mini):")
    response = api.chat(
        "In one sentence, what makes a good machine learning model?",
        model="gpt-4o-mini",
    )
    if response["success"]:
        print(f"   ✅ Success!")
        print(f"   Response: {response['content'][:200]}...")
        print(f"   Tokens: {response.get('usage', {})}")
    else:
        print(f"   ❌ Failed: {response.get('message')}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    quick_test()
