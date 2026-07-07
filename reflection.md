# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
It has all four classses and the correct ownership
- What classes did you include, and what responsibilities did you assign to each?
I included owner, pet, task, and schedule. I gave them responsiblities that correspond with the class

**b. Design changes**

- Did your design change during implementation?
It did not
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

  My conflict detector (`Scheduler.detect_conflicts`) checks whether two tasks'
  time *windows* overlap using each task's `preferred_time` plus its
  `duration_minutes`. However, the greedy `build_plan` itself does not honor
  `preferred_time` — it packs tasks back-to-back starting at the owner's
  `day_start`, ordered by priority then duration. So conflict detection reasons
  about *requested* times while the generated plan reasons about *available*
  time. I chose to keep these two views separate rather than making the planner
  solve the harder constrained-placement problem.

- Why is that tradeoff reasonable for this scenario?

  A busy pet owner benefits most from a simple, predictable plan that never
  crashes and clearly warns when two things they *wanted* at the same time can't
  both happen. A full constraint solver (respecting fixed times, durations, and
  priorities simultaneously) would be more "correct" but much harder to read,
  test, and explain — and overkill for a handful of daily tasks. The lightweight
  warning gives the owner the information to resolve clashes themselves.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
