"""Quick tests for PawPal+ core behaviors."""

from pawpal_system import Pet, Task


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
