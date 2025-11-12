#!/usr/bin/env python3
"""
Multi-Agent Trial: 3 Agents with GPT-4o
Test concurrent agent execution for racing analysis
"""

import time

from src.api.task_executor import execute_multi_agent_task

print("=" * 80)
print("MULTI-AGENT TRIAL: 3 Agents with GPT-4o")
print("=" * 80)
print()

# Task: Analyze racing prediction model requirements
task_description = """
Design a comprehensive feature engineering pipeline for horse racing predictions.
Focus on practical implementation for betting models.
"""

# Define 3 specialized agents
subtasks = [
    {
        "agent": "DataArchitect",
        "task": "Design the data storage schema and ETL pipeline for race data. Include tables for races, horses, jockeys, and market data.",
    },
    {
        "agent": "FeatureEngineer",
        "task": "List 10 critical features to engineer from raw race data. Explain why each feature is predictive.",
    },
    {
        "agent": "ModelingExpert",
        "task": "Recommend the best model architecture and training strategy for racing predictions with uncertain outcomes.",
    },
]

print(f"Task: {task_description.strip()}")
print(f"\nLaunching {len(subtasks)} agents in parallel...")
print("-" * 80)

# Execute with timing
start_time = time.time()

task = execute_multi_agent_task(
    description=task_description,
    subtasks=subtasks,
    provider="openai",  # Using GPT-4o
    max_agents=3,
)

execution_time = time.time() - start_time

print("\n" + "=" * 80)
print("AGENT RESULTS")
print("=" * 80)

# Display each agent's output
for i, result in enumerate(task.results, 1):
    print(f"\n[Agent {i}/{len(task.results)}] {result.agent_name}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    print(f"Status: {'✅ Success' if result.success else '❌ Failed'}")
    print("-" * 80)

    if result.success:
        # Display first 500 chars
        output = result.output
        if len(output) > 500:
            print(output[:500] + "...\n[truncated]")
        else:
            print(output)
    else:
        print(f"Error: {result.error}")
    print()

# Display synthesized result
print("=" * 80)
print("SYNTHESIZED RESULT (Combined Insights)")
print("=" * 80)
print()
print(task.synthesis)
print()

# Summary statistics
print("=" * 80)
print("EXECUTION SUMMARY")
print("=" * 80)
print(f"Total agents: {len(task.results)}")
print(f"Successful: {sum(1 for r in task.results if r.success)}")
print(f"Failed: {sum(1 for r in task.results if not r.success)}")
print(f"Total execution time: {execution_time:.2f}s")
print(f"Average per agent: {execution_time / len(task.results):.2f}s")
print(f"Provider: {task.results[0].agent_name if task.results else 'N/A'}")
print()

# Cost estimate (approximate)
print("Approximate API Cost:")
print(f"  - {len(subtasks)} agent requests")
print(f"  - 1 synthesis request")
print(f"  - Total: {len(subtasks) + 1} API calls")
print(f"  - Estimated cost: $0.08-0.15")
print()
print("=" * 80)
