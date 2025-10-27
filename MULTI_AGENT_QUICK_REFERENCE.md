# Multi-Agent Argumentation Quick Reference Card

**Use this card when making major decisions or debugging complex issues.**

---

## The 5 Agents at a Glance

### 1️⃣ THE PESSIMIST 😟

**Asks:** "What could go wrong?"

- Worst-case scenarios
- Edge cases
- Failure modes
- Data format breaks
- Permission problems
- Network timeouts
- Memory exhaustion

**Output Style:** "This will definitely fail when..."
**When Right:** Catches production disasters
**When Wrong:** Paralyzed by worst case

### 2️⃣ THE OPTIMIST 😊

**Asks:** "Why this could work?"

- Best-case scenarios
- Common patterns
- Proven approaches
- Safe defaults
- Simplifications

**Output Style:** "This works for 99% of cases..."
**When Right:** Validates feasibility
**When Wrong:** Misses edge cases

### 3️⃣ THE ENGINEER 🔧

**Asks:** "How do we actually build it?"

- Simplest implementation
- Dependencies needed
- Performance characteristics
- Maintenance burden
- Testing strategy

**Output Style:** "Implementation needs: X, Y, Z components..."
**When Right:** Realistic implementation plan
**When Wrong:** Impractical or too complex

### 4️⃣ THE RESEARCHER 📚

**Asks:** "What does the industry know?"

- How others solve it
- Academic standards
- Open source patterns
- Research findings
- Common pitfalls

**Output Style:** "Best practice is X (source: Y)..."
**When Right:** Grounds in proven methods
**When Wrong:** Standards may not fit your context

### 5️⃣ THE DEVIL'S ADVOCATE 😈

**Asks:** "Is our premise wrong?"

- Are we solving the right problem?
- Are assumptions flawed?
- What aren't we considering?
- Better approach exists?
- Fundamental objections?

**Output Style:** "Why are we even assuming X?..."
**When Right:** Reveals blind spots
**When Wrong:** Unnecessarily disruptive

---

## Decision-Making Workflow

### Step 1: State Problem Clearly

```
❌ VAGUE: "GPU memory is broken"
✅ CLEAR: "Second 3D generation job fails with OOM despite having 8GB available"
```

### Step 2: Ask Each Agent

Go through all 5 agents **in order**. Don't skip any.

```
PESSIMIST: What could go wrong?
OPTIMIST: Why this could work?
ENGINEER: How do we build it?
RESEARCHER: What do experts say?
DEVIL: Is our premise wrong?
```

### Step 3: Look for Disagreement

Disagreement reveals blind spots.

```
IF Pessimist says: "Will definitely fail"
BUT Optimist says: "Works 99% of time"
THEN: Disagreement means we need to understand the 1% failure case better
```

### Step 4: Identify Consensus

What do all agents agree on?

```
All 5 agree: "Pre-check before allocation is good"
All 5 disagree: "Whether to use GPU or CPU"
Action: Implement what all agree on, debate what they disagree on
```

### Step 5: Choose Best Solution

The solution that addresses all 5 perspectives.

```
PESSIMIST: "Needs fallback"     → ✅ Add CPU fallback tier
OPTIMIST: "Keep it simple"      → ✅ Don't over-engineer
ENGINEER: "Needs cleanup logic" → ✅ Add finally block
RESEARCHER: "Industry standard" → ✅ Follow PyTorch pattern
DEVIL: "What about fragmentation?" → ✅ Add memory pooling research
```

---

## Real-World Example: Decision Point

**PROBLEM:** Should we cache expensive computations?

### Agent Dialogue

**PESSIMIST:**
"Cache will cause stale data bugs. Users get wrong results. Nightmare to debug. Cache invalidation is hard. What if cache grows unbounded? System runs out of RAM."

**OPTIMIST:**
"Caching is industry standard. 80% of ML services do it. We'll get 40x speedup. Cache misses only cost CPU, nothing lost. Worth the risk."

**ENGINEER:**
"Caching needs: Redis or in-memory store, invalidation logic, TTL management, monitoring. 1500 LOC. Moderate complexity. Testing: hit/miss rates, expiry behavior."

**RESEARCHER:**
"Best practice is time-based TTL plus event invalidation. Google: Spanner uses this. Facebook: Similar caching strategy. Academic: 'Cache Consistency' papers show TTL-based is sufficient for 99% of cases."

**DEVIL'S ADVOCATE:**
"Why cache at all? What if we just accept the latency? Or pre-compute everything offline? Caching adds complexity for speed - is speed actually the bottleneck? Have we profiled?"

### Consensus Building

```
ALL AGREE:
✓ Caching helpful IF done right
✓ Need TTL to prevent staleness
✓ Need monitoring to catch issues
✓ Need fallback/disable switch

DISAGREE ON:
✗ Whether to do caching (YES vs NO)
✗ What technology (Redis vs in-memory)
✗ TTL duration (1 hour vs 1 day)

RESOLUTION:
→ Implement with 1-hour TTL (conservative, Pessimist happy)
→ Use in-memory first (Engineer: simplest), upgrade to Redis if scale requires
→ Feature flag to disable instantly (Pessimist safety valve)
→ Monitor cache hit/miss rates (verify it's actually helping)
→ 20% gradual rollout (test theory before full deployment)
```

---

## Agent Priority Matrix

**For each decision, check if agent is relevant:**

| Decision Type | Pessimist | Optimist | Engineer | Researcher | Devil | Priority |
|---------------|-----------|----------|----------|-----------|-------|----------|
| **Critical production code** | 🔴 MUST | 🟡 SHOULD | 🔴 MUST | 🟡 SHOULD | 🟡 SHOULD | All 5 |
| **Major architecture** | 🔴 MUST | 🔴 MUST | 🔴 MUST | 🔴 MUST | 🔴 MUST | All 5 |
| **Bug fix** | 🟡 SHOULD | 🟡 SHOULD | 🔴 MUST | 🟢 MAYBE | 🟢 MAYBE | 2-3 |
| **Performance optimization** | 🟡 SHOULD | 🔴 MUST | 🔴 MUST | 🔴 MUST | 🟡 SHOULD | All 5 |
| **Simple feature** | 🟢 MAYBE | 🟡 SHOULD | 🟡 SHOULD | 🟢 MAYBE | 🟢 MAYBE | 2-3 |
| **Emergency fix** | 🟢 MAYBE | 🔴 MUST | 🔴 MUST | 🟢 MAYBE | 🟢 MAYBE | 2 |

🔴 MUST = Absolutely include
🟡 SHOULD = Usually include
🟢 MAYBE = Optional, time permitting

---

## Agent Conversation Starters

### For Pessimist

- "What's the disaster scenario?"
- "What data format could break this?"
- "What if [resource] runs out?"
- "What happens if this fails mid-execution?"
- "What's the 1% failure case?"

### For Optimist

- "Has this pattern worked before?"
- "What do other projects do?"
- "Can we simplify this?"
- "What are the safe defaults?"
- "What's the industry standard?"

### For Engineer

- "How hard is this to implement?"
- "What are the dependencies?"
- "What's the performance impact?"
- "How much code is this?"
- "How do we test this?"

### For Researcher

- "What does the academic literature say?"
- "What's the industry standard?"
- "What do open source projects do?"
- "What did others learn?"
- "What's the common pitfall?"

### For Devil's Advocate

- "Is this even the right problem?"
- "Are we making wrong assumptions?"
- "What if we approached it differently?"
- "What haven't we considered?"
- "Why are we assuming X?"

---

## Quick Scoring Template

**Rate each agent's concern (1-5):**

```
DECISION: [Your decision here]

PESSIMIST concern level:     1 2 3 4 5  (5 = high risk)
OPTIMIST confidence level:   1 2 3 4 5  (5 = definitely works)
ENGINEER complexity level:   1 2 3 4 5  (5 = very complex)
RESEARCHER consensus score:  1 2 3 4 5  (5 = strong industry standard)
DEVIL doubt level:           1 2 3 4 5  (5 = fundamental flaw)

TOTAL RISK SCORE:            ___/25

If score > 15: Risky - add more safeguards
If score 10-15: Moderate - proceed with caution
If score < 10: Low risk - proceed confidently
```

---

## When to Use Multi-Agent vs Single Agent

### Use Multi-Agent (All 5) When

- ✅ Making major architectural decisions
- ✅ Planning risky deployments
- ✅ Evaluating competing solutions
- ✅ You have 30+ min to decide
- ✅ Decision affects many people
- ✅ Costs are high (performance, money, risk)

### Use Single Agent When

- ✅ Pessimist only: Code review (what could break?)
- ✅ Engineer only: Technical feasibility check
- ✅ Researcher only: Learning what industry does
- ✅ You have 5-10 min only
- ✅ Decision is reversible
- ✅ Low stakes

### Don't Use Multi-Agent When

- ❌ Emergency firefighting (too slow)
- ❌ Obvious decision (waste of time)
- ❌ Already decided (avoid analysis paralysis)
- ❌ Simple tactical changes (overkill)

---

## Common Anti-Patterns to Avoid

| Anti-Pattern | What Goes Wrong | Better Way |
|--------------|-----------------|-----------|
| **Only Pessimist** | Paralyzed, never ship | Include Optimist too |
| **Only Optimist** | Surprised by failures | Include Pessimist too |
| **Skip Devil's Advocate** | Miss fundamental flaws | Always include Devil last |
| **No Researcher** | Reinvent the wheel | Check what others did |
| **No Engineer** | Plan fails in implementation | Validate with Engineer |
| **Talk but don't decide** | Analysis paralysis | Make decision even with disagreement |
| **Ignore disagreement** | Blind spots fester | Use disagreement as signal |
| **Add 6th agent** | Dilutes framework | Stick with 5 |

---

## One-Page Cheat Sheet

```
WHEN FACING A PROBLEM:

1. STATE IT CLEARLY
   Problem: [specific, measurable description]

2. ASK EACH AGENT (in order)
   Pessimist: What could go wrong?
   Optimist: Why this could work?
   Engineer: How do we build it?
   Researcher: What do experts know?
   Devil: Is premise wrong?

3. LOOK FOR SIGNALS
   Disagreement = blind spot to investigate
   Consensus = solid ground to build on

4. MAKE DECISION
   Choose solution addressing all concerns
   Add safeguards for Pessimist's risks
   Include Pessimist's fallback tier

5. IMPLEMENT WITH CONVICTION
   You've heard all perspectives
   Decision is stronger for it
   Proceed confidently
```

---

## Reference: Agent Personality Templates

### PESSIMIST Example Dialogue

"This will fail catastrophically when [X happens]. You haven't considered [Y]. The worst case is [Z]. We absolutely need [fallback strategy]. I recommend [defensive approach]."

### OPTIMIST Example Dialogue

"This works for 99% of cases. Industry standard is [approach]. Simple solution is [X]. Don't overthink it. This has proven [benefits] in production at [companies]."

### ENGINEER Example Dialogue

"Implementation needs: [components list]. Testing plan: [test cases]. Performance impact: [metrics]. Maintenance burden: [estimate]. Timeline: [duration]."

### RESEARCHER Example Dialogue

"Best practice from [source]: [recommendation]. Academic research shows: [finding]. Open source projects do: [pattern]. Common pitfall: [warning]."

### DEVIL Example Dialogue

"Why are we assuming [X]? Have we considered [alternative]? What if [different premise]? Fundamental issue: [objection]. Better approach: [different solution]."

---

**Last Updated:** October 27, 2025
**Part Of:** PESSIMISTIC_MULTI_AGENT_ENHANCEMENTS.md
