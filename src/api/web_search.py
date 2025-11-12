"""
Mandatory Web Search Integration
Automatically search the web for up-to-date information before responding
"""

import os
from datetime import datetime
from typing import Any

import requests

from .copilot_api import GitHubCopilotAPI


class WebSearchAPI:
    """
    Web search integration for keeping AI responses current.
    Uses multiple search APIs (Tavily, Serper, or DuckDuckGo).
    """

    def __init__(self):
        """Initialize with available search API."""
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.serper_key = os.getenv("SERPER_API_KEY")

        # Determine which API to use
        if self.tavily_key:
            self.provider = "tavily"
        elif self.serper_key:
            self.provider = "serper"
        else:
            self.provider = "duckduckgo"  # Fallback to free search

    def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """
        Search the web for current information.

        Args:
            query: Search query
            max_results: Number of results to return

        Returns:
            List of search results with title, url, snippet
        """
        if self.provider == "tavily":
            return self._search_tavily(query, max_results)
        elif self.provider == "serper":
            return self._search_serper(query, max_results)
        else:
            return self._search_duckduckgo(query, max_results)

    def _search_tavily(self, query: str, max_results: int) -> list[dict[str, Any]]:
        """Search using Tavily API (best for AI)."""
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": True,
                },
                timeout=10,
            )
            data = response.json()

            results = []
            for item in data.get("results", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", ""),
                    }
                )

            return results
        except Exception as e:
            print(f"Tavily search failed: {e}")
            return []

    def _search_serper(self, query: str, max_results: int) -> list[dict[str, Any]]:
        """Search using Serper API."""
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.serper_key},
                json={"q": query, "num": max_results},
                timeout=10,
            )
            data = response.json()

            results = []
            for item in data.get("organic", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                    }
                )

            return results
        except Exception as e:
            print(f"Serper search failed: {e}")
            return []

    def _search_duckduckgo(self, query: str, max_results: int) -> list[dict[str, Any]]:
        """Search using DuckDuckGo (free, no API key needed)."""
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=max_results):
                    results.append(
                        {
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "snippet": result.get("body", ""),
                        }
                    )

            return results
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
            return []


class SearchEnhancedAI:
    """
    AI with mandatory web search before responding.
    Ensures responses are up-to-date with latest information.
    """

    def __init__(self, provider: str = "openai"):
        """Initialize with AI provider and web search."""
        self.ai = GitHubCopilotAPI(provider=provider)
        self.search = WebSearchAPI()

    def chat(self, prompt: str, search_query: str | None = None) -> dict[str, Any]:
        """
        Chat with mandatory web search.

        Args:
            prompt: User's question/request
            search_query: Optional custom search query (defaults to using prompt)

        Returns:
            AI response enhanced with current web information
        """
        # Perform web search
        query = search_query or self._extract_search_query(prompt)
        print(f"[WebSearch] Searching for: {query}")

        search_results = self.search.search(query)

        if not search_results:
            print("[WebSearch] No results found, proceeding without search context")

        # Build enhanced prompt with search results
        enhanced_prompt = self._build_enhanced_prompt(prompt, search_results)

        # Get AI response
        response = self.ai.chat(enhanced_prompt)

        # Add search metadata
        if response.get("success"):
            response["search_results"] = search_results
            response["search_query"] = query

        return response

    def _extract_search_query(self, prompt: str) -> str:
        """Extract a good search query from the prompt."""
        # Use AI to create optimal search query
        query_prompt = f"Extract a concise search query from this request (respond with ONLY the search query, no explanation):\n\n{prompt}"

        response = self.ai.chat(query_prompt, temperature=0.3)

        if response.get("success"):
            return response["content"].strip().strip("\"'")

        # Fallback: use first 100 chars
        return prompt[:100]

    def _build_enhanced_prompt(
        self, prompt: str, search_results: list[dict[str, Any]]
    ) -> str:
        """Build prompt enhanced with search results."""
        if not search_results:
            return prompt

        enhanced = f"""Current Date: {datetime.now().strftime("%B %d, %Y")}

Web Search Results:
"""

        for i, result in enumerate(search_results[:5], 1):
            enhanced += f"\n{i}. {result['title']}\n"
            enhanced += f"   Source: {result['url']}\n"
            enhanced += f"   {result['snippet']}\n"

        enhanced += f"\n---\n\nUser Request: {prompt}\n\n"
        enhanced += (
            "Use the search results above to provide an up-to-date, accurate response. "
        )
        enhanced += "Cite sources when relevant."

        return enhanced


# Convenience function
def chat_with_search(
    prompt: str, provider: str = "openai", search_query: str | None = None
) -> dict[str, Any]:
    """
    Quick function to chat with mandatory web search.

    Example:
        >>> result = chat_with_search("What are the latest advancements in LightGBM?")
        >>> print(result['content'])
        >>> print(f"Sources: {len(result['search_results'])} results")
    """
    ai = SearchEnhancedAI(provider=provider)
    return ai.chat(prompt, search_query)
