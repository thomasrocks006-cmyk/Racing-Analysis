"""
Claude Skills Integration
Claude's new feature allowing it to use tools and perform actions
"""

from typing import Any

from .copilot_api import GitHubCopilotAPI


class ClaudeSkills:
    """
    Interface for Claude's Skills feature.
    Skills allow Claude to:
    - Use tools (search, code execution, file operations)
    - Access web content
    - Perform multi-step reasoning
    - Use computer vision capabilities
    """

    def __init__(self):
        """Initialize Claude Skills API."""
        self.api = GitHubCopilotAPI(provider="anthropic", model="claude-sonnet-4-5")

    def search_and_analyze(
        self, query: str, context: str | None = None
    ) -> dict[str, Any]:
        """
        Use Claude's search skill to find information and analyze it.

        Args:
            query: What to search for
            context: Additional context for the search

        Returns:
            Analysis with sources
        """
        prompt = f"Search for: {query}"
        if context:
            prompt += f"\n\nContext: {context}"

        prompt += "\n\nProvide detailed analysis with sources."

        # Claude Skills automatically uses search when needed
        response = self.api.chat(
            prompt,
            system_prompt="You have access to web search. Use it to provide accurate, "
            "up-to-date information with sources.",
        )

        return response

    def analyze_code(self, code: str, task: str) -> dict[str, Any]:
        """
        Use Claude to analyze code with its enhanced reasoning.

        Args:
            code: Code to analyze
            task: What to do with the code (review, refactor, explain, etc.)

        Returns:
            Analysis result
        """
        prompt = f"Task: {task}\n\nCode:\n```python\n{code}\n```"

        response = self.api.chat(
            prompt,
            system_prompt="You are an expert code analyst. Provide detailed, "
            "actionable feedback.",
        )

        return response

    def multi_step_reasoning(self, problem: str) -> dict[str, Any]:
        """
        Use Claude's enhanced reasoning for complex problems.

        Args:
            problem: Complex problem to solve

        Returns:
            Step-by-step solution
        """
        response = self.api.chat(
            problem,
            system_prompt="Break down complex problems into steps. Show your reasoning "
            "process clearly.",
            temperature=0.3,
        )

        return response

    def research_topic(
        self, topic: str, depth: str = "comprehensive"
    ) -> dict[str, Any]:
        """
        Deep research on a topic using Claude's search and reasoning.

        Args:
            topic: Topic to research
            depth: "quick", "standard", or "comprehensive"

        Returns:
            Research report with sources
        """
        depth_prompts = {
            "quick": "Provide a concise overview",
            "standard": "Provide a thorough analysis",
            "comprehensive": "Provide an in-depth, comprehensive analysis with examples",
        }

        prompt = f"""Research topic: {topic}

{depth_prompts.get(depth, depth_prompts["standard"])}

Include:
1. Current state of the art
2. Recent developments (last 6 months)
3. Key tools and technologies
4. Best practices
5. Sources and references
"""

        response = self.api.chat(
            prompt,
            system_prompt="You have access to web search. Conduct thorough research "
            "and cite your sources.",
        )

        return response


# Convenience function
def research_with_claude(topic: str, depth: str = "comprehensive") -> dict[str, Any]:
    """
    Quick function to research a topic using Claude Skills.

    Example:
        >>> result = research_with_claude("Transformer models for time series prediction")
        >>> print(result['content'])
    """
    skills = ClaudeSkills()
    return skills.research_topic(topic, depth)
