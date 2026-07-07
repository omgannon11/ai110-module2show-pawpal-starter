# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

PawPal+ is more than a task list — it applies lightweight algorithms to help a busy owner:

- **Daily planning** — greedily fits due tasks into the owner's time budget by priority, then explains the plan (`Scheduler.build_plan()`, `Scheduler.explain()`).
- **Sorting by time** — displays tasks in chronological order by preferred time (`Scheduler.sort_by_time()`).
- **Filtering** — view tasks by completion status or by pet (`Scheduler.filter_by_status()`, `Scheduler.filter_by_pet()`).
- **Conflict warnings** — flags tasks whose requested times overlap, for the same or different pets, with a friendly warning instead of a crash (`Scheduler.detect_conflicts()`).
- **Daily & weekly recurrence** — completing a recurring task automatically creates its next occurrence (+1 day or +1 week) (`Scheduler.mark_task_complete()`, `Task.next_occurrence()`).

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

Run the full automated test suite from the project root:

```bash
python -m pytest
```

**What the tests cover** (`tests/test_pawpal.py`, 10 tests):

- **Core behavior** — marking a task complete flips its status; adding a task grows the pet's task list.
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological order, with untimed tasks last.
- **Filtering** — `filter_by_status()` and `filter_by_pet()` return only matching tasks.
- **Recurrence logic** — completing a daily task creates tomorrow's copy; a weekly task advances seven days.
- **Conflict detection** — overlapping and exact-same-time tasks are flagged; non-overlapping tasks are not; nothing ever crashes.
- **Edge case** — a pet with no tasks returns empty results from sorting, conflict detection, and `build_plan()`.

Terminal output from a successful run:

```
platform darwin -- Python 3.10.9, pytest-7.1.2, pluggy-1.0.0
rootdir: /Users/olliegannon/codePath/ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 10 items

tests/test_pawpal.py ..........                                          [100%]

============================== 10 passed in 0.01s ==============================
```

**Confidence Level: ★★★★☆ (4/5)**

The core scheduling algorithms — sorting, filtering, recurrence, and conflict detection — are all covered by passing tests, including the key edge cases (empty pets, exact-time clashes). I've left one star off because the greedy `build_plan()` time-budget packing and cross-day recurrence over month/year boundaries have lighter coverage and would be the next things to test.

## 📐 Smarter Scheduling

Phase 3 adds lightweight algorithms that make PawPal+ feel intelligent. Each
feature and the method that implements it:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks by `preferred_time` (earliest first) via a `lambda` key; tasks with no time sort last. The planner also sorts internally by priority then duration in `Scheduler._sort_tasks()`. |
| Filtering | `Scheduler.filter_by_status()`, `Scheduler.filter_by_pet()` | Filter tasks by completion status (done/pending) or by pet name. |
| Conflict detection | `Scheduler.detect_conflicts()` | Compares every pair of timed tasks (start time + duration); returns human-readable warning strings for overlaps instead of crashing. Works for same-pet or cross-pet clashes. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()` | Completing a daily/weekly task auto-creates the next instance, advancing `due_date` with `timedelta` (+1 day / +1 week). |

## 🚶 Demo Walkthrough

### Main UI features

Launch the app with `streamlit run app.py`. From the single-page interface a user can:

- Set the **owner's name and daily time budget** (minutes available today).
- **Add pets** (name, species, breed).
- **Add tasks** to any pet, including duration, priority, category, and a **preferred time**.
- See a **"Today at a Glance"** panel that filters tasks by status (Pending / Completed / All), sorts them chronologically, and shows any **conflict warnings**.
- **Generate a schedule** for a chosen weekday and read the "Why this plan?" explanation.

### Example workflow

1. Enter the owner name **Jordan** and set the time budget to **90 minutes**.
2. **Add a pet** — "Mochi", a dog.
3. **Add a task** — "Morning walk", 30 min, high priority, preferred time 08:00.
4. Add a second task at the same time to see PawPal+ raise a **conflict warning** in the "Today at a Glance" panel.
5. Click **Generate schedule** to see today's ordered plan and the reasoning behind it.

### Key Scheduler behaviors shown

- **Sorting** — the glance panel and CLI both list tasks earliest-time-first.
- **Filtering** — toggle Pending/Completed/All to filter by status.
- **Conflict warnings** — two tasks wanting the same slot produce a `st.warning` instead of a crash.
- **Recurrence** — completing a daily/weekly task spawns its next occurrence automatically.
- **Explainable planning** — the greedy planner fits tasks into the time budget by priority and explains what it skipped and why.

### Sample CLI output

Running `python main.py`:

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

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
