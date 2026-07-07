"""Demo script for PawPal+ — a temporary testing ground.

Run with:  python main.py

Builds an owner with two pets and several tasks, then prints the
schedule the Scheduler produces for today.
"""

from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # --- Owner with a daily time budget and a preference ---
    owner = Owner(
        name="Jordan",
        available_minutes=90,
        day_start=time(8, 0),
        preferences={"prefers_morning_walks": True},
    )

    # --- Pet 1: a dog ---
    mochi = Pet(name="Mochi", species="dog", breed="Corgi")
    mochi.add_task(Task("Morning walk", 30, "high", "walk", preferred_time=time(8, 0)))
    mochi.add_task(Task("Breakfast", 10, "high", "feeding"))
    mochi.add_task(Task("Grooming", 45, "low", "grooming"))

    # --- Pet 2: a cat ---
    biscuit = Pet(name="Biscuit", species="cat", breed="Tabby")
    biscuit.add_task(Task("Feed cat", 10, "high", "feeding"))
    biscuit.add_task(Task("Litter box", 5, "medium", "grooming"))
    biscuit.add_task(
        Task("Vet checkup", 30, "medium", "meds", recurrence="weekly", weekday="tuesday")
    )

    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    # --- Build and print today's schedule ---
    scheduler = Scheduler(owner)
    scheduler.build_plan(weekday="monday")

    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    print(scheduler.explain())


if __name__ == "__main__":
    main()
