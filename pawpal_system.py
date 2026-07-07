"""PawPal+ core system classes.

Logic layer generated from diagrams/uml.mmd:

- Task      : a single care activity (description, time, frequency, completion).
- Pet       : pet details plus a list of its tasks.
- Owner     : manages multiple pets and exposes all their tasks.
- Scheduler : the "brain" that retrieves, organizes, and plans tasks across pets.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta, datetime

# Priority labels mapped to sortable weights (higher = more important).
PRIORITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3}

# Recurrence values a task may take.
DAILY = "daily"
WEEKLY = "weekly"


@dataclass
class Task:
    """A single pet care activity — the core scheduling unit."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = "other"  # walk | feeding | meds | grooming | enrichment
    recurrence: str = DAILY  # "daily" | "weekly"
    preferred_time: time | None = None
    weekday: str | None = None  # for weekly tasks, the day it is due (e.g. "monday")
    due_date: date | None = None  # the date this instance is due (for recurrence)
    completed: bool = False

    def priority_weight(self) -> int:
        """Map priority to a sortable integer (higher = more important)."""
        return PRIORITY_WEIGHTS.get(self.priority.lower(), PRIORITY_WEIGHTS["medium"])

    def is_due(self, weekday: str) -> bool:
        """Return True if this task should run on the given weekday.

        Daily tasks are always due. Weekly tasks are due only on their
        assigned weekday (case-insensitive); a weekly task with no weekday
        set is treated as due every day.
        """
        if self.recurrence == DAILY:
            return True
        if self.recurrence == WEEKLY:
            if self.weekday is None:
                return True
            return self.weekday.lower() == weekday.lower()
        return True

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self, today: date | None = None) -> "Task":
        """Return a fresh, uncompleted copy of this task for its next due date.

        Daily tasks advance by one day (today + 1 day); weekly tasks advance by
        seven days. The interval is computed with datetime.timedelta so month
        and year boundaries are handled correctly.
        """
        base = self.due_date or today or datetime.min.date()
        step = timedelta(weeks=1) if self.recurrence == WEEKLY else timedelta(days=1)
        return replace(self, completed=False, due_date=base + step)

    def __repr__(self) -> str:
        """Return a compact, human-readable one-line summary of the task."""
        mark = "✓" if self.completed else " "
        return (
            f"[{mark}] {self.title} ({self.duration_minutes} min) "
            f"[priority: {self.priority}]"
        )


@dataclass
class Pet:
    """The animal being cared for; owns the care tasks."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove all tasks matching the given title (case-insensitive)."""
        self.tasks = [t for t in self.tasks if t.title.lower() != title.lower()]

    def tasks_due_today(self, weekday: str) -> list[Task]:
        """Filter tasks by recurrence for the given weekday."""
        return [t for t in self.tasks if t.is_due(weekday)]

    def total_required_time(self) -> int:
        """Sum of all task durations in minutes."""
        return sum(t.duration_minutes for t in self.tasks)


@dataclass
class Owner:
    """The pet owner: manages multiple pets and their scheduling constraints."""

    name: str
    available_minutes: int
    day_start: time = time(8, 0)
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Flatten and return every task across all of the owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def all_tasks_due_today(self, weekday: str) -> list[Task]:
        """Every task due on the given weekday, across all pets."""
        return [task for pet in self.pets for task in pet.tasks_due_today(weekday)]

    def remaining_time(self, scheduled: list[Task]) -> int:
        """Budget minus the durations of already-scheduled tasks."""
        used = sum(t.duration_minutes for t in scheduled)
        return self.available_minutes - used

    def prefers(self, key: str) -> bool:
        """Safe truthy lookup into preferences."""
        return bool(self.preferences.get(key, False))


@dataclass
class Scheduler:
    """The brain: retrieves, organizes, and plans tasks across an owner's pets."""

    owner: Owner
    scheduled: list[tuple[time, Task]] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)

    def build_plan(self, weekday: str = "monday") -> list[tuple[time, Task]]:
        """Build a daily plan for the given weekday.

        Pulls all due tasks across the owner's pets, sorts them by priority
        (then duration), and greedily fits them into the owner's time budget,
        assigning a clock time to each. Tasks that don't fit go to `skipped`.
        """
        self.scheduled = []
        self.skipped = []

        due = self.owner.all_tasks_due_today(weekday)
        ordered = self._sort_tasks(due)

        used = 0
        current = datetime.combine(datetime.min, self.owner.day_start)
        for task in ordered:
            if self._fits(task, used):
                self.scheduled.append((current.time(), task))
                used += task.duration_minutes
                current += timedelta(minutes=task.duration_minutes)
            else:
                self.skipped.append(task)

        return self.scheduled

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by their preferred_time (earliest first).

        Tasks with no preferred_time are treated as latest so they sort to the
        end rather than crashing the comparison.
        """
        return sorted(
            tasks,
            key=lambda t: t.preferred_time or time(23, 59),
        )

    def filter_by_status(self, tasks: list[Task], completed: bool) -> list[Task]:
        """Return only the tasks whose completion status matches `completed`."""
        return [t for t in tasks if t.completed == completed]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks belonging to the pet with the given name."""
        return [
            task
            for pet in self.owner.pets
            if pet.name.lower() == pet_name.lower()
            for task in pet.tasks
        ]

    def mark_task_complete(self, task: Task, pet: Pet) -> Task | None:
        """Complete a task and auto-create its next occurrence if it recurs.

        Marks `task` complete. If the task is daily or weekly, a fresh instance
        is created for the next due date and appended to `pet`'s task list, then
        returned. Returns None for one-off tasks.
        """
        task.mark_complete()
        if task.recurrence in (DAILY, WEEKLY):
            upcoming = task.next_occurrence()
            pet.add_task(upcoming)
            return upcoming
        return None

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Return warning messages for tasks whose requested times overlap.

        A "lightweight" check: it compares every pair of tasks that have a
        preferred_time, using start time + duration to decide if their windows
        overlap. Two tasks for the same pet or different pets both count. It
        never raises — it simply returns a list of human-readable warnings
        (empty if the day is conflict-free) so callers can print them.
        """
        if tasks is None:
            tasks = self.owner.all_tasks()

        timed = [t for t in tasks if t.preferred_time is not None and not t.completed]
        timed.sort(key=lambda t: t.preferred_time)

        warnings: list[str] = []
        for i in range(len(timed)):
            task_a = timed[i]
            end_a = (
                datetime.combine(datetime.min, task_a.preferred_time)
                + timedelta(minutes=task_a.duration_minutes)
            ).time()
            for j in range(i + 1, len(timed)):
                task_b = timed[j]
                if task_b.preferred_time < end_a:
                    warnings.append(
                        f"⚠ Conflict: '{task_a.title}' "
                        f"({task_a.preferred_time.strftime('%H:%M')}, "
                        f"{task_a.duration_minutes} min) overlaps "
                        f"'{task_b.title}' "
                        f"({task_b.preferred_time.strftime('%H:%M')})"
                    )
        return warnings

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort by priority (desc), then shorter duration first."""
        return sorted(
            tasks,
            key=lambda t: (-t.priority_weight(), t.duration_minutes),
        )

    def _fits(self, task: Task, used: int) -> bool:
        """True if the task fits within the owner's remaining time budget."""
        return used + task.duration_minutes <= self.owner.available_minutes

    def explain(self) -> str:
        """Human-readable reasoning for the generated plan."""
        lines: list[str] = []
        if self.scheduled:
            lines.append("Daily plan:")
            for slot, task in self.scheduled:
                lines.append(
                    f"  {slot.strftime('%H:%M')} — {task.title} "
                    f"({task.duration_minutes} min) [priority: {task.priority}]"
                )
        else:
            lines.append("No tasks scheduled.")

        if self.skipped:
            lines.append("")
            lines.append("Skipped (not enough time):")
            for task in self.skipped:
                lines.append(f"  - {task.title} (needs {task.duration_minutes} min)")

        return "\n".join(lines)
