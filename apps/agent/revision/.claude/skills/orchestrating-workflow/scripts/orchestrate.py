#!/usr/bin/env python3
"""
Orchestration script for travel planning workflow.

Updates workflow state and returns the next step to execute.

Usage:
    python3 orchestrate.py --completed-step transportation --message "Found 5 flight options"
    python3 orchestrate.py --init
    python3 orchestrate.py --status
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Paths
project_root = Path.cwd()
process_dir = project_root / "files" / "process"
workflow_state_file = process_dir / "workflow_state.json"
trip_context_file = process_dir / "trip_context.json"

# Fixed sequence of subagents
SEQUENCE = ["transportation", "accommodation", "activities", "verification", "booking"]


def load_workflow_state():
    """Load current workflow state."""
    if not workflow_state_file.exists():
        return None

    try:
        with open(workflow_state_file, 'r') as f:
            return json.load(f)
    except:
        return None


def save_workflow_state(state):
    """Save workflow state."""
    process_dir.mkdir(parents=True, exist_ok=True)
    with open(workflow_state_file, 'w') as f:
        json.dump(state, f, indent=2)


def load_trip_context():
    """Load trip context."""
    if not trip_context_file.exists():
        return None

    try:
        with open(trip_context_file, 'r') as f:
            return json.load(f)
    except:
        return None


def get_next_step(current_step, skip_booking=False):
    """Get the next step in the sequence."""
    if current_step not in SEQUENCE:
        return SEQUENCE[0]  # Start from beginning

    idx = SEQUENCE.index(current_step)

    # Check if we should skip booking
    if current_step == "verification" and skip_booking:
        return None  # Workflow complete

    # Move to next step
    if idx + 1 >= len(SEQUENCE):
        return None  # Workflow complete

    return SEQUENCE[idx + 1]


def get_step_prompt(step, trip_context):
    """Get the prompt for invoking a subagent."""
    destination = trip_context.get("destination", "the destination") if trip_context else "the destination"

    prompts = {
        "transportation": f"""Research transportation options for the trip to {destination}.

1. Read files/process/trip_context.json for complete trip details
2. Use the duffel skill to search for flights between origin and destination
3. Use the google-maps skill for ground transportation (airport to hotel directions)
4. Save flight results to files/content/flights/
5. Save route results to files/content/routes/

When complete, use Skill tool to invoke 'orchestrating-workflow' with message:
'Transportation research complete. [summary of findings]'""",

        "accommodation": f"""Research accommodation options for the trip to {destination}.

1. Read files/process/trip_context.json for trip details (dates, guests, budget)
2. Use the duffel skill to search for hotels in the destination
3. Save hotel results to files/content/hotels/

When complete, use Skill tool to invoke 'orchestrating-workflow' with message:
'Accommodation research complete. [summary of findings]'""",

        "activities": f"""Research activities and attractions for the trip to {destination}.

1. Read files/process/trip_context.json for trip details and traveler interests
2. Use the google-maps skill to search for places matching interests
3. Use google-maps to calculate distances between attractions
4. Save results to files/content/activities/

When complete, use Skill tool to invoke 'orchestrating-workflow' with message:
'Activities research complete. [summary of findings]'""",

        "verification": f"""Validate all travel research for the trip to {destination}.

1. Read all research results from files/content/
2. Verify prices are within budget
3. Check schedule compatibility (flight times vs hotel check-in, etc.)
4. Confirm logical consistency of the trip plan
5. Write verification report

When complete, use Skill tool to invoke 'orchestrating-workflow' with message:
'Verification complete. [summary of validation results]'""",

        "booking": f"""Create the final trip itinerary for {destination}.

1. Read all verified research from files/content/
2. Compile a complete day-by-day itinerary
3. Include all booking links and instructions
4. Calculate total estimated cost
5. Write final itinerary to files/output/itinerary.md

When complete, use Skill tool to invoke 'orchestrating-workflow' with message:
'Booking complete. Itinerary created at files/output/itinerary.md'"""
    }

    return prompts.get(step, f"Execute {step} step for the trip.")


def handle_init():
    """Initialize or check workflow state."""
    state = load_workflow_state()
    trip_context = load_trip_context()

    if not trip_context:
        return {
            "status": "error",
            "message": "No trip context found. Run workflow_init.py hook first."
        }

    if state and state.get("status") == "in_progress":
        # Resume existing workflow
        current_step = state.get("current_step", 0)
        if current_step < len(SEQUENCE):
            next_step = SEQUENCE[current_step]
            return {
                "status": "resume",
                "next_step": next_step,
                "prompt": get_step_prompt(next_step, trip_context),
                "message": f"Resuming workflow at step: {next_step}"
            }

    # Start fresh
    state = {
        "current_step": 0,
        "steps": SEQUENCE.copy(),
        "completed_steps": [],
        "skip_booking": False,
        "status": "in_progress",
        "started_at": datetime.now().isoformat()
    }
    save_workflow_state(state)

    first_step = SEQUENCE[0]
    return {
        "status": "start",
        "next_step": first_step,
        "prompt": get_step_prompt(first_step, trip_context),
        "message": f"Starting workflow. First step: {first_step}"
    }


def handle_completed_step(completed_step, message):
    """Handle completion of a step and return next action."""
    state = load_workflow_state()
    trip_context = load_trip_context()

    if not state:
        return {
            "status": "error",
            "message": "No workflow state found. Initialize workflow first."
        }

    # Validate the completed step
    if completed_step not in SEQUENCE:
        return {
            "status": "error",
            "message": f"Unknown step: {completed_step}. Valid steps: {SEQUENCE}"
        }

    # Update completed steps
    if completed_step not in state.get("completed_steps", []):
        state.setdefault("completed_steps", []).append(completed_step)

    # Record completion
    state.setdefault("history", []).append({
        "step": completed_step,
        "message": message,
        "completed_at": datetime.now().isoformat()
    })

    # Get next step
    skip_booking = state.get("skip_booking", False)
    next_step = get_next_step(completed_step, skip_booking)

    if next_step is None:
        # Workflow complete
        state["status"] = "completed"
        state["completed_at"] = datetime.now().isoformat()
        state["current_step"] = len(SEQUENCE)
        save_workflow_state(state)

        return {
            "status": "complete",
            "message": "Workflow complete! All steps finished.",
            "completed_steps": state["completed_steps"],
            "output": "files/output/itinerary.md"
        }

    # Update current step
    state["current_step"] = SEQUENCE.index(next_step)
    save_workflow_state(state)

    return {
        "status": "continue",
        "next_step": next_step,
        "prompt": get_step_prompt(next_step, trip_context),
        "message": f"Step '{completed_step}' complete. Next: {next_step}",
        "completed_steps": state["completed_steps"]
    }


def handle_status():
    """Return current workflow status."""
    state = load_workflow_state()

    if not state:
        return {
            "status": "not_started",
            "message": "No workflow in progress"
        }

    return {
        "status": state.get("status", "unknown"),
        "current_step": state.get("current_step", 0),
        "steps": state.get("steps", SEQUENCE),
        "completed_steps": state.get("completed_steps", []),
        "skip_booking": state.get("skip_booking", False)
    }


def main():
    parser = argparse.ArgumentParser(description="Orchestrate travel planning workflow")
    parser.add_argument("--init", action="store_true", help="Initialize workflow")
    parser.add_argument("--completed-step", help="Mark a step as completed")
    parser.add_argument("--message", default="", help="Completion message")
    parser.add_argument("--status", action="store_true", help="Get workflow status")
    parser.add_argument("--skip-booking", action="store_true", help="Skip booking step")

    args = parser.parse_args()

    if args.skip_booking:
        state = load_workflow_state()
        if state:
            state["skip_booking"] = True
            save_workflow_state(state)
            print(json.dumps({"status": "updated", "skip_booking": True}, indent=2))
            return

    if args.init:
        result = handle_init()
    elif args.completed_step:
        result = handle_completed_step(args.completed_step, args.message)
    elif args.status:
        result = handle_status()
    else:
        # Default to init/status check
        result = handle_init()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
