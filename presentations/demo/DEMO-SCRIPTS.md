# Presentation Demo Script

## Combined Demo: Lifecycle in Action (Slide 9, ~2:30)

### Pre-flight check
- Terminal open with Claude Code in the **blog** repo
- `demo/demo-1-feature-request.txt` has the feature request ready
- Second terminal tab in `demo/demo-2-quality-gates/` with `ruff`, `basedpyright`, `pytest` installed (all via `uv`)
- `calculator.py` has intentional issues (formatting, unused imports, type errors, missing annotations)
- `tests/test_calculator.py` has a test that will fail (`test_divide_by_zero`)
- Clean git state (`git stash` anything in progress)

### Confirm issues exist (rehearsal only)
```bash
ruff format --check demo/demo-2-quality-gates/calculator.py
ruff check demo/demo-2-quality-gates/calculator.py
basedpyright demo/demo-2-quality-gates/calculator.py
python3 -m pytest demo/demo-2-quality-gates/tests/ -v
```

---

### Part 1: Spec Workflow (~1:30)

**1. Set the stage** (say aloud):
> "I want to add a callout shortcode to my Hugo blog. Instead of jumping into code, I'll let the lifecycle run."

**2. Invoke `/spec`**:
```
/spec
```
When prompted, paste the contents of `demo/demo-1-feature-request.txt`.

**3. Plan phase** — point out as it runs:
- "It's exploring the codebase first — reading layouts, custom.css, hugo.toml"
- "Now it's designing tasks — notice it found the Catppuccin palette in custom.css"
- "I get a plan with concrete tasks before any code is written"

**4. Approve the plan**:
- Read it briefly on screen
- "This looks right. I approve."
- (Approve when prompted)

**5. Implementation** — point out:
- "Now it's implementing — test first for each task"
- "Notice the TDD cycle: failing test, then implementation, then refactor"
- "I decided *what* to build. I approved the *plan*. The AI handled the *how*."

**Transition line**:
> "That's the judgment side — decisions and approval are mine, execution is automated. Now let's see the quality gates."

---

### Part 2: Quality Gates (~1:00)

**6. Switch to the quality-gates tab** (say aloud):
> "I have a Python module with issues. Let's see what happens when we try to commit."

**7. Show the code briefly**:
- Scroll through `calculator.py`
- "Formatting inconsistencies, unused imports, missing type annotations, a bug in divide"

**8. Invoke `/preflight`**:
```
/preflight
```

**9. Narrate the four gates**:
- **Format**: "First gate — Ruff auto-fixes spacing and style. This one's free."
- **Lint**: "Unused imports, code smells caught. Some auto-fixed, some flagged."
- **Type check**: "Basedpyright in strict mode. Missing annotations, type mismatches. AI fixes these."
- **Tests**: "One test fails — `divide(10, 0)` raises `ZeroDivisionError` instead of `ValueError`. AI adds the zero check, test passes."

**10. Landing line**:
> "Same bar, regardless of who wrote the code. The commit doesn't happen until all four gates pass. That's enforcement, not suggestion."

---

### Recovery

- If `/spec` stalls or errors: "This is a live system — sometimes the model needs a retry. The point is the workflow, not the speed."
- If plan is unexpected: adjust and approve — shows the human-in-the-loop is real
- If `/preflight` fixes everything too fast: "It fixed 15+ issues in seconds. The point isn't that I couldn't do this by hand — it's that it happens *every time*, automatically."
- If something unexpected breaks: fix live — demonstrates the feedback loop. "The system caught it. That's the point."

---

### General Tips

- **Font size**: 16pt+ in terminal, dark background (matches slide theme)
- **Terminal width**: ~100 columns max so audience can read
- **Pace**: Narrate what's happening as it runs — the audience can't read the terminal as fast as you can
- **Timing**: Part 1 can be cut short by approving the plan quickly and narrating the rest. Part 2 runs fast — the gates take seconds.
