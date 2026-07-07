"""PawPal+ core system classes.

Skeleton generated from diagrams/uml.mmd. Method bodies are stubs
(no scheduling logic yet) — to be implemented incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time


@dataclass
class Task:
    """A single pet care activity — the core scheduling unit."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = "other"  # walk | feeding | meds | grooming | enrichment
    recurrence: str = "daily"  # "daily" | "weekly"
    preferred_time: time | None = None

    def priority_weight(self) -> int:
        """Map priority to a sortable integer (higher = more important)."""
        raise NotImplementedError

    def is_due(self, weekday: str) -> bool:
        """Return True if this task should run on the given weekday."""
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError


@dataclass
class Pet:
    """The animal being cared for; owns the care tasks."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, title: str) -> None:
        raise NotImplementedError

    def tasks_due_today(self, weekday: str) -> list[Task]:
        """Filter tasks by recurrence for the given weekday."""
        raise NotImplementedError

    def total_required_time(self) -> int:
        """Sum of all task durations in minutes."""
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner and their scheduling constraints/preferences."""

    name: str
    available_minutes: int
    day_start: time = time(8, 0)
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def remaining_time(self, scheduled: list[Task]) -> int:
        """Budget minus already-scheduled durations."""
        raise NotImplementedError

    def prefers(self, key: str) -> bool:
        """Safe lookup into preferences."""
        raise NotImplementedError


@dataclass
class Scheduler:
    """Produces a daily plan from a pet's tasks + owner constraints."""

    owner: Owner
    pet: Pet
    scheduled: list[tuple[time, Task]] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)

    def build_plan(self) -> list[tuple[time, Task]]:
        """Sort by priority, fit into the time budget, assign clock times."""
        raise NotImplementedError

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort by priority (desc), then duration."""
        raise NotImplementedError

    def _fits(self, task: Task, used: int) -> bool:
        """Time-budget / conflict check."""
        raise NotImplementedError

    def explain(self) -> str:
        """Human-readable reasoning for the generated plan."""
        raise NotImplementedError
