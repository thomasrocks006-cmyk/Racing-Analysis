# GitHub Copilot Setup Guide

This guide explains how to use the specialized agent instructions and skills in this repository.

## 1. Operating Instructions

### Location
`.github/COPILOT_INSTRUCTIONS.md`

### What It Does
This file contains standing instructions for GitHub Copilot to follow throughout your session. It tells the agent to:
- Summarize requests before acting
- Propose a plan before making changes
- Show BEFORE/AFTER for code changes
- Maintain TODO lists
- Follow project patterns and conventions

### How to Use

**Option A: Paste at Start of Each Session**
Copy the content of `.github/COPILOT_INSTRUCTIONS.md` and paste it into a new Copilot chat at the start of your coding session. The agent will follow these rules for the entire session.

**Option B: Reference in Workspace (Recommended)**
At the start of a new chat, paste this one-liner:
```
Read .github/COPILOT_INSTRUCTIONS.md and follow those instructions throughout this session. 
Then read dev/SESSION_NOTES.md and brief me on current context.
```

This tells the agent to:
1. Load the operating instructions
2. Review the session notes
3. Brief you on the current project state

## 2. Specialized Agent Skills

### Location
`.github/AGENT_SKILLS/` (5 specialized skill files)

### Available Skills

1. **Data Engineering** - Build scrapers, validate data, design pipelines
2. **Model Development** - Feature engineering, model training, optimization
3. **Analysis & Insights** - EDA, statistical testing, reporting
4. **Integration & Orchestration** - Pipeline design, API integration, error handling
5. **Testing & QA** - Unit/integration tests, code quality, performance

### How to Use

**Format:**
```
Use [SKILL_NAME] skill: [TASK_DESCRIPTION]
```

**Examples:**
```
Use data-engineering skill: Create a new scraper for Betfair odds

Use model-development skill: Build features for win prediction model

Use testing-qa skill: Write comprehensive tests for the GraphQL scraper

Use integration-orchestration skill: Connect the scraper output to feature engineering pipeline

Use analysis-insights skill: Analyze which gear changes improve performance
```

**Multiple Skills in One Session:**
```
First, use data-engineering skill: Create new scraper for [source]
Then, use testing-qa skill: Add unit and integration tests
Then, use integration-orchestration skill: Integrate into main pipeline
Finally, use analysis-insights skill: Create report on data quality
```

## 3. Session Notes Brain File

### Location
`dev/SESSION_NOTES.md`

### What It Does
Acts as your project's "session brain" - a persistent memory file that the agent refers to for:
- Current sprint goals
- Active TODO list
- Design decisions and constraints
- Completed work
- Next steps

### How to Update

At the end of each session:
```
Update dev/SESSION_NOTES.md with:
- Completed tasks (move to "Completed Tasks")
- New TODOs discovered
- Design decisions made
- Next steps for future sessions
```

At the start of each session:
```
Read dev/SESSION_NOTES.md to understand:
- What we're working on
- Design constraints
- What's already done
- What's next
```

## 4. Recommended Workflow

### Start a New Session

1. Open GitHub Copilot chat
2. Paste:
   ```
   Read .github/COPILOT_INSTRUCTIONS.md and follow those throughout this session.
   Then read dev/SESSION_NOTES.md to understand project context.
   
   Based on the session notes, give me:
   - 1-paragraph project overview
   - Current sprint goal
   - 5 specific TODOs we should tackle today
   - Any blockers or decisions needed
   
   Do NOT start coding yet. I'll review this first.
   ```

3. Review the agent's summary
4. Agree on which TODOs to tackle
5. As you work, reference skills:
   ```
   Use [SKILL_NAME] skill: [TASK]
   ```

### End Session

Before closing, update `dev/SESSION_NOTES.md`:
```
Update dev/SESSION_NOTES.md:
- Mark completed TODOs as ✅
- Add any new blockers or decisions
- Summarize what was accomplished
- Note any follow-up work needed
- Update "Next Steps"
```

## 5. Example Session

### Start
```
Agent: Read .github/COPILOT_INSTRUCTIONS.md and follow those throughout this session.
Then read dev/SESSION_NOTES.md and brief me on current context.

📋 RACING-ANALYSIS PROJECT
Current goal: Improve data pipeline reliability
Sprint focus: Add gear change detection to scraper

✅ Completed: GraphQL scraper (14 tests pass)
🔄 In progress: Integrate Betfair odds
📋 Next: Add gear change parsing

Blockers: None
Decisions needed: Should we cache scraper results?
```

### During Session
```
Use data-engineering skill: Add gear change parsing to racing_com_graphql.py

[Agent provides plan, implements changes, shows diffs]

Use testing-qa skill: Write tests for new gear change parsing

[Agent writes tests and verifies they pass]

Use integration-orchestration skill: Connect gear changes to feature pipeline

[Agent shows how data flows through pipeline]
```

### End Session
```
Update dev/SESSION_NOTES.md with completed work and next steps.
```

## 6. Tips for Best Results

### ✅ Do This
- Be specific: "Create the event_scheduler.py module with..." instead of "Build the scheduler"
- Use skills: Reference the specialized skills for domain-specific knowledge
- Ask for plans: "Show me a plan first, then we'll approve before coding"
- Read documents: Refer agent to ARCHITECTURE.md, DESIGN_DECISIONS.md, etc.
- Update session notes: Keep the "brain file" current for context continuity

### ❌ Don't Do This
- Vague requests: "Fix the pipeline" → instead "Fix the race data validation in pipeline"
- Skip plans: Don't ask agent to code immediately, get a plan first
- Ignore skills: Each skill has best practices and patterns you should follow
- Leave notes stale: Outdated session notes lose context value
- Multiple big tasks: Focus on 1-3 things per session for better results

## 7. Customizing for Your Style

The instructions and skills are templates. You can:

### Modify COPILOT_INSTRUCTIONS.md for your preferences
- Change planning steps
- Add/remove communication preferences
- Adjust the style guidance

### Create new agent skills
- Add skills for common patterns in your project
- Document domain-specific patterns and practices
- Share across team

### Update SESSION_NOTES.md frequently
- Use it as your project dashboard
- Reference it in every chat
- Keep it in sync with actual work

## 8. Troubleshooting

### Agent isn't following instructions
→ Paste the instructions directly into the chat instead of referencing the file

### Agent keeps jumping ahead without planning
→ Add this to your request: "First, propose a 5-step plan. Wait for 'OK' before making any changes."

### Agent forgets context between messages
→ Reference `dev/SESSION_NOTES.md` again: "Refer back to SESSION_NOTES.md to remind yourself of constraints"

### Skills don't seem to apply
→ Make sure you're using the exact format: "Use [skill-name] skill: [task]"

### Changed too many files at once
→ Use "Roll back to plan and make ONE change at a time" or check git diff

## 9. Next Steps

1. ✅ You now have operating instructions in place
2. ✅ You have 5 specialized agent skills ready
3. ✅ You have a session brain file to maintain context
4. Start your first session with the new setup:
   ```
   Read .github/COPILOT_INSTRUCTIONS.md and follow those throughout this session.
   Then read dev/SESSION_NOTES.md.
   ```
5. Reference skills as you work
6. Update session notes at end of day

---

**Questions?** Check the individual skill files or COPILOT_INSTRUCTIONS.md for more details on specific domains.
