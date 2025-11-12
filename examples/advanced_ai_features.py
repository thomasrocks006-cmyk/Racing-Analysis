"""
Complete Example: Multi-Agent Task Execution with OpenAI/Anthropic/GLM
Demonstrates multi-agent execution like GitHub Copilot Chat, but using REST APIs

Note: GitHub Copilot Pro Plus (1500 premium requests/month) is for VS Code chat interface only.
      For programmatic multi-agent execution, use OpenAI, Anthropic, or GLM APIs.
"""

# ============================================================================
# Example 1: Multi-Agent Task Execution
# ============================================================================
print("=" * 80)
print("EXAMPLE 1: Multi-Agent Task Execution (like GitHub Copilot Chat)")
print("=" * 80)

from src.api.task_executor import execute_multi_agent_task

# Create and execute a task with multiple agents working simultaneously
# Uses OpenAI API (gpt-4o) - similar to how GitHub Copilot Chat works
task = execute_multi_agent_task(
    description="Design a feature engineering pipeline for horse racing prediction",
    subtasks=[
        {
            "agent": "DataArchitect",
            "task": "Design the data flow and storage schema for features",
        },
        {
            "agent": "FeatureEngineer",
            "task": "List 10 key features to engineer from race data",
        },
        {
            "agent": "MLEngineer",
            "task": "Recommend the best way to preprocess and scale these features",
        },
    ],
    provider="openai",  # or "anthropic" or "glm"
    max_agents=3,
)

print(f"\n✅ Task completed by {len(task.subtasks)} agents working in parallel")
print(f"Provider: {task.subtasks[0].get('provider', 'openai')}")
print()
print("Individual Agent Results:")
print("-" * 80)
for result in task.results:
    if result.success:
        print(f"\n{result.agent_name} ({result.execution_time:.2f}s):")
        print(result.output[:200] + "...")

print("\n" + "=" * 80)
print("SYNTHESIZED RESULT:")
print("=" * 80)
print(task.synthesis)


# ============================================================================
# Example 2: Claude Skills Integration
# ============================================================================
print("\n\n" + "=" * 80)
print("EXAMPLE 2: Claude Skills (Research & Analysis)")
print("=" * 80)

from src.api.claude_skills import research_with_claude

# Use Claude to research latest developments
result = research_with_claude(
    topic="Latest improvements in gradient boosting libraries (CatBoost, LightGBM, XGBoost) in 2024-2025",
    depth="comprehensive",
)

if result.get("success"):
    print("\n📚 Research Report:")
    print(result["content"])


# ============================================================================
# Example 3: Mandatory Web Search
# ============================================================================
print("\n\n" + "=" * 80)
print("EXAMPLE 3: AI with Mandatory Web Search")
print("=" * 80)

from src.api.web_search import chat_with_search

# Every prompt automatically searches the web first
response = chat_with_search(
    "What are the newest features in scikit-learn 1.5+ that help with model calibration?",
    provider="openai",
)

if response.get("success"):
    print("\n💡 AI Response (with web search):")
    print(response["content"])

    print(f"\n🔍 Sources ({len(response.get('search_results', []))} results):")
    for i, result in enumerate(response.get("search_results", [])[:3], 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['url']}\n")


# ============================================================================
# Example 4: Combined - Multi-Agent Task with Web Search
# ============================================================================
print("\n\n" + "=" * 80)
print("EXAMPLE 4: Multi-Agent Task with Real-Time Research")
print("=" * 80)

from src.api.task_executor import TaskExecutor
from src.api.web_search import SearchEnhancedAI

# Create task executor
executor = TaskExecutor(provider="openai", max_agents=3)

# Create a task that requires current information
task = executor.create_task(
    description="Research and recommend the best approach for conformal prediction in 2025",
    subtasks=[
        {
            "agent": "Researcher",
            "task": "Search for latest conformal prediction papers and implementations",
        },
        {
            "agent": "Analyst",
            "task": "Compare different conformal prediction methods for time series",
        },
        {
            "agent": "Implementer",
            "task": "Recommend specific Python libraries and code structure",
        },
    ],
)

# Execute with each agent having web search capability
print(f"\nExecuting task: {task.description}")
print(f"Agents: {[s['agent'] for s in task.subtasks]}\n")

executed_task = executor.execute_task(task)

print("\n" + "=" * 80)
print("FINAL SYNTHESIS:")
print("=" * 80)
print(executed_task.synthesis)


# ============================================================================
# Example 5: Quick Multi-Agent Task (Auto-Decompose)
# ============================================================================
print("\n\n" + "=" * 80)
print("EXAMPLE 5: Auto-Decomposed Multi-Agent Task")
print("=" * 80)

# Let the AI automatically break down the task
task = execute_multi_agent_task(
    description="Build a real-time racing odds tracker with alert system",
    # No subtasks specified - will auto-decompose
    provider="openai",
)

print("\nAuto-generated subtasks:")
for i, subtask in enumerate(task.subtasks, 1):
    print(f"{i}. {subtask['agent']}: {subtask['task']}")

print("\n" + "=" * 80)
print("Result:")
print("=" * 80)
print(task.synthesis[:500] + "...")


print("\n\n" + "=" * 80)
print("✅ All examples completed!")
print("=" * 80)
print("\nKey Features Demonstrated:")
print("1. Multi-agent task execution (like Copilot Chat)")
print("2. Claude Skills for deep research")
print("3. Mandatory web search for current information")
print("4. Combined multi-agent + web search")
print("5. Auto-task decomposition")
