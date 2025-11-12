# GitHub Copilot Premium API Setup

This guide shows how to use your **GitHub Copilot Pro Plus premium requests (1500/month)** for multi-agent task execution.

## What You Get

- **1500 premium requests/month** from GitHub Copilot Pro Plus
- Multi-agent task execution using GitHub Copilot
- Each agent counts as 1 premium request
- Task synthesis counts as 1 additional premium request

## How It Works

```python
from src.api.task_executor import execute_multi_agent_task

# This uses 3 agents + 1 synthesis = 4 premium requests
task = execute_multi_agent_task(
    description="Design a feature engineering pipeline",
    subtasks=[
        {"agent": "DataArchitect", "task": "Design data flow"},
        {"agent": "FeatureEngineer", "task": "List key features"},
        {"agent": "MLEngineer", "task": "Recommend preprocessing"},
    ],
    max_agents=3,
)
```

## Prerequisites

### 1. GitHub CLI Installation

The GitHub Copilot API is accessed through GitHub CLI (`gh`):

```bash
# Check if installed
gh --version

# If not installed, install it:
# For Debian/Ubuntu
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### 2. GitHub Authentication

Authenticate GitHub CLI with your account:

```bash
# Authenticate
gh auth login

# Select:
# - GitHub.com
# - HTTPS
# - Login with a web browser (or paste token)

# Verify authentication
gh auth status

# Should show: ✓ Logged in to github.com as <your-username>
```

### 3. Verify Copilot Access

```bash
# Test Copilot CLI access
gh copilot suggest -t shell "list files in current directory"

# Should return a shell command suggestion
# This counts as 1 premium request
```

## Setup Steps

### 1. Install GitHub CLI (if not already installed)

```bash
cd /workspaces/Racing-Analysis
make install-gh-cli  # Will be added to Makefile
```

### 2. Set Environment Variables

Add to your `.env` file:

```bash
# GitHub authentication (obtained from gh auth status)
GITHUB_TOKEN=your_github_token_here

# Optional: Track usage
GITHUB_COPILOT_PREMIUM_LIMIT=1500  # Your monthly limit
```

Get your token from:
```bash
gh auth token
```

### 3. Verify Setup

```bash
python scripts/verify_github_copilot.py
```

Should output:
```
✅ GitHub CLI installed: gh version X.X.X
✅ GitHub authenticated as: <your-username>
✅ GitHub Copilot access: Working
✅ Premium requests API: Ready

Your GitHub Copilot Pro Plus plan:
- Premium requests: 1500/month
- Requests used this month: X
- Requests remaining: X
```

## Usage Examples

### Basic Multi-Agent Task

```python
from src.api.task_executor import execute_multi_agent_task

task = execute_multi_agent_task(
    description="Analyze horse racing data",
    subtasks=[
        {"agent": "Analyst", "task": "Identify key patterns"},
        {"agent": "Modeler", "task": "Recommend model architecture"},
    ],
    max_agents=2,
)

print(task.synthesis)  # Uses 2 + 1 = 3 premium requests
```

### Auto-Decompose Tasks

```python
# Let GitHub Copilot break down the task automatically
task = execute_multi_agent_task(
    description="Build a complete feature engineering pipeline for racing data"
    # No subtasks - will auto-decompose using 1 premium request
    # Then execute agents + synthesis
)
```

### Direct API Access

```python
from src.api.github_copilot_premium import GitHubCopilotPremiumAPI

api = GitHubCopilotPremiumAPI()

# Check if working
status = api.health_check()
print(status)  # Should be {"status": "healthy", ...}

# Make a request
response = api.chat("What's the best way to engineer time-based features?")
print(response["content"])  # Uses 1 premium request
```

### Individual Agent

```python
from src.api.github_copilot_premium import GitHubCopilotAgent

agent = GitHubCopilotAgent(
    name="FeatureEngineer",
    system_prompt="You are an expert in feature engineering for time series"
)

response = agent.chat("How should I handle missing data?")
print(response["content"])  # Uses 1 premium request
```

## Tracking Usage

Your premium requests are tracked by GitHub:

1. **View in VS Code**: GitHub Copilot extension shows usage
2. **View in GitHub**: Settings → Copilot → Usage
3. **Check via CLI**:
   ```bash
   gh api /user/copilot_seats/usage
   ```

## Rate Limits

- **Monthly limit**: 1500 premium requests
- **Concurrent requests**: Limited by GitHub (typically 3-5)
- **Request timeout**: 60 seconds per request

## Cost Optimization

### Multi-Agent Execution
- 3 agents + synthesis = 4 requests
- 5 agents + synthesis = 6 requests
- Auto-decompose adds 1 request upfront

### Best Practices
1. **Batch similar tasks**: Don't create separate tasks for related work
2. **Use auto-decompose wisely**: Only when needed (costs 1 extra request)
3. **Cache results**: Store agent outputs for reuse
4. **Monitor usage**: Check remaining requests before large operations

### Example: Efficient Usage

```python
# ❌ Inefficient: 6 separate requests
for question in questions:
    api.chat(question)

# ✅ Efficient: 1 request
combined = "Answer these questions:\n" + "\n".join(questions)
api.chat(combined)
```

## Troubleshooting

### "GitHub CLI not found"
```bash
which gh  # Should show path
gh --version  # Should show version
# If not installed, see Installation section above
```

### "Not authenticated"
```bash
gh auth status  # Check status
gh auth login  # Re-authenticate
gh auth token  # Get token for .env
```

### "Copilot suggest failed"
```bash
# Check Copilot subscription
gh api /user/copilot_seats

# Should show your Pro Plus subscription
```

### "Rate limit exceeded"
You've used your 1500 monthly requests. Check usage:
```bash
gh api /user/copilot_seats/usage
```

### "Connection timeout"
- Check internet connection
- GitHub API may be down: https://www.githubstatus.com/
- Increase timeout in code: `timeout=120` in subprocess call

## Architecture

```
Your Code
    ↓
GitHubCopilotPremiumAPI (src/api/github_copilot_premium.py)
    ↓
GitHub CLI (gh copilot suggest)
    ↓
GitHub Copilot API (counts premium requests)
    ↓
Response
```

## API Reference

### `GitHubCopilotPremiumAPI`
Main API wrapper for GitHub Copilot premium requests.

**Methods:**
- `chat(prompt, system_prompt=None)` - Send a message (1 premium request)
- `health_check()` - Verify API is working (0 requests)

### `GitHubCopilotAgent`
Individual agent using GitHub Copilot.

**Methods:**
- `chat(prompt)` - Agent sends message (1 premium request)

### `TaskExecutor`
Multi-agent task execution framework.

**Methods:**
- `create_task(description, subtasks=None)` - Create task (0 requests if subtasks provided, 1 if auto-decompose)
- `execute_task(task)` - Execute task (N agents + 1 synthesis requests)

### `execute_multi_agent_task()`
Quick function for task execution.

**Parameters:**
- `description` - Task description
- `subtasks` - Optional list of {"agent": name, "task": description}
- `max_agents` - Max concurrent agents (default 5)

**Returns:** Task with results and synthesis

**Premium Requests Used:**
- Auto-decompose (if no subtasks): 1 request
- Each agent: 1 request
- Synthesis: 1 request
- **Total**: 1 (if auto) + N agents + 1 = N+2 or N+1 requests

## Comparison with Other APIs

| Feature | GitHub Copilot | OpenAI | Anthropic |
|---------|---------------|---------|-----------|
| Cost | Included in Pro Plus | Pay per token | Pay per token |
| Limit | 1500 requests/month | Unlimited (paid) | Unlimited (paid) |
| Model | GPT-4 based | GPT-4o, o1, etc | Claude 3.5, 4 |
| Use Case | Coding, tech tasks | General purpose | Long context |

For this project, **GitHub Copilot premium requests are used for multi-agent execution** as they're already included in your subscription.

## Next Steps

1. ✅ Install GitHub CLI
2. ✅ Authenticate with GitHub
3. ✅ Verify Copilot access
4. ✅ Run verification script
5. ✅ Try the examples
6. 🚀 Build your multi-agent workflows

## Support

- **GitHub Copilot docs**: https://docs.github.com/copilot
- **GitHub CLI docs**: https://cli.github.com/manual/
- **This project's examples**: `/workspaces/Racing-Analysis/examples/advanced_ai_features.py`
