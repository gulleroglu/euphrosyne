#!/usr/bin/env python3
"""
Orchestration script for planning workflow.

Updates workflow state, performs progressive Supabase updates, and returns next step.

Usage:
    python3 orchestrate.py --init
    python3 orchestrate.py --completed-step transportation --message "Found 5 flight options"
    python3 orchestrate.py --status
"""
import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv

# Paths (scripts -> orchestrating-workflow -> skills -> .claude -> planning)
project_root = Path(__file__).parent.parent.parent.parent.parent
process_dir = project_root / "files" / "process"

# Load .env from planning agent root
load_dotenv(project_root / ".env")
content_dir = project_root / "files" / "content"
workflow_state_file = process_dir / "workflow_state.json"
plan_context_file = process_dir / "plan_context.json"
user_context_file = process_dir / "user_context.json"
occasion_context_file = process_dir / "occasion_context.json"

# Fixed sequence of subagents (NO booking in planning agent)
SEQUENCE = ["transportation", "accommodation", "activities", "verification"]

# Map steps to user_plans fields
STEP_TO_FIELD = {
    "transportation": "transportation",
    "accommodation": "accommodation",
    "activities": "activities",
    "verification": "plan"  # verification creates the plan
}

# Supabase setup
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def get_supabase_client():
    """Create Supabase client."""
    try:
        from supabase import create_client
        if not SUPABASE_URL or not SUPABASE_KEY:
            return None  # Will skip Supabase updates
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except ImportError:
        return None


def load_json_file(file_path: Path) -> dict:
    """Load JSON from file."""
    if not file_path.exists():
        return None
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        return None


def save_json_file(file_path: Path, data: dict):
    """Save JSON to file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def load_step_results(step: str) -> dict:
    """Load results from files/content/<step>/"""
    step_dir = content_dir / step

    if not step_dir.exists():
        return None

    results = {}

    # Look for results.json or similar
    for json_file in step_dir.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                results[json_file.stem] = data
        except:
            continue

    if not results:
        return None

    # If there's a single results.json, return its content directly
    if "results" in results:
        return results["results"]

    # If there's a single file, return its content
    if len(results) == 1:
        return list(results.values())[0]

    return results


def update_supabase(client, user_plan_id: str, step: str, results: dict, message: str):
    """Update user_plans in Supabase after step completion."""
    if not client or not user_plan_id:
        return False

    field = STEP_TO_FIELD.get(step)
    if not field:
        return False

    now = datetime.now().isoformat()

    try:
        # Build update data
        update_data = {
            field: results,
            "updated_at": now
        }

        # For verification step, also update change_log
        if step == "verification":
            # Fetch current change_log
            response = client.table("user_plans").select("change_log").eq("id", user_plan_id).single().execute()
            current_log = response.data.get("change_log") or []

            current_log.append({
                "timestamp": now,
                "action": "initial_plan",
                "agent": "planning",
                "summary": message or "Created initial plan"
            })

            update_data["change_log"] = current_log

        # Update
        client.table("user_plans").update(update_data).eq("id", user_plan_id).execute()
        return True

    except Exception as e:
        print(f"Warning: Supabase update failed: {e}", file=sys.stderr)
        return False


def get_step_prompt(step: str, user_context: dict, occasion_context: dict) -> str:
    """Get the prompt for invoking a subagent."""
    user_prefs = user_context.get("preferences", "") if user_context else ""
    occasion_name = occasion_context.get("occasion", "the occasion") if occasion_context else "the occasion"
    city = occasion_context.get("city", "destination") if occasion_context else "destination"
    start_date = occasion_context.get("start_date", "") if occasion_context else ""
    end_date = occasion_context.get("end_date", "") if occasion_context else ""

    prompts = {
        "transportation": f"""Research transportation options for the trip to {city} for {occasion_name}.

**Your Tasks**:
1. Read files/process/user_context.json for user preferences
2. Read files/process/occasion_context.json for dates and location
3. Use the duffel skill to search for LIVE flight options
4. Apply user preferences (cabin class, timing, budget) to filter/rank
5. Write results to files/content/transportation/results.json

**Key Details**:
- Destination: {city}
- Dates: {start_date} to {end_date}
- User preferences available in context file

When complete, invoke 'orchestrating-workflow' skill with message:
'Transportation research complete. [summary of selected flights]'""",

        "accommodation": f"""Select accommodation for the trip to {city} for {occasion_name}.

**Your Tasks**:
1. Read files/process/occasion_context.json - use the accommodations masterlist
2. Read files/process/user_context.json for user preferences
3. DO NOT search externally - SELECT from the masterlist
4. Apply user preferences to filter and rank options
5. Select top 3 options (1 primary + 2 alternatives)
6. Write results to files/content/accommodation/results.json

**Data Source**: occasion_context.json contains pre-populated accommodations masterlist.
Filter by user preferences (stars, amenities, location) and select best matches.

When complete, invoke 'orchestrating-workflow' skill with message:
'Accommodation selection complete. [summary of selected hotels]'""",

        "activities": f"""Select activities for the trip to {city} for {occasion_name}.

**Your Tasks**:
1. Read files/process/occasion_context.json - use the activities masterlist
2. Read files/process/user_context.json for user preferences/interests
3. DO NOT search externally - SELECT from the masterlist
4. Calculate available time based on trip duration
5. Apply user preferences to filter and rank
6. Select appropriate activities to fill schedule (meals, attractions, etc.)
7. Write results to files/content/activities/results.json

**Data Source**: occasion_context.json contains pre-populated activities masterlist.
Consider occasion description and user interests when selecting.

When complete, invoke 'orchestrating-workflow' skill with message:
'Activities selection complete. [summary of selected activities]'""",

        "verification": f"""Verify and create day-by-day plan for {city} trip to {occasion_name}.

**Your Tasks**:
1. Read all selections from files/content/ (transportation, accommodation, activities)
2. Verify flight times vs check-in/check-out compatibility
3. Verify activity schedule doesn't conflict with main event
4. Use google-maps skill to calculate travel times between locations
5. Verify budget compliance if specified in user preferences
6. Create comprehensive day-by-day plan structure
7. Write plan to files/content/verification/results.json

**Plan Structure**:
- Summary with total costs
- Day-by-day schedule with times, activities, locations
- Travel logistics between locations
- Any warnings or recommendations

When complete, invoke 'orchestrating-workflow' skill with message:
'Verification complete. Created day-by-day plan. [summary]'"""
    }

    return prompts.get(step, f"Execute {step} step for the trip.")


def handle_init():
    """Initialize or check workflow state."""
    state = load_json_file(workflow_state_file)
    plan_context = load_json_file(plan_context_file)
    user_context = load_json_file(user_context_file)
    occasion_context = load_json_file(occasion_context_file)

    if not plan_context:
        return {
            "status": "error",
            "message": "No plan context found. Run workflow_init.py hook first."
        }

    if state and state.get("status") == "in_progress":
        # Resume existing workflow
        current_step = state.get("current_step", 0)
        if current_step < len(SEQUENCE):
            next_step = SEQUENCE[current_step]
            return {
                "status": "resume",
                "next_step": next_step,
                "prompt": get_step_prompt(next_step, user_context, occasion_context),
                "message": f"Resuming workflow at step: {next_step}"
            }

    # Start fresh
    state = {
        "user_plan_id": plan_context.get("user_plan_id"),
        "current_step": 0,
        "steps": SEQUENCE.copy(),
        "completed_steps": [],
        "status": "in_progress",
        "started_at": datetime.now().isoformat(),
        "history": []
    }
    save_json_file(workflow_state_file, state)

    first_step = SEQUENCE[0]
    return {
        "status": "start",
        "next_step": first_step,
        "prompt": get_step_prompt(first_step, user_context, occasion_context),
        "message": f"Starting workflow. First step: {first_step}"
    }


def handle_completed_step(completed_step: str, message: str):
    """Handle completion of a step and return next action."""
    state = load_json_file(workflow_state_file)
    plan_context = load_json_file(plan_context_file)
    user_context = load_json_file(user_context_file)
    occasion_context = load_json_file(occasion_context_file)

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

    # Load results from content directory
    results = load_step_results(completed_step)

    # Update Supabase with results
    user_plan_id = state.get("user_plan_id") or plan_context.get("user_plan_id")
    supabase_client = get_supabase_client()
    supabase_updated = False

    if results and supabase_client and user_plan_id:
        supabase_updated = update_supabase(supabase_client, user_plan_id, completed_step, results, message)

    # Update completed steps
    if completed_step not in state.get("completed_steps", []):
        state.setdefault("completed_steps", []).append(completed_step)

    # Record completion
    state.setdefault("history", []).append({
        "step": completed_step,
        "message": message,
        "completed_at": datetime.now().isoformat(),
        "supabase_updated": supabase_updated
    })

    # Get next step
    current_idx = SEQUENCE.index(completed_step)
    next_idx = current_idx + 1

    if next_idx >= len(SEQUENCE):
        # Workflow complete
        state["status"] = "completed"
        state["completed_at"] = datetime.now().isoformat()
        state["current_step"] = len(SEQUENCE)
        save_json_file(workflow_state_file, state)

        return {
            "status": "complete",
            "message": "Workflow complete! Planning finished.",
            "completed_steps": state["completed_steps"],
            "user_plan_id": user_plan_id
        }

    # Update current step
    next_step = SEQUENCE[next_idx]
    state["current_step"] = next_idx
    save_json_file(workflow_state_file, state)

    return {
        "status": "continue",
        "next_step": next_step,
        "prompt": get_step_prompt(next_step, user_context, occasion_context),
        "message": f"Step '{completed_step}' complete. Next: {next_step}",
        "completed_steps": state["completed_steps"],
        "supabase_updated": supabase_updated
    }


def handle_status():
    """Return current workflow status."""
    state = load_json_file(workflow_state_file)

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
        "user_plan_id": state.get("user_plan_id"),
        "history": state.get("history", [])
    }


def main():
    parser = argparse.ArgumentParser(description="Orchestrate planning workflow")
    parser.add_argument("--init", action="store_true", help="Initialize workflow")
    parser.add_argument("--completed-step", help="Mark a step as completed")
    parser.add_argument("--message", default="", help="Completion message")
    parser.add_argument("--status", action="store_true", help="Get workflow status")

    args = parser.parse_args()

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
