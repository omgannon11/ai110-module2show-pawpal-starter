"""Demo script for PawPal+ — a temporary testing ground.

Run with:  python main.py

Builds an owner with two pets and several tasks, then prints the
schedule the Scheduler produces for today.
"""

from datetime import date, time

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # --- Owner with a daily time budget and a preference ---
    owner = Owner(
        name="Jordan",
        available_minutes=90,
        day_start=time(8, 0),
        preferences={"prefers_morning_walks": True},
    )

    # --- Pet 1: a dog (tasks added deliberately OUT OF ORDER by time) ---
    mochi = Pet(name="Mochi", species="dog", breed="Corgi")
    mochi.add_task(Task("Evening walk", 30, "high", "walk", preferred_time=time(18, 0)))
    mochi.add_task(Task("Breakfast", 10, "high", "feeding", preferred_time=time(8, 0)))
    mochi.add_task(Task("Grooming", 45, "low", "grooming", preferred_time=time(12, 0)))

    # --- Pet 2: a cat (also out of order) ---
    biscuit = Pet(name="Biscuit", species="cat", breed="Tabby")
    biscuit.add_task(Task("Feed cat", 10, "high", "feeding", preferred_time=time(7, 30)))
    biscuit.add_task(Task("Litter box", 5, "medium", "grooming", preferred_time=time(9, 0)))
    # Deliberate clash: Biscuit's meds start at 12:00 while Mochi is grooming
    # (12:00, 45 min) — the Scheduler should warn about the overlap.
    biscuit.add_task(Task("Give meds", 10, "high", "meds", preferred_time=time(12, 0)))
    biscuit.add_task(
        Task("Vet checkup", 30, "medium", "meds", recurrence="weekly", weekday="tuesday")
    )

    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    scheduler = Scheduler(owner)

    # --- Build and print today's greedy schedule ---
    scheduler.build_plan(weekday="monday")
    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    print(scheduler.explain())

    # --- Sorting: order every task by preferred time ---
    print("\nAll tasks sorted by time")
    print("=" * 40)
    for task in scheduler.sort_by_time(owner.all_tasks()):
        stamp = task.preferred_time.strftime("%H:%M") if task.preferred_time else "--:--"
        print(f"  {stamp}  {task.title}")

    # --- Filtering: by pet, and by completion status ---
    print("\nMochi's tasks (filter by pet)")
    print("=" * 40)
    for task in scheduler.filter_by_pet("Mochi"):
        print(f"  {task}")

    # --- Recurring tasks: completing a daily task spawns tomorrow's copy ---
    print("\nRecurring task automation")
    print("=" * 40)
    breakfast = mochi.tasks[1]  # daily task
    breakfast.due_date = date(2026, 7, 7)
    upcoming = scheduler.mark_task_complete(breakfast, mochi)
    print(f"  Completed: {breakfast}")
    print(f"  Auto-created next occurrence due {upcoming.due_date}: {upcoming}")

    print("\n  Pending tasks (filter by status)")
    for task in scheduler.filter_by_status(owner.all_tasks(), completed=False):
        print(f"    {task}")

    # --- Conflict detection: warn on overlapping time slots ---
    print("\nConflict detection")
    print("=" * 40)
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts in the current plan.")


if __name__ == "__main__":
    main()
