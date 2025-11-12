"""
Example: Using GitHub Copilot API for racing analysis
Demonstrates single requests and multi-agent pattern
"""

from src.api.copilot_api import CopilotAgent, GitHubCopilotAPI, MultiAgent


def example_single_request():
    """Simple single request to Copilot."""
    print("=" * 60)
    print("Example 1: Single Request")
    print("=" * 60)

    api = GitHubCopilotAPI()

    # Check if server is running
    if not api.health_check():
        print("❌ Copilot API Server is not running!")
        print("Please start it from VS Code: Cmd+Shift+P > 'Start Copilot API Server'")
        return

    print("✅ API Server is running\n")

    # Make a simple request
    response = api.chat(
        "Explain the difference between CatBoost and LightGBM in 3 sentences."
    )

    if response.get("success"):
        print(f"Response from {response['model']}:")
        print(response["content"])
    else:
        print(f"❌ Error: {response.get('message')}")


def example_three_agents():
    """Use 3 specialized agents for comprehensive analysis."""
    print("\n" + "=" * 60)
    print("Example 2: Three Agent Analysis")
    print("=" * 60)

    # Create 3 specialized racing analysts
    agents = MultiAgent.create_racing_analysts()

    query = """
    I'm building a horse racing prediction model. Should I use CatBoost or LightGBM?
    Consider: feature handling, training speed, prediction quality, and ease of use.
    """

    print(f"\nQuery: {query.strip()}\n")
    print("Consulting 3 experts concurrently...\n")

    # Get analysis from all agents (runs in parallel)
    results = agents.analyze(query, max_concurrent=3)

    # Print each agent's response
    for agent_name, result in results.items():
        print(f"\n{'=' * 60}")
        print(f"{agent_name}'s Analysis:")
        print("=" * 60)

        if result.get("success"):
            print(result["content"])
        else:
            print(f"❌ Error: {result.get('message')}")

    # Synthesize results
    print(f"\n{'=' * 60}")
    print("Synthesized Recommendation:")
    print("=" * 60)

    synthesis = agents.synthesize(query, results)
    if synthesis.get("success"):
        print(synthesis["content"])
    else:
        print(f"❌ Error: {synthesis.get('message')}")


def example_custom_agents():
    """Create custom agents for specific task."""
    print("\n" + "=" * 60)
    print("Example 3: Custom Agents")
    print("=" * 60)

    configs = [
        {
            "name": "OptimisticAnalyst",
            "system_prompt": "You are an optimistic analyst who focuses on opportunities and potential upside. Always highlight positive aspects.",
        },
        {
            "name": "PessimisticAnalyst",
            "system_prompt": "You are a pessimistic analyst who focuses on risks and potential problems. Always highlight concerns.",
        },
        {
            "name": "RealisticAnalyst",
            "system_prompt": "You are a balanced analyst who weighs both opportunities and risks objectively.",
        },
    ]

    agents = MultiAgent.create_custom(configs)

    query = "What are the prospects for using transformer models in horse racing prediction?"

    print(f"\nQuery: {query}\n")
    print("Getting perspectives from 3 analysts...\n")

    results = agents.analyze(query)

    for agent_name, result in results.items():
        print(f"\n{agent_name}:")
        if result.get("success"):
            print(result["content"][:200] + "...")  # First 200 chars
        else:
            print(f"❌ Error: {result.get('message')}")


def example_conversational_agent():
    """Single agent with conversation history."""
    print("\n" + "=" * 60)
    print("Example 4: Conversational Agent")
    print("=" * 60)

    agent = CopilotAgent(
        name="RacingTutor",
        system_prompt="""You are a patient tutor teaching machine learning for horse racing.
Explain concepts clearly with racing-specific examples.""",
    )

    # Multi-turn conversation
    questions = [
        "What is gradient boosting?",
        "How does it apply to racing prediction?",
        "What features should I engineer for horse performance?",
    ]

    for question in questions:
        print(f"\nUser: {question}")
        response = agent.chat(question)

        if response.get("success"):
            print(f"Tutor: {response['content'][:150]}...")
        else:
            print(f"❌ Error: {response.get('message')}")

    print(f"\nConversation history length: {len(agent.conversation_history)} messages")


if __name__ == "__main__":
    print("GitHub Copilot API Examples")
    print("Using your GitHub Copilot Pro Plus premium requests\n")

    # Run examples
    example_single_request()
    example_three_agents()
    example_custom_agents()
    example_conversational_agent()

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
