#!/usr/bin/env python3
"""
Activate VS Code Copilot Bridge Extension

This extension allows programmatic access to GitHub Copilot's PREMIUM models:
- Claude Sonnet 4.5 (4.5, NOT 3.5!) - PREMIUM TIER (default)
- GPT-4o, GPT-4.1 - FREE TIER (not premium)

Uses your 1500 premium requests/month.
"""

import subprocess
import sys
import time

import requests

print("=" * 80)
print("ACTIVATING VS CODE COPILOT BRIDGE EXTENSION")
print("=" * 80)
print()

print("IMPORTANT: GitHub Copilot Model Tiers")
print("-" * 80)
print("FREE TIER (not premium):")
print("  - GPT-4o")
print("  - GPT-4.1")
print()
print("PREMIUM TIER (uses premium requests):")
print("  - Claude Sonnet 4.5 (THIS IS 4.5, NOT 3.5!)")
print()
print("Our extension defaults to: Claude Sonnet 4.5 (premium)")
print("=" * 80)
print()

# Check current status
print("1. Checking current status...")
try:
    response = requests.get("http://localhost:3737/health", timeout=2)
    if response.status_code == 200:
        print("   ✅ Extension ALREADY running!")
        print(f"   Response: {response.json()}")
        sys.exit(0)
except Exception:
    print("   ❌ Extension not running (expected)")

print()
print("2. Extension needs to be activated in VS Code")
print()
print("   The extension is a VS Code extension, so it must be activated")
print("   from within VS Code itself (not from Python/terminal).")
print()
print("=" * 80)
print("ACTIVATION STEPS")
print("=" * 80)
print()
print("Step 1: Reload VS Code Window")
print("   - Press F1 (Command Palette)")
print("   - Type: 'Developer: Reload Window'")
print("   - Press Enter")
print()
print("Step 2: Start the Extension Server")
print("   - After reload, press F1 again")
print("   - Type: 'Copilot Bridge: Start Server'")
print("   - Press Enter")
print()
print("Step 3: Look for confirmation")
print("   - You should see a notification:")
print("   - 'GitHub Copilot Bridge running on http://localhost:3737'")
print()
print("Step 4: Verify it's running")
print("   - Run this script again")
print("   - Or run: curl http://localhost:3737/health")
print()
print("=" * 80)
print("AFTER ACTIVATION")
print("=" * 80)
print()
print("Test the extension:")
print()
print('  python -c "')
print("from src.api.vscode_copilot_bridge import VSCodeCopilotAPI")
print()
print("api = VSCodeCopilotAPI()")
print()
print("# Uses Claude Sonnet 4.5 (premium) by default")
print("response = api.chat('What is gradient boosting?')")
print("print(response['content'])")
print()
print("# Or specify model explicitly:")
print("response = api.chat('Explain XGBoost', model='claude-sonnet-4.5')")
print('  "')
print()
print("=" * 80)
print()
print("NOTE: I cannot activate VS Code extensions from Python.")
print("You must use the Command Palette (F1) in VS Code itself.")
print()
