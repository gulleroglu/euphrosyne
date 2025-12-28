#!/usr/bin/env python3
"""
Orchestration script for inventory agent workflow.

Updates workflow state and returns the next step to execute.
On final step, compiles results and updates Supabase occasions table.

Usage:
    python3 orchestrate.py --init
    python3 orchestrate.py --completed-step accommodation --message "Found 45 hotels"
    python3 orchestrate.py --completed-step activities --message "Found 120 activities"
    python3 orchestrate.py --status
"""
import argparse
import json
import sys
import os
import glob as glob_module
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

# Paths (scripts -> orchestrating-workflow -> skills -> .claude -> inventory)
project_root = Path(__file__).parent.parent.parent.parent.parent

# Load .env from inventory agent root
load_dotenv(project_root / ".env")
process_dir = project_root / "files" / "process"
content_dir = project_root / "files" / "content"
workflow_state_file = process_dir / "workflow_state.json"
occasion_context_file = process_dir / "occasion_context.json"

# Fixed sequence for inventory agent
SEQUENCE = ["accommodation", "activities"]


def load_workflow_state():
    """Load current workflow state."""
    if not workflow_state_file.exists():
        return None
    try:
        with open(workflow_state_file, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def save_workflow_state(state):
    """Save workflow state."""
    process_dir.mkdir(parents=True, exist_ok=True)
    with open(workflow_state_file, 'w') as f:
        json.dump(state, f, indent=2)


def load_occasion_context():
    """Load occasion context."""
    if not occasion_context_file.exists():
        return None
    try:
        with open(occasion_context_file, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def get_next_step(current_step):
    """Get the next step in the sequence."""
    if current_step not in SEQUENCE:
        return SEQUENCE[0]

    idx = SEQUENCE.index(current_step)
    if idx + 1 >= len(SEQUENCE):
        return None  # Workflow complete

    return SEQUENCE[idx + 1]


def get_step_prompt(step, occasion_context):
    """Get the prompt for invoking a subagent."""
    occasion = occasion_context.get("occasion", "the occasion") if occasion_context else "the occasion"
    city = occasion_context.get("city", "the city") if occasion_context else "the city"
    country = occasion_context.get("country", "") if occasion_context else ""
    description = occasion_context.get("description", "") if occasion_context else ""

    location = f"{city}, {country}" if country else city

    prompts = {
        "accommodation": f"""Build exhaustive masterlist of accommodations for {occasion} in {location}.

1. Read files/process/occasion_context.json for location and date context
2. Use the duffel skill to search for all hotels in {city}
3. Use the google-maps skill to search for lodging places
4. Write results to files/content/accommodations/ as JSON files
5. Include ALL hotels regardless of price or availability - this is a masterlist

When complete, use Skill tool to invoke 'orchestrating-workflow' with message:
'Accommodation research complete. Found [count] hotels from duffel and google-maps.'""",

        "activities": f"""Build exhaustive masterlist of activities for {occasion} in {location}.

Occasion Description: {description[:200] if description else 'General occasion'}

1. Read files/process/occasion_context.json for location and description context
2. Use the occasion description to understand what activities are relevant
3. Use the google-maps skill to search for:
   - Restaurants, cafes, bars
   - Tourist attractions, museums, art galleries
   - Parks, spas, shopping centers
   - Occasion-specific venues based on the description
4. Write results to files/content/activities/ as JSON files
5. Include ALL places regardless of price level - this is a masterlist

When complete, use Skill tool to invoke 'orchestrating-workflow' with message:
'Activities research complete. Found [count] activities across [N] categories.'"""
    }

    return prompts.get(step, f"Execute {step} step.")


def compile_results():
    """Compile all results from content directories into flat lists."""
    accommodations = []
    activities = []

    # Read accommodations
    accommodations_dir = content_dir / "accommodations"
    if accommodations_dir.exists():
        for file_path in accommodations_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        accommodations.extend(data)
                    elif isinstance(data, dict):
                        accommodations.append(data)
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)

    # Read activities
    activities_dir = content_dir / "activities"
    if activities_dir.exists():
        for file_path in activities_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        activities.extend(data)
                    elif isinstance(data, dict):
                        activities.append(data)
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)

    # Deduplicate by id
    seen_accommodation_ids = set()
    unique_accommodations = []
    for acc in accommodations:
        acc_id = acc.get("id")
        if acc_id and acc_id not in seen_accommodation_ids:
            seen_accommodation_ids.add(acc_id)
            unique_accommodations.append(acc)
        elif not acc_id:
            unique_accommodations.append(acc)

    seen_activity_ids = set()
    unique_activities = []
    for act in activities:
        act_id = act.get("id")
        if act_id and act_id not in seen_activity_ids:
            seen_activity_ids.add(act_id)
            unique_activities.append(act)
        elif not act_id:
            unique_activities.append(act)

    return unique_accommodations, unique_activities


def update_supabase(occasion_id, accommodations, activities):
    """Update Supabase occasions table with compiled masterlists."""
    try:
        from supabase import create_client

        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            return False, "SUPABASE_URL and SUPABASE_KEY environment variables required"

        client = create_client(supabase_url, supabase_key)

        response = client.table("occasions").update({
            "accommodations": accommodations,
            "activities": activities,
            "updated_at": datetime.now().isoformat()
        }).eq("id", occasion_id).execute()

        if response.data:
            return True, "Supabase updated successfully"
        else:
            return False, "No rows updated in Supabase"

    except ImportError:
        return False, "supabase-py package not installed"
    except Exception as e:
        return False, str(e)


def handle_init():
    """Initialize or resume workflow state."""
    state = load_workflow_state()
    occasion_context = load_occasion_context()

    if not occasion_context:
        return {
            "status": "error",
            "message": "No occasion context found. Run workflow_init.py hook first."
        }

    if state and state.get("status") == "in_progress":
        # Resume existing workflow
        current_step = state.get("current_step", 0)
        if current_step < len(SEQUENCE):
            next_step = SEQUENCE[current_step]
            return {
                "status": "resume",
                "next_step": next_step,
                "prompt": get_step_prompt(next_step, occasion_context),
                "message": f"Resuming workflow at step: {next_step}"
            }

    # Start fresh
    state = {
        "occasion_id": occasion_context.get("id"),
        "current_step": 0,
        "steps": SEQUENCE.copy(),
        "completed_steps": [],
        "status": "in_progress",
        "started_at": datetime.now().isoformat(),
        "history": []
    }
    save_workflow_state(state)

    first_step = SEQUENCE[0]
    return {
        "status": "start",
        "next_step": first_step,
        "prompt": get_step_prompt(first_step, occasion_context),
        "message": f"Starting inventory workflow. First step: {first_step}"
    }


def handle_completed_step(completed_step, message):
    """Handle completion of a step and return next action."""
    state = load_workflow_state()
    occasion_context = load_occasion_context()

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

    # Record completion in history
    state.setdefault("history", []).append({
        "step": completed_step,
        "message": message,
        "completed_at": datetime.now().isoformat()
    })

    # Get next step
    next_step = get_next_step(completed_step)

    if next_step is None:
        # Workflow complete - compile results and update Supabase
        accommodations, activities = compile_results()

        occasion_id = state.get("occasion_id")
        success, supabase_message = update_supabase(occasion_id, accommodations, activities)

        state["status"] = "completed"
        state["completed_at"] = datetime.now().isoformat()
        state["current_step"] = len(SEQUENCE)
        state["supabase_updated"] = success
        state["supabase_message"] = supabase_message
        save_workflow_state(state)

        occasion_name = occasion_context.get("occasion", "occasion") if occasion_context else "occasion"

        return {
            "status": "complete",
            "message": f"Workflow complete! Inventory masterlist built for {occasion_name}.",
            "summary": {
                "accommodations_count": len(accommodations),
                "activities_count": len(activities),
                "supabase_updated": success,
                "supabase_message": supabase_message
            },
            "completed_steps": state["completed_steps"]
        }

    # Update current step
    state["current_step"] = SEQUENCE.index(next_step)
    save_workflow_state(state)

    return {
        "status": "continue",
        "next_step": next_step,
        "prompt": get_step_prompt(next_step, occasion_context),
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
        "occasion_id": state.get("occasion_id"),
        "current_step": state.get("current_step", 0),
        "steps": state.get("steps", SEQUENCE),
        "completed_steps": state.get("completed_steps", []),
        "history": state.get("history", [])
    }


def main():
    parser = argparse.ArgumentParser(description="Orchestrate inventory workflow")
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
