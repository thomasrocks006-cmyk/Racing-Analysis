# GitHub Copilot Agent System

## Your Questions Answered

### Question 1: "How can I provide operating instructions to Codex in this environment?"

✅ **DONE** - I've created a complete system for you.

**Location:** `.github/COPILOT_INSTRUCTIONS.md`

This file contains standing instructions that make GitHub Copilot behave like Claude Sonnet 4.5:
- Announces plans before acting
- Shows BEFORE/AFTER code changes
- Explains reasoning (WHY not just WHAT)
- Makes incremental changes, not huge refactors
- Asks clarifying questions when needed
- Follows your project's existing patterns

**How to use it:**
- At the start of any GitHub Copilot session, paste:
  ```
  Read .github/COPILOT_INSTRUCTIONS.md and follow those instructions throughout this session.
  Then read dev/SESSION_NOTES.md and brief me on current context.
  ```

---

### Question 2: "Should we set up specialized agent skills for different tasks?"

✅ **YES - AND I'VE BUILT IT**

I've created 5 specialized skills, each with patterns, workflows, and best practices for different domains:

| Skill | Use For |
|-------|---------|
| **Data Engineering** | Building scrapers, validating data, designing ETL pipelines |
| **Model Development** | Engineering features, training models, optimization |
| **Analysis & Insights** | Exploratory analysis, statistical testing, reporting |
| **Integration & Orchestration** | Pipeline design, API integration, data flow coordination |
| **Testing & QA** | Unit/integration tests, code quality, performance testing |

**Location:** `.github/AGENT_SKILLS/`

**How to use:**
```
Use [skill-name] skill: [task description]

Examples:
- Use data-engineering skill: Create a scraper for Betfair odds
- Use model-development skill: Engineer features for win prediction
- Use testing-qa skill: Write comprehensive tests
- Use integration-orchestration skill: Connect scraper to pipeline
```

When you reference a skill, the agent:
1. Loads patterns specific to that domain
2. Reviews your project's existing code in that area
3. Follows your conventions and best practices
4. Returns code that fits naturally into your project

---

## What You Get

### 1. Operating Instructions
- File: `.github/COPILOT_INSTRUCTIONS.md`
- Makes agent behavior consistent and predictable
- Emphasizes planning, explanation, and incrementalism

### 2. Five Specialized Skills
- Location: `.github/AGENT_SKILLS/`
- Each skill has workflows, code patterns, and checklists
- Guides agent to produce domain-appropriate solutions

### 3. Session Brain File
- File: `dev/SESSION_NOTES.md`
- Persistent project memory across sessions
- Update it at end of each session to maintain context

### 4. Setup & Reference Guides
- `COPILOT_SETUP_GUIDE.md` - Complete walkthrough
- `AGENT_SKILLS_ARCHITECTURE.md` - Deep dive on design
- `COPILOT_QUICK_REFERENCE.md` - Bookmark this!
- `IMPLEMENTATION_COMPLETE.md` - This implementation
- `README_COPILOT_AGENT.md` - You're reading it!

---

## Quick Start

### Every Session: Start With This

```
Read .github/COPILOT_INSTRUCTIONS.md and follow those throughout this session.
Then read dev/SESSION_NOTES.md.

Give me:
1. One-paragraph project overview
2. Current sprint goal
3. Five specific TODOs for today
4. Any blockers or decisions needed

Do NOT start coding yet.
```

### During Coding: Use Skills

```
Use [skill-name] skill: [task description]

Show me a plan first. I'll say "OK" before you make changes.
```

### End of Session: Update Notes

```
Update dev/SESSION_NOTES.md with:
- Completed TODOs (mark ✅)
- New TODOs discovered
- What we accomplished
- Design decisions made
- Next steps
```

---

## Files Overview

```
✅ .github/COPILOT_INSTRUCTIONS.md
   → Standing operating manual for Copilot

✅ .github/AGENT_SKILLS/
   ├── README.md (skill index and overview)
   ├── data-engineering.md
   ├── model-development.md
   ├── analysis-insights.md
   ├── integration-orchestration.md
   └── testing-qa.md

✅ dev/SESSION_NOTES.md
   → Update this at the end of each session

✅ COPILOT_SETUP_GUIDE.md
   → Complete how-to guide

✅ AGENT_SKILLS_ARCHITECTURE.md
   → Design rationale and advanced usage

✅ COPILOT_QUICK_REFERENCE.md
   → Bookmark this! Quick prompts for common tasks

✅ IMPLEMENTATION_COMPLETE.md
   → Summary of what was built

✅ README_COPILOT_AGENT.md
   → This file
```

---

## Why This Design Works

### Without This System
```
You: "Help me create a scraper"
Agent: [Generic code, may miss error handling, skip tests]
Result: Code that doesn't fit your project's patterns
```

### With This System
```
You: "Use data-engineering skill: Create a scraper for Betfair"
Agent: [Loads data-engineering skill]
Agent: [Reviews your existing scrapers as templates]
Agent: [Includes proper error handling, rate limiting, tests]
Agent: [Code fits naturally into your project]
```

**The key difference:** The agent knows your project's patterns and conventions.

---

## Benefits

✅ **Claude-Like Planning** - Agent proposes plans before acting  
✅ **Transparent Decision-Making** - Shows BEFORE/AFTER and explains WHY  
✅ **Domain Expertise** - 5 specialized skills for different tasks  
✅ **Persistent Context** - Session brain file maintains project state  
✅ **Consistency** - Agent produces code aligned with your project  
✅ **Composability** - Skills work together for complex workflows  
✅ **Extensibility** - Easy to add new skills or update existing ones  

---

## Next Actions

1. **Read the setup guide**: `COPILOT_SETUP_GUIDE.md` (15 min read)
2. **Bookmark the quick reference**: `COPILOT_QUICK_REFERENCE.md`
3. **Start your first session**: Use the "Quick Start" prompt above
4. **Experiment with skills**: Try different skills for different tasks
5. **Keep SESSION_NOTES.md updated**: Maintain context between sessions

---

## FAQ

**Q: Do I have to follow these instructions exactly?**  
A: No! They're templates. Customize them to match how you work.

**Q: Can I add new skills?**  
A: Yes! Follow the template in `.github/AGENT_SKILLS/README.md` to create new ones.

**Q: How often should I update SESSION_NOTES.md?**  
A: At the end of each coding session (even if just 30 min of work).

**Q: What if the agent doesn't follow the instructions?**  
A: Paste the instructions directly into the chat instead of referencing the file.

**Q: Can I use multiple skills at once?**  
A: Yes! You can say "First use skill A, then use skill B..."

---

## Status

✅ **Complete and Ready to Use**

All files created, documented, and pushed to your repository.

**Branch:** `pr/copilot-swe-agent/2`

---

## Start Now

Open GitHub Copilot and paste:

```
Read .github/COPILOT_INSTRUCTIONS.md and follow those throughout this session.
Then read dev/SESSION_NOTES.md and brief me on current context.
```

Enjoy your Claude-like Copilot! 🚀
