# Copilot Agent Quick Reference Card

## 🚀 START SESSION

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

---

## 💡 USE SKILLS

**Format:**

```
Use [skill-name] skill: [task description]
```

**Available Skills:**

- `data-engineering` - Scrapers, validation, ETL
- `model-development` - Features, training, optimization
- `analysis-insights` - EDA, statistics, reporting
- `integration-orchestration` - Pipelines, data flow, APIs
- `testing-qa` - Tests, code quality, performance

**Examples:**

```
Use data-engineering skill: Create a scraper for Betfair live odds

Use model-development skill: Engineer features for win prediction

Use testing-qa skill: Write comprehensive tests for the scraper

Use integration-orchestration skill: Connect scraper to feature pipeline

Use analysis-insights skill: Analyze which venues have best data completeness
```

---

## 📝 END SESSION

```
Update dev/SESSION_NOTES.md:
- Mark completed TODOs as ✅
- Add any new TODOs discovered
- Summarize what was accomplished
- Note any design decisions made
- Update "Next Steps"
```

---

## 📚 KEY FILES

| File | Purpose |
|------|---------|
| `.github/COPILOT_INSTRUCTIONS.md` | Standing operating manual |
| `.github/AGENT_SKILLS/` | 5 specialized skill guides |
| `dev/SESSION_NOTES.md` | Session brain file (update each session) |
| `COPILOT_SETUP_GUIDE.md` | Complete setup walkthrough |
| `AGENT_SKILLS_ARCHITECTURE.md` | Design rationale |

---

## ⚡ TIPS & TRICKS

### Get a Plan First

```
Use [skill] skill: [task]

Show me a 5-step plan first. I'll say "OK" before you make changes.
```

### Ask Before Big Changes

```
Can you show me what would change? I want to review before you proceed.
```

### Combine Multiple Skills

```
First, use analysis-insights skill: Analyze X
Then, use model-development skill: Build features for Y
Then, use testing-qa skill: Write tests
```

### Maintain Context

```
Refer back to dev/SESSION_NOTES.md to remind yourself of constraints and decisions.
```

### Force Incremental Changes

```
Make ONE change at a time. Show me the diff. I'll approve before next change.
```

---

## 🔧 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Agent isn't following instructions | Paste instructions directly into chat |
| Agent skipped planning | Add: "Show plan first. Wait for 'OK' before coding." |
| Agent forgot context | Reference: "Read dev/SESSION_NOTES.md again" |
| Agent isn't using right patterns | Use exact format: "Use [skill-name] skill: [task]" |
| Too many files changed at once | Say: "Roll back. Make ONE change at a time." |

---

## 📊 WORKFLOWS

### Add New Feature

```
1. Use analysis-insights skill: Understand the problem
2. Use model-development skill: Design the feature
3. Use testing-qa skill: Plan the tests
4. Use data-engineering skill: Build data layer
5. Use integration-orchestration skill: Connect everything
```

### Fix Bug

```
1. Use integration-orchestration skill: Trace the data flow
2. Use analysis-insights skill: Find where it breaks
3. Use testing-qa skill: Write test to reproduce
4. Use [appropriate skill]: Implement fix
5. Update dev/SESSION_NOTES.md with what we learned
```

### Debug Failing Code

```
Use testing-qa skill: Debug the failing test

[Show output, check assumptions, add debugging]

Keep going until test passes.
```

---

## 📌 OPERATING PRINCIPLES

✅ **Always plan before acting** - "Show me a plan first"
✅ **Show diffs and explain** - "Why did we make that change?"
✅ **Make small changes** - "One file at a time"
✅ **Update session notes** - Keep context alive
✅ **Use the right skill** - Different tasks, different patterns
✅ **Ask for approval** - "Is this approach OK?"

---

## 🎯 SUCCESS CHECKLIST

Before ending a session:

- [ ] Updated dev/SESSION_NOTES.md with completed work
- [ ] Marked completed TODOs as ✅
- [ ] Noted any new TODOs discovered
- [ ] Documented design decisions made
- [ ] Listed next steps for future sessions
- [ ] All changes are committed to git
- [ ] Pushed to cloud (git push)

---

## 💬 COMMON PHRASES

**Request a plan:**

```
Show me a [number]-step plan first. Wait for my "OK" before making changes.
```

**Before refactoring:**

```
What would this refactor affect? Show me the scope before proceeding.
```

**For incrementalism:**

```
Make one small change. Show the diff. I'll approve before the next change.
```

**To fix context:**

```
Refer back to dev/SESSION_NOTES.md to remember our constraints and decisions.
```

**To force patience:**

```
This is complex. Let's break it into steps. Show each step before implementing.
```

---

## 🚀 START RIGHT NOW

1. Open GitHub Copilot in VS Code
2. Paste the "START SESSION" prompt above
3. Agent will brief you on project state
4. Pick a TODO from the list
5. Say: "Use [skill] skill: [task description]"
6. Enjoy planning, transparency, and incremental progress!

---

**Bookmark this card.** Reference it in every session! 🎯
