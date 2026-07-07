# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

  My initial UML had all four classes with the correct ownership relationships: an Owner owns Pets, and each Pet has Tasks. The Scheduler sat on top as the "brain" that used the Owner's data to build a plan.

- What classes did you include, and what responsibilities did you assign to each?

  I included Owner, Pet, Task, and Scheduler. Owner holds the constraints (time budget, preferences) and the pets; Pet holds its own care tasks; Task represents one activity; and Scheduler retrieves, organizes, and plans those tasks across all pets.

**b. Design changes**

- Did your design change during implementation?

  The core structure stayed the same, but the Scheduler and Task classes grew during Phase 3. I added algorithmic methods (`sort_by_time`, `filter_by_status`, `filter_by_pet`, `detect_conflicts`, `mark_task_complete`) and a `due_date` field plus `next_occurrence()` on Task.

- If yes, describe at least one change and why you made it.

  I added a `due_date` field and `next_occurrence()` to Task so recurring tasks could advance their date with `timedelta`. This was necessary because "mark complete" needed to spawn the next daily/weekly instance, which the original design didn't account for. The final version is captured in `diagrams/uml_final.mmd`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

  The scheduler considers the owner's total available minutes, each task's priority (low/medium/high), and each task's duration. It also respects recurrence, so only tasks actually due on the chosen weekday are considered.

- How did you decide which constraints mattered most?

  Time budget and priority mattered most because a busy owner physically can't do everything, so the plan has to protect the highest-priority tasks first. I sort by priority descending, then by shorter duration, so important short tasks are the least likely to be skipped.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

  My conflict detector (`Scheduler.detect_conflicts`) checks whether two tasks' time *windows* overlap using each task's `preferred_time` plus its `duration_minutes`. However, the greedy `build_plan` itself does not honor `preferred_time` — it packs tasks back-to-back starting at the owner's `day_start`, ordered by priority then duration. So conflict detection reasons about *requested* times while the generated plan reasons about *available* time. I chose to keep these two views separate rather than making the planner solve the harder constrained-placement problem.

- Why is that tradeoff reasonable for this scenario?

  A busy pet owner benefits most from a simple, predictable plan that never crashes and clearly warns when two things they *wanted* at the same time can't both happen. A full constraint solver (respecting fixed times, durations, and priorities simultaneously) would be more "correct" but much harder to read, test, and explain — and overkill for a handful of daily tasks. The lightweight warning gives the owner the information to resolve clashes themselves.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

  I used my AI coding assistant to brainstorm the algorithmic features, draft the sorting/filtering/conflict methods, and generate the test suite. I kept separate chat sessions for the core implementation versus the algorithmic planning so each conversation stayed focused. I also used it to explain test code and Python idioms like `lambda` sort keys and `timedelta`.

- What kinds of prompts or questions were most helpful?

  Specific, scoped prompts were the most helpful — for example asking for a "lightweight conflict detection strategy that returns a warning instead of crashing" gave a much better result than a vague "add conflict detection." Attaching the actual file so the assistant matched my existing style and method names also cut down on rework.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

  The original conflict-detection code checked the greedy `scheduled` plan, which never actually overlaps because tasks are packed sequentially — so it could never fire. I rejected that approach and had it re-based on each task's `preferred_time` instead, which is what a pet owner actually cares about.

- How did you evaluate or verify what the AI suggested?

  I ran `python main.py` and `python -m pytest` after every change and read the actual output rather than trusting the code by eye. When the demo printed a false "Breakfast overlaps Breakfast" conflict, that told me completed/recurring copies needed to be excluded, so I fixed it and confirmed with the tests.

**c. AI Strategy**

- Which AI coding assistant features were most effective for building your scheduler?

  Multi-file editing was the most effective feature, since adding recurrence touched `Task`, `Scheduler`, `main.py`, and the tests at once. Inline chat scoped to a single method was also valuable for asking "how could this be simplified?" without losing the surrounding context.

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.

  It suggested sorting `preferred_time` as `"HH:MM"` strings with a lambda, but my codebase already models `preferred_time` as `datetime.time` objects. I kept my typed objects and sorted on them directly, which is cleaner and avoids fragile string parsing.

- How did using separate chat sessions for different phases help you stay organized?

  Keeping planning, implementation, and testing in separate sessions meant each conversation had a tight, relevant context instead of a giant mixed history. It made the assistant's suggestions more on-target and made it easier for me to track which decisions belonged to which phase.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

  I tested the five core behaviors: task completion, sorting by time, filtering by status/pet, daily and weekly recurrence, and conflict detection. I also tested edge cases like a pet with no tasks and two tasks at the exact same time.

- Why were these tests important?

  These are the behaviors that make PawPal+ "smart," so a regression in any of them would break the app's value. The edge cases matter because empty inputs and exact-time clashes are exactly where naive code tends to crash.

**b. Confidence**

- How confident are you that your scheduler works correctly?

  I'm fairly confident — about 4 out of 5 — because all 10 tests pass and cover the core algorithms and their main edge cases. I've verified the behavior both through the test suite and by reading the actual CLI output.

- What edge cases would you test next if you had more time?

  I'd test the greedy `build_plan` time-budget packing more thoroughly, and recurrence across month and year boundaries (e.g. completing a daily task on Dec 31). I'd also add tests for ties in priority and for weekly tasks landing on their exact due weekday.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

  I'm most satisfied with the conflict detection, because it turns a potential crash into a friendly, actionable warning that a real pet owner could use. It also cleanly reused the existing `preferred_time` and `duration_minutes` fields instead of requiring new data.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

  I'd make `build_plan` actually respect `preferred_time` so the generated schedule and the conflict warnings agree with each other. I'd also add editing and deleting of tasks in the Streamlit UI and let users mark tasks complete directly from the app.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

  I learned that being the "lead architect" means the AI accelerates the work but I own the correctness — the AI can write plausible code quickly, but only running it, reading the output, and testing edge cases proved whether it was actually right. My job was to set clear scope, reject suggestions that didn't fit my design, and verify everything, rather than to accept generated code on faith.
