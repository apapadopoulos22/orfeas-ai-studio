# BOB AI & Reasoning Quick Reference Card

**Print this or bookmark for daily use!**

---

## 🎯 3 Core Reasoning Principles

### Principle 1: Transparency

**Always explain: WHAT, WHY, HOW, WHAT could go wrong, HOW to verify**

```
✅ DO THIS:
  WHAT: Missing closing brace in template
  WHY: Typo during editing
  HOW: Change ${progre" to ${progressData.progress}%
  RISK: Breaks progress bar rendering
  VERIFY: Bar renders with correct percentage

❌ NOT THIS:
  "Fix template error"
```

### Principle 2: Root Cause

**Find the actual problem, not the symptom**

```
❌ SYMPTOM FIX:
  Error: Function undefined
  Fix: Move function down in file

✅ ROOT CAUSE FIX:
  Symptom: Function called before definition
  Cause: HTML body executes before <head> loads
  Real fix: Move function to <head>
```

### Principle 3: Evidence-Based

**Collect evidence FOR and AGAINST each decision**

```
DECISION: GPU or CPU fallback?

FOR GPU:
✓ GPU available
✓ VRAM sufficient (24GB > 6GB needed)
✓ Previous generation worked
✓ No thermal issues

AGAINST GPU:
✗ OOM error last job
✓ Memory not cleaned up
✓ xformers unstable on Windows

→ Use GPU with pre-check & fallback
→ Confidence: 85%
```

---

## 🛡️ 3 Error Patterns (Learn from Past Mistakes)

### Pattern 1: Import-Time Configuration

**Problem:** Libraries read env vars during import, not runtime

```python
# ❌ BREAKS
import xformers  # Crashes - XFORMERS_DISABLED not set

# ✅ WORKS
os.environ['XFORMERS_DISABLED'] = '1'  # SET FIRST
import xformers  # Now safe
```

**Prevention:** Set all env vars BEFORE any imports

---

### Pattern 2: Inline Styles

**Problem:** `style="width: 0%"` hides accessibility/linting issues

```html
<!-- ❌ WRONG -->
<div style="width: 0%">Memory</div>

<!-- ✅ RIGHT -->
<div class="progress-fill-bar">Memory</div>

<style>
  .progress-fill-bar {
    width: 0%;
    transition: width 0.3s ease;
  }
</style>
```

**Prevention:** Use `validate_html_css.py` before commits

---

### Pattern 3: Missing Type Hints

**Problem:** Untyped functions cause 5+ cascading errors in IDE

```python
# ❌ WRONG - 11 type errors
def extract_style_properties(element):
    properties = {}  # Unknown type
    return properties

# ✅ RIGHT - 0 type errors
from typing import Dict

def extract_style_properties(element: str) -> Dict[str, str]:
    properties: Dict[str, str] = {}
    return properties
```

**Prevention:** Add type hints from day 1

---

## 🤖 BOB AI Diagnostic Decision Tree

**Use when stuck on a problem**

```
ERROR OCCURS
  ↓
  1️⃣ IMPORT ERROR?
     → Check env vars FIRST (Pattern 1)
     → grep "os.environ" in modules
     ↓
  2️⃣ RENDERING ERROR?
     → Check HTML structure
     → Function defined before use?
     → Template syntax valid? (${var})
     → CSS classes used? (not inline styles)
     ↓
  3️⃣ MEMORY ERROR?
     → Check GPU/VRAM
     → Pre-check before job? (gpu_manager)
     → Cleanup after job? (torch.cuda.empty_cache)
     → Fallback processor? (graceful degradation)
     ↓
  4️⃣ WEBSOCKET ERROR?
     → Check subscriptions
     → Client joined room? (subscribe_to_job)
     → Server emitting to room? (socketio.emit(..., room=id))
     → Heartbeat working? (ping/pong)
     ↓
  5️⃣ STILL STUCK?
     → Check Common Issues Table
     → Read .github/copilot-instructions-full.md
```

---

## 📦 4 Pattern Sets (Proven Solutions)

### Set A: Configuration & Initialization

```
✓ Set env vars BEFORE imports
✓ Use lazy loading (not preload)
✓ Thread-safe singletons with locks
✓ Validate config early, fail fast
```

### Set B: Resource Management

```
✓ Pre-check before allocating (VRAM check)
✓ Try block → Execute → Finally: cleanup
✓ Graceful degradation (GPU → CPU fallback)
✓ Monitor resource usage continuously
```

### Set C: Communication & Events

```
✓ WebSocket rooms for subscriptions
✓ Targeted delivery, NOT global broadcast
✓ Heartbeat for connection health
✓ JSON serialization always
```

### Set D: Error Handling

```
✓ Catch specific exceptions (not generic)
✓ Log context: state, input, expected vs actual
✓ Provide fallback - NEVER leave client hanging
✓ Return meaningful errors, NOT stack traces
```

---

## 🔍 Diagnostic Questions (Ask in Order)

**When something breaks:**

1. ❓ **Has this worked before?**
   - Regression or new issue?

2. ❓ **What exactly changed?**
   - `git diff` files?
   - Dependency changes?
   - Environment changes?

3. ❓ **What does error say?**
   - Full stack trace?
   - Line number accurate?
   - Root cause or symptom?

4. ❓ **Which layer failing?**
   - Frontend (console errors)
   - Backend (Flask/Python errors)
   - WebSocket (connection issues)
   - GPU (CUDA errors)

5. ❓ **What would fix this?**
   - Try safest: rollback → env check → restart → logs

---

## ✅ Before Every Commit

```bash
# 1. Reasoning explained?
grep -E "WHAT:|WHY:|HOW:" git diff

# 2. No Pattern violations?
grep 'style="' *.html              # Pattern 2?
head -20 *.py | grep import         # Pattern 1?
grep -E 'def \w+\(' *.py            # Pattern 3?

# 3. Error handling complete?
grep "except:" *.py | wc -l         # Catch errors?
grep "finally:" *.py | wc -l        # Cleanup?

# 4. Fallback mechanism?
grep "fallback\|except" *.py        # Graceful degradation?
```

---

## 🎓 Real Project Examples

| Issue | Pattern | Fix | Result |
|-------|---------|-----|--------|
| Template `${progre"` | Reasoning | Complete variable | ✅ Renders |
| showSection undefined | Root Cause | Move to `<head>` | ✅ Navigation works |
| Inline `style="0%"` | Pattern 2 | CSS class | ✅ Webhint passes |
| Type errors (11×) | Pattern 3 | Add type hints | ✅ IDE works |

---

## 🚀 During Development

```python
# ALWAYS follow this pattern:

# 1. Set env vars FIRST (Pattern 1)
os.environ['VAR'] = 'value'

# 2. Add type hints (Pattern 3)
def process(data: Dict) -> str:
    pass

# 3. Use CSS classes, not inline styles (Pattern 2)
<div class="progress">Loading...</div>

# 4. Resource management (Pattern Set B)
try:
    check_vram()  # Pre-check
    result = run()
finally:
    cleanup()  # Always cleanup

# 5. Error handling (Pattern Set D)
except MemoryError as e:
    logger.error(f"OOM: state={state}, input={input_file}")
    return fallback()  # Always fallback
```

---

## 🧠 When Stuck (Decision Tree)

1. **Stop and think** - Don't guess
2. **Ask questions** - Use diagnostic Q&A (above)
3. **Collect evidence** - What supports/contradicts my hypothesis?
4. **Apply patterns** - Does this match Pattern 1/2/3?
5. **Use decision tree** - Follow BOB AI flow
6. **Document** - Explain your reasoning (Principle 1)

---

## 📍 Key Files

| File | Purpose |
|------|---------|
| `.github/copilot-instructions.md` | Main instructions + patterns |
| `REASONING_AND_BOB_AI_GUIDE.md` | Detailed guide + examples |
| `REASONING_ENHANCEMENT_SUMMARY.md` | Usage guide + checklists |
| This file | Quick reference (you are here!) |

---

## 🎯 Remember

- ✅ **Root cause BEFORE symptoms** (Don't fix symptoms!)
- ✅ **Explain your reasoning** (WHAT, WHY, HOW)
- ✅ **Collect evidence** (FOR and AGAINST each decision)
- ✅ **Use patterns** (Don't reinvent solutions)
- ✅ **Systematic debugging** (Follow decision tree)
- ✅ **Always fallback** (Never leave client hanging)
- ✅ **Document everything** (Future you will thank you)

---

**Version:** 1.0
**Last Updated:** October 27, 2025
**Status:** ✅ Ready to use
**Commits:** 52ba6b7, 22c552b, 090faa7

Print this! Bookmark this! Use this! 🚀
