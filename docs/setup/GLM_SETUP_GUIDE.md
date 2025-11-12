# Setting Up GLM 4.6 in VS Code

This guide will help you set up Zhipu AI's GLM 4.6 model for use in VS Code as an AI coding assistant.

## Overview

Since GitHub Copilot doesn't support custom model providers, we'll use the **Continue** extension, which allows you to use GLM 4.6 alongside or instead of Copilot.

## Prerequisites

- VS Code installed
- GLM Pro subscription with API access from Zhipu AI (https://open.bigmodel.cn/)
- Your GLM API key

## Setup Steps

### 1. Install Continue Extension

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "Continue"
4. Install the "Continue - Codestral, Claude, and more" extension
5. Reload VS Code if prompted

### 2. Get Your GLM API Key

1. Go to https://open.bigmodel.cn/
2. Log in with your account
3. Navigate to API Keys section
4. Create a new API key or copy your existing one
5. Keep this key secure!

### 3. Configure Continue with GLM

The configuration file has already been created at `.vscode/continue-config.json`.

**Update the API key:**

1. Open `.vscode/continue-config.json`
2. Replace all instances of `YOUR_GLM_API_KEY_HERE` with your actual GLM API key
3. Save the file

Alternatively, add it to your `.env` file:

```bash
GLM_API_KEY=your_actual_api_key_here
```

### 4. Available GLM Models

The configuration includes two models:

- **GLM-4-Plus**: Most capable, best for complex coding tasks
  - Context: 128K tokens
  - Best for: Complex refactoring, architecture design, debugging

- **GLM-4-Air**: Faster and cheaper
  - Context: 128K tokens
  - Best for: Quick completions, simple queries, autocomplete

### 5. Using Continue with GLM

Once configured, you can use Continue in several ways:

#### Chat Interface
- Press `Ctrl+L` (Windows/Linux) or `Cmd+L` (Mac) to open Continue chat
- Select GLM-4-Plus or GLM-4-Air from the model dropdown
- Ask questions, request code changes, etc.

#### Inline Editing
- Select code in the editor
- Press `Ctrl+I` (Windows/Linux) or `Cmd+I` (Mac)
- Type your instruction and hit Enter
- Continue will edit the code using GLM

#### Custom Commands
Pre-configured commands:
- `/test` - Generate unit tests for selected code
- `/doc` - Generate documentation for selected code

#### Tab Autocomplete
- Configured to use GLM-4-Air for fast completions
- Works like GitHub Copilot
- Just start typing and accept suggestions with Tab

### 6. VS Code Keyboard Shortcuts

| Action | Shortcut (Win/Linux) | Shortcut (Mac) |
|--------|---------------------|----------------|
| Open Continue Chat | Ctrl+L | Cmd+L |
| Inline Edit | Ctrl+I | Cmd+I |
| Accept Suggestion | Tab | Tab |
| Reject Suggestion | Esc | Esc |

### 7. Configuration Options

You can customize the Continue configuration in `.vscode/continue-config.json`:

```json
{
  "models": [
    {
      "title": "GLM-4-Plus",
      "provider": "openai",  // GLM API is OpenAI-compatible
      "model": "glm-4-plus",
      "apiBase": "https://open.bigmodel.cn/api/paas/v4",
      "apiKey": "YOUR_API_KEY",
      "contextLength": 128000
    }
  ]
}
```

### 8. Environment Variable Configuration

For better security, use environment variables:

1. Add to `.env`:
```bash
GLM_API_KEY=your_api_key_here
```

2. Update `continue-config.json` to reference it:
```json
{
  "models": [
    {
      "apiKey": "${GLM_API_KEY}"
    }
  ]
}
```

## GLM API Endpoints

- **Base URL**: `https://open.bigmodel.cn/api/paas/v4`
- **Compatible with**: OpenAI API format
- **Documentation**: https://open.bigmodel.cn/dev/api

## Available Models

| Model | Context | Use Case | Speed | Cost |
|-------|---------|----------|-------|------|
| glm-4-plus | 128K | Complex tasks | Medium | Higher |
| glm-4-0520 | 128K | General purpose | Medium | Medium |
| glm-4-air | 128K | Fast completions | Fast | Lower |
| glm-4-airx | 8K | Very fast | Fastest | Lowest |
| glm-4-flash | 128K | Balanced | Fast | Low |

## Troubleshooting

### Issue: Continue not responding
- Check your API key is correct
- Verify you have API credits remaining
- Check network connection to Zhipu AI servers

### Issue: Slow responses
- Try switching to GLM-4-Air or GLM-4-Flash
- Reduce context length if needed

### Issue: API errors
- Check your API key has necessary permissions
- Verify your subscription is active
- Check rate limits haven't been exceeded

### Issue: Continue extension not found
- Manually install from: https://marketplace.visualstudio.com/items?itemName=Continue.continue
- Or install via command line: `code --install-extension Continue.continue`

## Comparison: Continue vs GitHub Copilot

| Feature | GitHub Copilot | Continue + GLM |
|---------|---------------|----------------|
| Model | GPT-4 (fixed) | GLM-4 (customizable) |
| Cost | $10-20/month | Pay-per-use |
| Customization | Limited | Full control |
| Multiple models | No | Yes |
| Self-hosted | No | Possible |
| Context size | Limited | 128K tokens |

## Using Both Copilot and GLM

You can use both simultaneously:
- GitHub Copilot for inline suggestions
- Continue + GLM for chat and complex tasks
- Switch between them based on your needs

## Advanced: Custom Instructions

Add custom system instructions for GLM in `continue-config.json`:

```json
{
  "models": [
    {
      "title": "GLM-4-Plus",
      "systemMessage": "You are an expert Python developer specializing in racing analysis and machine learning. Always write clean, tested code with comprehensive docstrings.",
      "...": "..."
    }
  ]
}
```

## Next Steps

1. Install the Continue extension
2. Add your GLM API key to `.env`
3. Update `.vscode/continue-config.json` with your key
4. Press `Ctrl+L` / `Cmd+L` to start using GLM
5. Try the `/test` and `/doc` commands

## Resources

- GLM API Documentation: https://open.bigmodel.cn/dev/api
- Continue Documentation: https://continue.dev/docs
- VS Code Extensions: https://marketplace.visualstudio.com/

## Support

If you encounter issues:
1. Check the Continue extension logs in VS Code
2. Verify API key and credits
3. Review Zhipu AI service status
4. Check Continue GitHub issues: https://github.com/continuedev/continue

---

**Note**: This configuration uses GLM's OpenAI-compatible API, which means most OpenAI API features work with GLM models.
