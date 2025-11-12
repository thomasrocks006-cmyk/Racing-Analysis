# GitHub Copilot API Setup Guide

Complete guide to using your GitHub Copilot Pro Plus premium requests programmatically.

## 📋 Prerequisites

- ✅ GitHub Copilot Pro Plus subscription (you have 1500 premium requests)
- ✅ VS Code with GitHub Copilot extension installed
- ✅ Python 3.11+ environment

## 🚀 Installation

### Step 1: Install the Copilot API Server Extension

The Copilot API Server extension is already prepared in your workspace:

```bash
# From VS Code:
# 1. Open Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
# 2. Type "Extensions: Install from VSIX..."
# 3. Navigate to: .vscode/extensions/copilot-api-server/

# Alternative: Install dependencies manually
cd .vscode/extensions/copilot-api-server/
npm install
```

### Step 2: Restart VS Code

After installing the extension, restart VS Code to activate it.

### Step 3: Start the API Server

The server should auto-start when VS Code opens. If not:

```
Command Palette > "Start Copilot API Server"
```

Or use the status bar button.

### Step 4: Verify Installation

```python
from src.api.copilot_api import GitHubCopilotAPI

api = GitHubCopilotAPI()
print("Server healthy:", api.health_check())
print("Available models:", api.list_models())
```

## 📖 Usage

### Single Request

```python
from src.api.copilot_api import GitHubCopilotAPI

api = GitHubCopilotAPI()
response = api.chat("Explain gradient boosting for racing prediction")

if response['success']:
    print(response['content'])
```

### Three Agent Pattern (Optimal Premium Request Usage)

```python
from src.api.copilot_api import MultiAgent

# Create 3 specialized racing analysts
agents = MultiAgent.create_racing_analysts()

# Query all agents concurrently
results = agents.analyze(
    "Should I use CatBoost or LightGBM for horse racing prediction?"
)

# Synthesize their insights
synthesis = agents.synthesize("Should I use CatBoost or LightGBM?", results)
print(synthesis['content'])
```

### Custom Agents

```python
configs = [
    {
        "name": "DataScientist",
        "system_prompt": "You are a data scientist specializing in sports analytics..."
    },
    {
        "name": "DomainExpert",
        "system_prompt": "You are a horse racing expert with 20 years experience..."
    },
    {
        "name": "MLEngineer",
        "system_prompt": "You are an ML engineer building production models..."
    }
]

agents = MultiAgent.create_custom(configs)
results = agents.analyze("How should I structure my training pipeline?")
```

### Conversational Agent

```python
from src.api.copilot_api import CopilotAgent

agent = CopilotAgent(
    name="RacingTutor",
    system_prompt="You are a patient ML tutor for racing prediction."
)

# Multi-turn conversation
agent.chat("What is feature engineering?")
agent.chat("Give me 3 examples for racing data")
agent.chat("How do I prevent data leakage?")

# View conversation history
print(f"Messages: {len(agent.conversation_history)}")
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Python API    │  ← Your code (copilot_api.py)
│  GitHubCopilot  │
│     API         │
└────────┬────────┘
         │ HTTP (localhost:8765)
         │
┌────────▼────────┐
│   VS Code       │
│   Extension     │  ← copilot-api-server
│  (Express.js)   │
└────────┬────────┘
         │ vscode.lm API
         │
┌────────▼────────┐
│  GitHub Copilot │  ← Your premium requests
│  Language Model │
│      API        │
└─────────────────┘
```

## 🎯 Pre-built Agent Teams

### Racing Analysts (3 agents)
```python
agents = MultiAgent.create_racing_analysts()
# - FeatureEngineer: Feature engineering specialist
# - ModelArchitect: ML model selection and tuning
# - DomainExpert: Racing strategy and qualitative insights
```

### Code Reviewers (3 agents)
```python
agents = MultiAgent.create_code_reviewers()
# - SecurityReviewer: Security vulnerabilities
# - PerformanceReviewer: Performance optimization
# - QualityReviewer: Code quality and maintainability
```

## 🔧 Configuration

### Default Settings

The extension auto-starts on port 8765. To customize:

```json
// .vscode/settings.json
{
    "copilot-api-server.port": 8765,
    "copilot-api-server.autoStart": true
}
```

### Change Model

```python
api = GitHubCopilotAPI(model="gpt-4o")  # Default
api = GitHubCopilotAPI(model="gpt-4")
api = GitHubCopilotAPI(model="gpt-3.5-turbo")
```

### Adjust Temperature

```python
response = api.chat(
    "Your prompt",
    temperature=0.2  # More deterministic
)
```

## 🧪 Testing

Run the example script:

```bash
python examples/copilot_api_example.py
```

This demonstrates:
- ✅ Single request
- ✅ Three agent analysis
- ✅ Custom agents
- ✅ Conversational agents

## 📊 Premium Request Management

### Your Allocation
- **Total**: 1500 premium requests/month (Pro Plus)
- **3 agents concurrently**: 500 queries with comprehensive analysis
- **Single agent**: 1500 individual queries

### Best Practices

1. **Use 3-agent pattern for important decisions**
   ```python
   agents = MultiAgent.create_racing_analysts()
   results = agents.analyze("Complex question requiring multiple perspectives")
   ```

2. **Use single agent for routine queries**
   ```python
   api = GitHubCopilotAPI()
   response = api.chat("Quick factual question")
   ```

3. **Track usage**
   ```python
   # Each api.chat() call = 1 premium request
   # agents.analyze() with 3 agents = 3 premium requests
   # agents.synthesize() = 1 additional premium request
   ```

## 🐛 Troubleshooting

### Server Not Running

**Problem**: `health_check()` returns `False`

**Solution**:
```
1. Open Command Palette (Cmd+Shift+P)
2. Type "Start Copilot API Server"
3. Check VS Code status bar for "Copilot API: Running ✓"
```

### Connection Refused

**Problem**: `ConnectionError: Could not connect to Copilot API Server`

**Solution**:
```bash
# Check if extension is installed
# VS Code > Extensions > Search "Copilot API Server"

# Restart VS Code
# Extension auto-starts on launch
```

### No Models Available

**Problem**: `list_models()` returns empty list

**Solution**:
- Ensure GitHub Copilot extension is active
- Sign in to GitHub account in VS Code
- Verify Copilot Pro Plus subscription is active

### Rate Limiting

**Problem**: Error about quota exceeded

**Solution**:
- You have 1500 premium requests/month
- Check usage in GitHub account settings
- Wait for monthly reset
- Use gpt-3.5-turbo for non-critical queries (may have different limits)

## 📚 Examples

See `examples/copilot_api_example.py` for comprehensive examples:

```bash
python examples/copilot_api_example.py
```

## 🔗 Integration with Racing Analysis

### Feature Engineering Pipeline

```python
# Get multi-agent input on feature design
agents = MultiAgent.create_racing_analysts()
results = agents.analyze("""
Given race data with horse speed ratings, track conditions, and jockey stats,
what derived features should I create for gradient boosting models?
""")

# Use FeatureEngineer's response for implementation
feature_ideas = results['FeatureEngineer']['content']
```

### Model Selection

```python
# Get expert opinions on model choice
agents = MultiAgent.create_racing_analysts()
results = agents.analyze("""
For racing prediction with categorical features (horse, jockey, trainer)
and numerical features (speed ratings, times), should I use:
- CatBoost (native categorical support)
- LightGBM (faster training)
- XGBoost (most popular)
""")

synthesis = agents.synthesize("Model selection question", results)
print(synthesis['content'])
```

### Code Review

```python
# Review your implementation
agents = MultiAgent.create_code_reviewers()

code = open('src/features/engineering.py').read()
results = agents.analyze(f"Review this code:\n\n{code[:2000]}")

# Check each reviewer's feedback
print(results['SecurityReviewer']['content'])
print(results['PerformanceReviewer']['content'])
print(results['QualityReviewer']['content'])
```

## 🎓 Tips for Effective Multi-Agent Use

1. **Diverse Perspectives**: Use agents with different expertise areas
2. **Specific Roles**: Give agents clear, distinct system prompts
3. **Parallel Execution**: `analyze()` runs agents concurrently (fast)
4. **Synthesis**: Always synthesize results for actionable conclusion
5. **Conversation History**: Single agents remember context across calls

## 📞 Support

- Extension code: `.vscode/extensions/copilot-api-server/`
- Python API: `src/api/copilot_api.py`
- Examples: `examples/copilot_api_example.py`
- GitHub Copilot docs: https://docs.github.com/copilot

## ✅ Quick Start Checklist

- [ ] Extension installed in VS Code
- [ ] VS Code restarted
- [ ] Server running (check status bar)
- [ ] `api.health_check()` returns `True`
- [ ] `examples/copilot_api_example.py` runs successfully
- [ ] Ready to use 1500 premium requests! 🚀
