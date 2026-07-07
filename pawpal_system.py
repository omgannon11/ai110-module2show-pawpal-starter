"""PawPal+ core system classes.

Logic layer generated from diagrams/uml.mmd:

- Task      : a single care activity (description, time, frequency, completion).
- Pet       : pet details plus a list of its tasks.
- Owner     : manages multiple pets and exposes all their tasks.
- Scheduler : the "brain" that retrieves, organizes, and plans tasks across pets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time, timedelta, datetime

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
