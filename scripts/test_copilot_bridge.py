#!/usr/bin/env python3
"""
Test Suite: GitHub Copilot Bridge with Claude Sonnet 4.5 (Premium)

3 Tests:
1. Health Check - Verify server is running
2. Single Request - Test one Claude Sonnet 4.5 call
3. Multi-Agent - Run 3 concurrent agents with premium model
"""

import time

from src.api.vscode_copilot_bridge import VSCodeCopilotAPI

print("=" * 80)
print("GITHUB COPILOT BRIDGE - CLAUDE SONNET 4.5 TEST SUITE")
print("=" * 80)
print()

# =============================================================================
# TEST 1: HEALTH CHECK
# =============================================================================
print("TEST 1: Health Check")
print("-" * 80)

api = VSCodeCopilotAPI()
health = api.health_check()

print(f"Status: {health.get('status')}")
print(f"Message: {health.get('message', 'N/A')}")

if health.get("status") == "healthy":
    print("✅ TEST 1 PASSED - Extension server is running")
else:
    print("❌ TEST 1 FAILED - Extension not responding")
    exit(1)

print()

# =============================================================================
# TEST 2: SINGLE REQUEST WITH CLAUDE SONNET 4.5
# =============================================================================
print("TEST 2: Single Request (Claude Sonnet 4.5)")
print("-" * 80)
print("Sending test query to Copilot Bridge...")
print("Model: claude-sonnet-4.5 (premium)")
print()

start_time = time.time()

response = api.chat(
    prompt="In exactly 2 sentences, explain what makes gradient boosting effective.",
    model="claude-sonnet-4.5",  # Premium model
)

execution_time = time.time() - start_time

if response.get("success"):
    print("✅ TEST 2 PASSED - Single request successful")
    print(f"   Model: {response.get('model', 'N/A')}")
    print(f"   Vendor: {response.get('vendor', 'N/A')}")
    print(f"   Family: {response.get('family', 'N/A')}")
    print(f"   Execution time: {execution_time:.2f}s")
    print(f"   Uses premium requests: {response.get('uses_premium_requests', False)}")
    print()
    print("   Response:")
    print(f"   {response['content']}")
    print()
else:
    print("❌ TEST 2 FAILED")
    print(f"   Error: {response.get('error')}")
    print(f"   Message: {response.get('message')}")
    exit(1)

print()

# =============================================================================
# TEST 3: MULTI-AGENT WITH 3 CONCURRENT CLAUDE SONNET 4.5 CALLS
# =============================================================================
print("TEST 3: Multi-Agent Execution (3 agents, Claude Sonnet 4.5)")
print("-" * 80)
print("This will use 3 premium requests + 1 for synthesis = 4 total")
print()

# First, we need to update task_executor to support vscode_copilot_bridge
print("Note: Using direct API calls (not task_executor integration yet)")
print("Testing 3 concurrent requests to validate premium model access...")
print()

import concurrent.futures

agents = [
    {
        "name": "FeatureExpert",
        "prompt": "In 3 sentences, what are the most critical features for racing predictions?",
    },
    {
        "name": "ModelExpert",
        "prompt": "In 3 sentences, what model architecture is best for racing predictions?",
    },
    {
        "name": "DataExpert",
        "prompt": "In 3 sentences, how should racing data be structured?",
    },
]


def run_agent(agent):
    """Run single agent with Claude Sonnet 4.5."""
    start = time.time()
    api = VSCodeCopilotAPI()
    response = api.chat(prompt=agent["prompt"], model="claude-sonnet-4.5")
    response["agent_name"] = agent["name"]
    response["execution_time"] = time.time() - start
    return response


print("Launching 3 agents in parallel...")
start_time = time.time()

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(run_agent, agent) for agent in agents]
    results = [future.result() for future in concurrent.futures.as_completed(futures)]

total_time = time.time() - start_time

print()
print("Agent Results:")
print("-" * 80)

success_count = 0
for i, result in enumerate(results, 1):
    if result.get("success"):
        success_count += 1
        print(f"\n[Agent {i}] {result['agent_name']}")
        print(f"Model: {result.get('family', 'N/A')}")
        print(f"Time: {result['execution_time']:.2f}s")
        print(f"Response: {result['content'][:150]}...")
    else:
        print(f"\n[Agent {i}] {result['agent_name']} - FAILED")
        print(f"Error: {result.get('message')}")

print()
print("-" * 80)
print(f"Total execution time: {total_time:.2f}s")
print(f"Successful agents: {success_count}/3")
print(f"Premium requests used: {success_count}")
print()

if success_count == 3:
    print("✅ TEST 3 PASSED - Multi-agent execution successful")
    print()
    print("=" * 80)
    print("ALL TESTS PASSED! 🎉")
    print("=" * 80)
    print()
    print("Summary:")
    print("  ✅ Extension server running")
    print("  ✅ Single Claude Sonnet 4.5 request working")
    print(f"  ✅ 3 concurrent agents executed in {total_time:.2f}s")
    print(f"  ✅ Premium requests used: {success_count + 1} (agents + this summary)")
    print()
    print("Your multi-agent system is now using GitHub Copilot premium requests!")
    print("Model: Claude Sonnet 4.5 (premium tier)")
else:
    print("❌ TEST 3 FAILED - Some agents did not complete")
    exit(1)
