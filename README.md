# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Terminal output from running `python main.py`:

```
Today's Schedule for Jordan
========================================
Daily plan:
  08:00 — Breakfast (10 min) [priority: high]
  08:10 — Feed cat (10 min) [priority: high]
  08:20 — Give meds (10 min) [priority: high]
  08:30 — Evening walk (30 min) [priority: high]
  09:00 — Litter box (5 min) [priority: medium]

Skipped (not enough time):
  - Grooming (needs 45 min)

All tasks sorted by time
========================================
  07:30  Feed cat
  08:00  Breakfast
  09:00  Litter box
  12:00  Grooming
  12:00  Give meds
  18:00  Evening walk
  --:--  Vet checkup

Recurring task automation
========================================
  Completed: [✓] Breakfast (10 min) [priority: high]
  Auto-created next occurrence due 2026-07-08: [ ] Breakfast (10 min) [priority: high]

Conflict detection
========================================
  ⚠ Conflict: 'Grooming' (12:00, 45 min) overlaps 'Give meds' (12:00)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
.......                                                                  [100%]
7 passed in 0.01s
```

## 📐 Smarter Scheduling

Phase 3 adds lightweight algorithms that make PawPal+ feel intelligent. Each
feature and the method that implements it:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks by `preferred_time` (earliest first) via a `lambda` key; tasks with no time sort last. The planner also sorts internally by priority then duration in `Scheduler._sort_tasks()`. |
| Filtering | `Scheduler.filter_by_status()`, `Scheduler.filter_by_pet()` | Filter tasks by completion status (done/pending) or by pet name. |
| Conflict detection | `Scheduler.detect_conflicts()` | Compares every pair of timed tasks (start time + duration); returns human-readable warning strings for overlaps instead of crashing. Works for same-pet or cross-pet clashes. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()` | Completing a daily/weekly task auto-creates the next instance, advancing `due_date` with `timedelta` (+1 day / +1 week). |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
