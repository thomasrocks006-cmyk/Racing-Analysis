#!/usr/bin/env python3
"""
Quick verification script for AI API setup
Tests all configured AI providers (OpenAI, Anthropic, GLM)
"""

import sys

from src.api.copilot_api import GitHubCopilotAPI, MultiAgent


def main():
    print("=" * 70)
    print("AI API Verification (OpenAI, Anthropic, GLM)")
    print("=" * 70)

    # Test all three providers
    providers = ["openai", "anthropic", "glm"]
    working_providers = []

    for provider in providers:
        print(f"\n[{provider.upper()}] Checking API...")
        api = GitHubCopilotAPI(provider=provider)

        if not api.health_check():
            print(f"❌ {provider.upper()} API key not found in environment")
            continue

        # Try a simple request
        response = api.chat(
            "In one sentence, what is gradient boosting?",
            temperature=0.5,
        )

        if response.get("success"):
            print(f"✅ {provider.upper()} API working!")
            print(f"   Model: {response.get('model')}")
            print(f"   Response: {response['content'][:80]}...")
            working_providers.append(provider)
        else:
            print(f"❌ {provider.upper()} request failed: {response.get('message')}")

    # Test multi-agent if we have at least one working provider
    if working_providers:
        print("\n" + "=" * 70)
        print("Testing Multi-Agent System")
        print("=" * 70)

        # Use the first working provider
        test_provider = working_providers[0]
        print(f"\nUsing {test_provider.upper()} for multi-agent test...")

        try:
            agents = MultiAgent.create_racing_analysts(provider=test_provider)
            print(f"✅ Created {len(agents.agents)} specialized agents:")
            for agent in agents.agents:
                print(f"   - {agent.name}")

            query = "In one sentence, what makes a good racing prediction model?"
            print(f"\n   Query: {query}")
            print("   Consulting agents...")

            results = agents.analyze(query, max_concurrent=3)

            success_count = sum(1 for r in results.values() if r.get("success"))
            print(f"\n✅ Received {success_count}/{len(results)} successful responses")

            for agent_name, result in results.items():
                if result.get("success"):
                    preview = result["content"][:60].replace("\n", " ")
                    print(f"   {agent_name}: {preview}...")

        except Exception as e:
            print(f"❌ Multi-agent test failed: {e}")

    # Summary
    print("\n" + "=" * 70)
    if working_providers:
        print(f"✅ {len(working_providers)}/{len(providers)} AI providers working!")
        print("=" * 70)
        print("\nWorking providers:", ", ".join([p.upper() for p in working_providers]))
        print("\nYou can now:")
        print(
            f"  • Use GitHubCopilotAPI(provider='{working_providers[0]}') for single requests"
        )
        print(
            f"  • Use MultiAgent.create_racing_analysts(provider='{working_providers[0]}') for multi-agent"
        )
        print("  • Run examples: python examples/copilot_api_example.py")
        print("\n" + "=" * 70)
    else:
        print("❌ No AI providers are working!")
        print("=" * 70)
        print("\nPlease check your .env file has these keys:")
        print("  - OPENAI_API_KEY")
        print("  - ANTHROPIC_API_KEY")
        print("  - GLM_API_KEY")
        sys.exit(1)


if __name__ == "__main__":
    main()
