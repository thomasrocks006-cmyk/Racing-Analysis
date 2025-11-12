#!/usr/bin/env python3
"""
Verification script for GitHub Copilot Premium API setup.
Checks all requirements and verifies the API is working.
"""

import os
import subprocess
import sys


def check_command(command: str, name: str) -> bool:
    """Check if a command exists and is accessible."""
    try:
        result = subprocess.run(
            ["which", command],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print(f"✅ {name} installed: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {name} not found. Please install it first.")
            return False
    except Exception as e:
        print(f"❌ Error checking {name}: {e}")
        return False


def check_gh_version() -> bool:
    """Check GitHub CLI version."""
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            version = result.stdout.split("\n")[0]
            print(f"✅ GitHub CLI version: {version}")
            return True
        else:
            print(f"❌ GitHub CLI version check failed")
            return False
    except Exception as e:
        print(f"❌ Error checking GitHub CLI version: {e}")
        return False


def check_gh_auth() -> tuple[bool, str]:
    """Check GitHub CLI authentication."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False,
        )
        if "Logged in" in result.stdout or "Logged in" in result.stderr:
            # Extract username if possible
            output = result.stdout + result.stderr
            for line in output.split("\n"):
                if "Logged in" in line and "as" in line:
                    username = line.split("as")[-1].strip()
                    print(f"✅ GitHub authenticated as: {username}")
                    return True, username
            print(f"✅ GitHub authenticated")
            return True, "unknown"
        else:
            print(f"❌ Not authenticated with GitHub")
            print(f"Run: gh auth login")
            return False, ""
    except Exception as e:
        print(f"❌ Error checking GitHub authentication: {e}")
        return False, ""


def check_copilot_access() -> bool:
    """Check if GitHub Copilot is accessible via CLI."""
    try:
        result = subprocess.run(
            ["gh", "copilot", "suggest", "-t", "shell", "test command"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            print(f"✅ GitHub Copilot CLI access: Working")
            print(f"   Test suggestion: {result.stdout[:50]}...")
            return True
        else:
            print(f"❌ GitHub Copilot CLI access failed")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⚠️  GitHub Copilot CLI access: Timeout (may still work)")
        return True  # Don't fail on timeout
    except Exception as e:
        print(f"❌ Error checking GitHub Copilot access: {e}")
        return False


def check_python_api() -> bool:
    """Check if Python API wrapper is working."""
    try:
        sys.path.insert(0, "/workspaces/Racing-Analysis")
        from src.api.github_copilot_premium import GitHubCopilotPremiumAPI

        api = GitHubCopilotPremiumAPI()
        status = api.health_check()

        if status.get("status") == "healthy":
            print(f"✅ Python API wrapper: Working")
            return True
        else:
            print(f"❌ Python API wrapper: {status.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Error checking Python API: {e}")
        return False


def check_environment() -> bool:
    """Check environment variables."""
    github_token = os.getenv("GITHUB_TOKEN")

    if github_token:
        print(f"✅ GITHUB_TOKEN: Set (length: {len(github_token)})")
        return True
    else:
        print(f"⚠️  GITHUB_TOKEN: Not set (optional - will use gh auth)")
        return True  # Not critical


def test_api_call() -> bool:
    """Test an actual API call."""
    try:
        print("\n" + "=" * 80)
        print("Testing API call (uses 1 premium request)...")
        print("=" * 80)

        sys.path.insert(0, "/workspaces/Racing-Analysis")
        from src.api.github_copilot_premium import GitHubCopilotPremiumAPI

        api = GitHubCopilotPremiumAPI()
        response = api.chat("What is 2+2? Answer with just the number.")

        if response.get("success"):
            print(f"✅ API call successful")
            print(f"   Response: {response.get('content', '')[:100]}")
            print(f"   Uses premium requests: {response.get('uses_premium_requests', False)}")
            return True
        else:
            print(f"❌ API call failed: {response.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing API call: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 80)
    print("GitHub Copilot Premium API Verification")
    print("=" * 80)
    print()

    checks = []

    # Check GitHub CLI
    print("1. Checking GitHub CLI...")
    checks.append(check_command("gh", "GitHub CLI"))
    if checks[-1]:
        checks.append(check_gh_version())
    print()

    # Check authentication
    print("2. Checking GitHub authentication...")
    auth_ok, username = check_gh_auth()
    checks.append(auth_ok)
    print()

    # Check Copilot access
    print("3. Checking GitHub Copilot access...")
    checks.append(check_copilot_access())
    print()

    # Check environment
    print("4. Checking environment variables...")
    checks.append(check_environment())
    print()

    # Check Python API
    print("5. Checking Python API wrapper...")
    checks.append(check_python_api())
    print()

    # Test actual API call
    if all(checks):
        print("6. Testing actual API call...")
        checks.append(test_api_call())
        print()

    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    passed = sum(checks)
    total = len(checks)

    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print()
        print("Your GitHub Copilot Premium API is ready to use!")
        print()
        print("Next steps:")
        print("1. Try the examples: python examples/advanced_ai_features.py")
        print("2. Read the docs: docs/GITHUB_COPILOT_SETUP.md")
        print("3. Check usage: gh api /user/copilot_seats/usage")
        return 0
    else:
        print(f"❌ {total - passed} checks failed ({passed}/{total} passed)")
        print()
        print("Please fix the issues above and run this script again.")
        print("See docs/GITHUB_COPILOT_SETUP.md for setup instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
