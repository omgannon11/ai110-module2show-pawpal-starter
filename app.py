from datetime import time as dtime

import streamlit as st

# --- Step 1: Establish the connection to the logic layer ---
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.markdown("A pet care planning assistant. Add your pets, give them tasks, and let PawPal+ build a daily plan.")

# --- Step 2: Manage application "memory" with st.session_state ---
# Streamlit re-runs this script top-to-bottom on every interaction. Storing the
# Owner in session_state keeps our data (pets, tasks) alive across those re-runs
# instead of being "reborn" empty each time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=90)

owner: Owner = st.session_state.owner

st.divider()

# --- Owner settings ---
st.subheader("Owner")
col_a, col_b = st.columns(2)
with col_a:
    owner.name = st.text_input("Owner name", value=owner.name)
with col_b:
    owner.available_minutes = st.number_input(
        "Time available today (minutes)", min_value=1, max_value=1440, value=owner.available_minutes
    )

st.divider()

# --- Step 3: Wiring UI actions to logic — Add a Pet ---
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    p1, p2, p3 = st.columns(3)
    with p1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with p2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with p3:
        breed = st.text_input("Breed", value="")
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), species=species, breed=breed.strip()))
            st.success(f"Added {pet_name}!")
        else:
            st.warning("Please enter a pet name.")

if not owner.pets:
    st.info("No pets yet. Add one above to get started.")
    st.stop()

# --- Wiring UI actions to logic — Add a Task to a chosen pet ---
st.subheader("Add a Task")
pet_names = [p.name for p in owner.pets]
with st.form("add_task_form", clear_on_submit=True):
    which_pet = st.selectbox("For which pet?", pet_names)
    t1, t2, t3 = st.columns(3)
    with t1:
        task_title = st.text_input("Task title", value="Morning walk")
    with t2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with t3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    c1, c2 = st.columns(2)
    with c1:
        category = st.selectbox(
            "Category", ["walk", "feeding", "meds", "grooming", "enrichment", "other"]
        )
    with c2:
        pref = st.time_input("Preferred time", value=dtime(8, 0))
    if st.form_submit_button("Add task"):
        target = next(p for p in owner.pets if p.name == which_pet)
        target.add_task(
            Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                category=category,
                preferred_time=pref,
            )
        )
        st.success(f"Added '{task_title}' for {which_pet}!")

# --- Show current pets and their tasks ---
st.subheader("Your Pets & Tasks")
for pet in owner.pets:
    with st.expander(f"{pet.name} ({pet.species}) — {len(pet.tasks)} task(s)", expanded=True):
        if pet.tasks:
            st.table(
                [
                    {
                        "Task": t.title,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority,
                        "Category": t.category,
                    }
                    for t in pet.tasks
                ]
            )
        else:
            st.caption("No tasks yet.")

st.divider()

# --- Phase 3 smart layer surfaced in the UI: sorting, filtering, conflicts ---
st.subheader("Today at a Glance")
glance = Scheduler(owner)

# Conflict detection — presented as an actionable warning, not a crash.
conflicts = glance.detect_conflicts()
if conflicts:
    st.warning(
        f"⚠ {len(conflicts)} scheduling conflict(s) found — "
        "two tasks want the same time slot:"
    )
    for message in conflicts:
        st.write(f"- {message}")
else:
    st.success("No scheduling conflicts — every task has its own time slot. ✅")

# Filtering by completion status, then sorting by time for a clean chronological view.
show = st.radio(
    "Show tasks",
    ["Pending", "Completed", "All"],
    horizontal=True,
)
tasks = owner.all_tasks()
if show == "Pending":
    tasks = glance.filter_by_status(tasks, completed=False)
elif show == "Completed":
    tasks = glance.filter_by_status(tasks, completed=True)

ordered = glance.sort_by_time(tasks)
if ordered:
    st.table(
        [
            {
                "Time": t.preferred_time.strftime("%H:%M") if t.preferred_time else "—",
                "Task": t.title,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Status": "✓ done" if t.completed else "pending",
            }
            for t in ordered
        ]
    )
else:
    st.caption("No tasks to show for this filter.")

st.divider()

# --- Wiring UI actions to logic — Generate the schedule ---
st.subheader("Build Schedule")
weekday = st.selectbox(
    "Day to plan for",
    ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    scheduler.build_plan(weekday=weekday)

    if scheduler.scheduled:
        st.markdown("### Today's Schedule")
        for slot, task in scheduler.scheduled:
            st.write(f"**{slot.strftime('%H:%M')}** — {task.title} ({task.duration_minutes} min) · _{task.priority}_")
    else:
        st.info("Nothing could be scheduled. Try adding tasks or increasing available time.")

    if scheduler.skipped:
        st.warning("Skipped (not enough time):")
        for task in scheduler.skipped:
            st.write(f"- {task.title} (needs {task.duration_minutes} min)")

    with st.expander("Why this plan?"):
        st.code(scheduler.explain(), language="text")
