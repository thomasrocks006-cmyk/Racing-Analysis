#!/usr/bin/env python3
"""
API Configuration Validator

This script helps verify your API setup is correct.
Tests GLM, OpenAI, and Anthropic API keys.
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_api_key():
    """Check if GLM API key is configured"""
    api_key = os.getenv("GLM_API_KEY")

    if not api_key or api_key == "your_glm_api_key_here":
        print("❌ GLM_API_KEY not found or not configured in .env file")
        print("\nTo fix:")
        print("1. Open .env file")
        print("2. Add: GLM_API_KEY=your_actual_api_key")
        print("3. Get your key from: https://open.bigmodel.cn/")
        return False

    print(f"✅ GLM_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
    return api_key


def check_continue_config():
    """Check if Continue configuration exists"""
    config_path = Path(".vscode/continue-config.json")

    if not config_path.exists():
        print("❌ Continue configuration not found at .vscode/continue-config.json")
        return False

    with open(config_path) as f:
        config = json.load(f)

    if not config.get("models"):
        print("❌ No models configured in continue-config.json")
        return False

    # Check if API key is configured
    for model in config["models"]:
        if model.get("apiKey") == "YOUR_GLM_API_KEY_HERE":
            print("⚠️  Continue config still has placeholder API key")
            print("\nTo fix:")
            print("1. Open .vscode/continue-config.json")
            print("2. Replace YOUR_GLM_API_KEY_HERE with ${GLM_API_KEY}")
            print("   Or paste your actual API key (less secure)")
            return False

    print(f"✅ Continue configuration found with {len(config['models'])} model(s)")
    return True


def test_api_connection(api_key):
    """Test connection to GLM API"""
    print("\n🔄 Testing API connection...")

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Try different model names to find which one works
    test_models = ["glm-4", "glm-4-plus", "glm-4-air", "glm-4-flash"]

    for model_name in test_models:
        print(f"   Trying model: {model_name}...")
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": "Say 'Hello' in one word"}],
            "max_tokens": 10,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                reply = (
                    data.get("choices", [{}])[0].get("message", {}).get("content", "")
                )
                print(f"✅ API connection successful with model: {model_name}!")
                print(f"   Model responded: {reply}")
                print(f"\n💡 Working model name: {model_name}")
                return True
            elif response.status_code == 401:
                print("❌ Authentication failed - check your API key")
                print(f"   Error: {response.text}")
                return False
            elif response.status_code == 429:
                print("⚠️  Rate limit exceeded or insufficient credits")
                print("   Check your account at https://open.bigmodel.cn/")
                return False
            elif response.status_code == 400:
                # Model not found, try next one
                print(f"   ✗ Model {model_name} not available")
                continue
            else:
                print(f"   ✗ Error {response.status_code}: {response.text}")
                continue

        except requests.exceptions.Timeout:
            print("❌ Connection timeout - check your internet connection")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            return False

    # If we get here, none of the models worked
    print("\n❌ None of the test models worked.")
    print("   Tested models:", ", ".join(test_models))
    print("   Please check https://open.bigmodel.cn/dev/api for correct model names")
    return False


def test_openai_api(api_key):
    """Test OpenAI API connection"""
    if not api_key or api_key == "your_openai_api_key_here":
        return None

    print("🔍 Testing OpenAI API...")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say hi in 2 words"}],
        "max_tokens": 10,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"✅ OpenAI API working! Response: '{reply}'")
            return True
        else:
            print(f"❌ OpenAI API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  OpenAI API connection error: {e}")
        return False


def test_anthropic_api(api_key):
    """Test Anthropic API connection"""
    if not api_key or api_key == "your_anthropic_api_key_here":
        return None

    print("🔍 Testing Anthropic API...")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Say hi in 2 words"}],
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            reply = data.get("content", [{}])[0].get("text", "")
            print(f"✅ Anthropic API working! Response: '{reply}'")
            return True
        else:
            print(f"❌ Anthropic API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Anthropic API connection error: {e}")
        return False


def check_continue_extension():
    """Check if Continue extension is installed"""
    print("\n📦 Checking Continue extension...")
    print("   Note: This script cannot verify VS Code extensions")
    print("   Please manually verify in VS Code Extensions panel")
    print("   Search for: 'Continue' by Continue")
    return None


def main():
    """Run all checks"""
    print("=" * 70)
    print("API Configuration Validator")
    print("=" * 70)
    print()

    # Check GLM API key
    glm_key = check_api_key()
    if not glm_key:
        sys.exit(1)

    # Check Continue config
    print()
    config_ok = check_continue_config()

    # Test GLM API connection
    if glm_key and glm_key != "your_glm_api_key_here":
        print()
        glm_ok = test_api_connection(glm_key)
    else:
        glm_ok = False

    # Test OpenAI API
    print()
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_ok = test_openai_api(openai_key)

    # Test Anthropic API
    print()
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_ok = test_anthropic_api(anthropic_key)

    # Check extension
    check_continue_extension()

    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)

    results = {
        "GLM": glm_ok,
        "OpenAI": openai_ok,
        "Anthropic": anthropic_ok,
    }

    working_apis = [name for name, status in results.items() if status is True]
    skipped_apis = [name for name, status in results.items() if status is None]
    failed_apis = [name for name, status in results.items() if status is False]

    if working_apis:
        print(f"\n✅ Working APIs: {', '.join(working_apis)}")

    if skipped_apis:
        print(f"\n⚪ Not configured: {', '.join(skipped_apis)}")

    if failed_apis:
        print(f"\n❌ Failed APIs: {', '.join(failed_apis)}")

    if glm_ok and config_ok:
        print("\n🎉 GLM setup is ready for VS Code Continue extension!")
        print("\nNext steps:")
        print("1. Open VS Code")
        print("2. Press Ctrl+L (Windows/Linux) or Cmd+L (Mac)")
        print("3. Select 'GLM-4-Plus' from the model dropdown")
        print("4. Start coding with GLM!")
    elif not glm_ok:
        print("\n⚠️  GLM issues detected. Please fix them and run again.")
        print("\nFor help, see:")
        print("- docs/GLM_SETUP_GUIDE.md")
        print("- docs/GLM_SUBSCRIPTION_SETUP.md")

    print()


if __name__ == "__main__":
    main()
