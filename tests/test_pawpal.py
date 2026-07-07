"""Quick tests for PawPal+ core behaviors."""

from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion_changes_status():
    """Calling mark_complete() flips the task's status to completed."""
    task = Task("Morning walk", 30, "high", "walk")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet(name="Mochi", species="dog", breed="Corgi")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", 10, "high", "feeding"))

    assert len(pet.tasks) == 1


def _scheduler_with_pet(pet):
    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(pet)
    return Scheduler(owner)


def test_sort_by_time_orders_earliest_first():
    """sort_by_time puts earlier preferred_times first; None sorts last."""
    pet = Pet(name="Mochi", species="dog")
    late = Task("Evening walk", 30, preferred_time=time(18, 0))
    early = Task("Breakfast", 10, preferred_time=time(8, 0))
    no_time = Task("Anytime play", 15)
    pet.tasks = [late, no_time, early]

    ordered = _scheduler_with_pet(pet).sort_by_time(pet.tasks)

    assert ordered == [early, late, no_time]


def test_filter_by_status_and_pet():
    """Filtering returns only matching completion status / pet name."""
    pet = Pet(name="Mochi", species="dog")
    done = Task("Breakfast", 10)
    done.mark_complete()
    pending = Task("Walk", 30)
    pet.tasks = [done, pending]
    scheduler = _scheduler_with_pet(pet)

    assert scheduler.filter_by_status(pet.tasks, completed=False) == [pending]
    assert scheduler.filter_by_status(pet.tasks, completed=True) == [done]
    assert scheduler.filter_by_pet("mochi") == [done, pending]


def test_completing_daily_task_creates_next_occurrence():
    """Marking a daily task complete spawns tomorrow's copy on the pet."""
    pet = Pet(name="Mochi", species="dog")
    task = Task("Breakfast", 10, recurrence="daily", due_date=date(2026, 7, 7))
    pet.add_task(task)
    scheduler = _scheduler_with_pet(pet)

    upcoming = scheduler.mark_task_complete(task, pet)

    assert task.completed is True
    assert upcoming is not None
    assert upcoming.completed is False
    assert upcoming.due_date == date(2026, 7, 8)
    assert len(pet.tasks) == 2


def test_detect_conflicts_flags_overlapping_times():
    """Two tasks whose requested time windows overlap produce a warning."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task("Walk", 60, preferred_time=time(8, 0)))
    pet.add_task(Task("Feed", 10, preferred_time=time(8, 30)))
    scheduler = _scheduler_with_pet(pet)

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert isinstance(conflicts[0], str)


def test_detect_conflicts_returns_empty_when_no_overlap():
    """Non-overlapping tasks return no warnings (and never crash)."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task("Walk", 30, preferred_time=time(8, 0)))
    pet.add_task(Task("Feed", 10, preferred_time=time(9, 0)))
    scheduler = _scheduler_with_pet(pet)

    assert scheduler.detect_conflicts() == []
