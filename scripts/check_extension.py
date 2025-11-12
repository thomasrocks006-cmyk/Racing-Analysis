#!/usr/bin/env python3
"""
Test if VS Code Copilot Bridge extension is accessible.
If not, provides instructions to activate it.
"""

import time

import requests


def check_extension():
    """Check if extension is running."""
    print("=" * 80)
    print("VS CODE COPILOT BRIDGE - EXTENSION CHECK")
    print("=" * 80)
    print()

    print("Checking if extension server is running on localhost:3737...")

    try:
        response = requests.get("http://localhost:3737/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print("✅ Extension IS running!")
            print(f"   Status: {data.get('status')}")
            print(f"   API: {data.get('api')}")
            print(f"   Vendor: {data.get('vendor')}")
            print()
            return True
        else:
            print(f"❌ Server responded with: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Extension NOT running")
        print(f"   Error: {e}")
        print()
        print_activation_instructions()
        return False


def print_activation_instructions():
    """Print instructions to activate the extension."""
    print("=" * 80)
    print("HOW TO ACTIVATE THE EXTENSION")
    print("=" * 80)
    print()
    print("Option 1: Via Command Palette")
    print("  1. Press F1 (or Ctrl+Shift+P / Cmd+Shift+P)")
    print("  2. Type: 'Copilot Bridge: Start Server'")
    print("  3. Press Enter")
    print("  4. Look for notification: 'GitHub Copilot Bridge running on...'")
    print()
    print("Option 2: Install Extension Manually")
    print("  The extension is located at:")
    print("  .vscode/extensions/copilot-multi-agent-bridge/")
    print()
    print("  VS Code should auto-load extensions from .vscode/extensions/")
    print("  but you may need to reload VS Code:")
    print()
    print("  1. Press F1")
    print("  2. Type: 'Developer: Reload Window'")
    print("  3. Press Enter")
    print("  4. Wait for VS Code to reload")
    print("  5. Extension should auto-start")
    print()
    print("Option 3: Check if Extension is Loaded")
    print("  Run: code --list-extensions")
    print("  Look for: 'copilot-multi-agent-bridge'")
    print()
    print("=" * 80)
    print("WHY USE THE EXTENSION?")
    print("=" * 80)
    print()
    print("Without Extension:")
    print("  ✅ OpenAI API (gpt-4o) - WORKS NOW")
    print("  ✅ Anthropic API (claude) - WORKS NOW")
    print("  ✅ GLM API - WORKS NOW")
    print("  💰 Cost: ~$0.03 per request")
    print()
    print("With Extension:")
    print("  ✅ GitHub Copilot (gpt-4o) - SAME MODEL")
    print("  ✅ Uses premium requests (1500/month included)")
    print("  💰 Cost: FREE (included in Pro Plus)")
    print()
    print("If you make >300 requests/month, the extension saves money.")
    print("If you make <300 requests/month, OpenAI is simpler.")
    print()
    print("=" * 80)


if __name__ == "__main__":
    is_running = check_extension()

    if is_running:
        print("✅ Extension is ready to use!")
        print()
        print("Test it with:")
        print()
        print("  from src.api.vscode_copilot_bridge import VSCodeCopilotAPI")
        print("  api = VSCodeCopilotAPI()")
        print("  response = api.chat('What is gradient boosting?')")
        print("  print(response)")
        print()
    else:
        print("⚠️  Extension not running - using OpenAI/Anthropic instead")
        print()
        print("Your multi-agent system WORKS with OpenAI (already tested!)")
        print("Activating the extension is OPTIONAL for cost savings.")
        print()
