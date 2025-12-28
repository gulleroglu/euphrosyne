#!/usr/bin/env python3
"""
Orchestration script for Revision Agent workflow.

Analyzes revision requests to determine which subagents to run dynamically.
Updates workflow state and returns the next step to execute.

Usage:
    python3 orchestrate.py --init
    python3 orchestrate.py --completed-step accommodation --message "Found 3 cheaper alternatives"
    python3 orchestrate.py --status
"""
import argparse
import json
import sys
import os
import re
import uuid
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file in revision folder
project_root = Path(__file__).parent.parent.parent.parent.parent
env_file = project_root / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)
else:
    # Try parent directories
    for parent in [project_root.parent, project_root.parent.parent]:
        env_file = parent / ".env"
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)
            break

try:
    from supabase import create_client, Client
except ImportError:
    print("Error: supabase package not installed. Run: pip install supabase")
    sys.exit(1)

# Paths
project_root = Path(__file__).parent.parent.parent.parent.parent
process_dir = project_root / "files" / "process"
content_dir = project_root / "files" / "content"
workflow_state_file = process_dir / "workflow_state.json"
revision_context_file = process_dir / "revision_context.json"

# Keyword mappings for request analysis
KEYWORD_MAPPINGS = {
    "transportation": [
        "flight", "airline", "departure", "arrival", "layover", "direct",
        "stopover", "airport", "transfer", "taxi", "uber", "car", "drive",
        "route", "earlier", "later", "morning", "evening", "red-eye"
    ],
    "accommodation": [
        "hotel", "accommodation", "room", "stay", "lodging", "boutique",
        "resort", "hostel", "villa", "apartment", "suite", "check-in",
        "check-out", "bed", "star", "stars"
    ],
    "activities": [
        "restaurant", "activity", "tour", "museum", "dinner", "lunch",
        "brunch", "breakfast", "cafe", "bar", "club", "spa", "show",
        "concert", "game", "match", "event", "attraction", "sightseeing",
        "shopping", "gallery", "park", "beach", "excursion", "dining",
        "upscale", "posh", "fancy", "casual", "michelin"
    ]
}

# Price-related keywords (need context to determine domain)
PRICE_KEYWORDS = ["cheaper", "expensive", "budget", "luxury", "affordable", "cost", "price"]

# Location-related keywords (may affect multiple domains)
LOCATION_KEYWORDS = ["closer", "near", "nearby", "location", "distance", "walking", "central"]


def get_supabase_client() -> Client:
    """Create Supabase client from environment variables."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables required")
    return create_client(url, key)


def load_workflow_state() -> dict:
    """Load current workflow state."""
    if not workflow_state_file.exists():
        return None
    try:
        with open(workflow_state_file, 'r') as f:
            return json.load(f)
    except:
        return None


def save_workflow_state(state: dict):
    """Save workflow state."""
    process_dir.mkdir(parents=True, exist_ok=True)
    with open(workflow_state_file, 'w') as f:
        json.dump(state, f, indent=2)


def load_revision_context() -> dict:
    """Load revision context."""
    if not revision_context_file.exists():
        return None
    try:
        with open(revision_context_file, 'r') as f:
            return json.load(f)
    except:
        return None


def analyze_requests(requests: list) -> list:
    """
    Analyze revision requests to determine which subagents need to run.

    Returns ordered list of subagents: transportation -> accommodation -> activities
    Always appends 'verification' at the end.
    """
    detected = set()

    for request in requests:
        request_lower = request.lower()

        # Check for domain-specific keywords
        for domain, keywords in KEYWORD_MAPPINGS.items():
            for keyword in keywords:
                if keyword in request_lower:
                    detected.add(domain)
                    break

        # Check for price keywords - need to infer domain
        has_price_keyword = any(kw in request_lower for kw in PRICE_KEYWORDS)
        if has_price_keyword:
            # Check for domain hints
            if any(kw in request_lower for kw in ["hotel", "room", "stay", "accommodation"]):
                detected.add("accommodation")
            elif any(kw in request_lower for kw in ["flight", "airline", "travel"]):
                detected.add("transportation")
            elif any(kw in request_lower for kw in ["restaurant", "dinner", "lunch", "activity", "tour"]):
                detected.add("activities")
            else:
                # Generic price request - affects all domains
                detected.update(["transportation", "accommodation", "activities"])

        # Check for location keywords - typically affects accommodation and activities
        has_location_keyword = any(kw in request_lower for kw in LOCATION_KEYWORDS)
        if has_location_keyword:
            detected.update(["accommodation", "activities"])

    # If nothing detected, default to verification only
    if not detected:
        return ["verification"]

    # Order by dependency: transportation -> accommodation -> activities
    ordered = []
    for domain in ["transportation", "accommodation", "activities"]:
        if domain in detected:
            ordered.append(domain)

    # Always add verification at the end
    ordered.append("verification")

    return ordered


def get_step_prompt(step: str, context: dict) -> str:
    """Get the prompt for invoking a subagent for revision."""
    occasion_name = context.get("occasion", {}).get("occasion", "the occasion")
    requests = context.get("requests", [])
    requests_text = "\n".join(f"  - {r}" for r in requests)

    prompts = {
        "transportation": f"""Revise transportation for the trip to {occasion_name}.

REVISION REQUESTS:
{requests_text}

INSTRUCTIONS:
1. Read files/process/revision_context.json for:
   - existing_plan.transportation (current selection)
   - user.preferences (markdown)
   - requests (what to change)

2. Identify transportation-related requests from the list

3. Use existing transportation data as BASELINE

4. Search for alternatives via duffel skill that address the requests:
   - If "cheaper" requested, find lower-cost flights
   - If "direct" requested, filter for non-stop flights
   - If "earlier/later" requested, adjust departure times

5. Write revised results to files/content/transportation/revised.json

6. When complete, invoke 'orchestrating-workflow' skill with message:
   'Transportation revision complete. [summary of changes]'""",

        "accommodation": f"""Revise accommodation for the trip to {occasion_name}.

REVISION REQUESTS:
{requests_text}

INSTRUCTIONS:
1. Read files/process/revision_context.json for:
   - existing_plan.accommodation (current selection)
   - occasion.accommodations (masterlist of alternatives)
   - user.preferences (markdown)
   - requests (what to change)

2. Identify accommodation-related requests from the list

3. Use existing accommodation data as BASELINE

4. Select alternatives from occasion masterlist that address the requests:
   - If "cheaper" requested, find lower-cost hotels
   - If "closer" requested, find hotels nearer to venue
   - If "better rated" requested, find higher-rated options

5. Write revised results to files/content/accommodation/revised.json

6. When complete, invoke 'orchestrating-workflow' skill with message:
   'Accommodation revision complete. [summary of changes]'""",

        "activities": f"""Revise activities for the trip to {occasion_name}.

REVISION REQUESTS:
{requests_text}

INSTRUCTIONS:
1. Read files/process/revision_context.json for:
   - existing_plan.activities (current selections)
   - occasion.activities (masterlist of alternatives)
   - user.preferences (markdown)
   - requests (what to change)

2. Identify activities-related requests from the list

3. Use existing activities data as BASELINE

4. Select alternatives or additions from occasion masterlist:
   - If "upscale restaurant" requested, find higher-end dining
   - If "more museums" requested, add museum activities
   - If "remove X" requested, exclude that activity

5. Write revised results to files/content/activities/revised.json

6. When complete, invoke 'orchestrating-workflow' skill with message:
   'Activities revision complete. [summary of changes]'""",

        "verification": f"""Verify revised plan for the trip to {occasion_name}.

REVISION REQUESTS:
{requests_text}

INSTRUCTIONS:
1. Read all revised data from files/content/*/revised.json

2. Compare with files/process/revision_context.json existing_plan

3. Validate:
   - No schedule conflicts introduced
   - Changes address the original requests
   - Overall plan remains coherent

4. Regenerate day-by-day plan with revision notes

5. Write verification results to files/content/verification/verified.json

6. When complete, invoke 'orchestrating-workflow' skill with message:
   'Verification complete. [summary of validation]'"""
    }

    return prompts.get(step, f"Execute {step} step for revision.")


def update_supabase_field(user_plan_id: str, field: str, data: dict) -> bool:
    """Update a specific field in user_plans table."""
    try:
        client = get_supabase_client()
        client.table("user_plans").update({
            field: data,
            "updated_at": datetime.now().isoformat()
        }).eq("id", user_plan_id).execute()
        return True
    except Exception as e:
        print(f"Warning: Failed to update Supabase {field}: {e}")
        return False


def read_content_file(step: str) -> dict:
    """Read the revised content file for a step."""
    file_path = content_dir / step / "revised.json"
    if not file_path.exists():
        return None
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        return None


def compile_change_log_entry(state: dict, context: dict) -> dict:
    """Compile a change log entry for this revision."""
    changes = {}

    for step in state.get("completed_steps", []):
        if step == "verification":
            continue

        revised_data = read_content_file(step)
        if revised_data:
            changes[step] = {
                "revised": True,
                "summary": revised_data.get("summary", "Changes applied")
            }

    return {
        "revision_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "requests": context.get("requests", []),
        "changes": changes,
        "subagents_invoked": state.get("steps", [])
    }


def finalize_revision(state: dict, context: dict) -> dict:
    """Finalize the revision: update plan and change_log in Supabase."""
    user_plan_id = state.get("user_plan_id")

    # Read verification results (contains regenerated plan)
    verification_data = read_content_file("verification")

    # Compile change log entry
    change_log_entry = compile_change_log_entry(state, context)

    # Get existing change_log from context
    existing_plan = context.get("existing_plan", {})
    existing_change_log = existing_plan.get("change_log", []) or []

    # Append new entry
    updated_change_log = existing_change_log + [change_log_entry]

    try:
        client = get_supabase_client()

        update_data = {
            "change_log": updated_change_log,
            "updated_at": datetime.now().isoformat()
        }

        # Add regenerated plan if available
        if verification_data and "plan" in verification_data:
            update_data["plan"] = verification_data["plan"]

        client.table("user_plans").update(update_data).eq("id", user_plan_id).execute()

        return {
            "supabase_updated": True,
            "change_log_entries": len(updated_change_log)
        }
    except Exception as e:
        return {
            "supabase_updated": False,
            "error": str(e)
        }


def handle_init():
    """Initialize the revision workflow by analyzing requests."""
    state = load_workflow_state()
    context = load_revision_context()

    if not context:
        return {
            "status": "error",
            "message": "No revision context found. Run workflow_init.py hook first."
        }

    requests = context.get("requests", [])
    if not requests:
        return {
            "status": "error",
            "message": "No revision requests found in context."
        }

    # Analyze requests to determine subagents
    detected_subagents = analyze_requests(requests)

    # Update workflow state with dynamic sequence
    state = state or {}
    state.update({
        "user_plan_id": context.get("user_plan_id"),
        "requests": requests,
        "detected_subagents": detected_subagents,
        "current_step": 0,
        "steps": detected_subagents,
        "completed_steps": [],
        "status": "in_progress",
        "started_at": datetime.now().isoformat(),
        "history": []
    })
    save_workflow_state(state)

    first_step = detected_subagents[0]

    return {
        "status": "start",
        "detected_subagents": detected_subagents,
        "next_step": first_step,
        "prompt": get_step_prompt(first_step, context),
        "message": f"Analyzed {len(requests)} request(s). Subagents to run: {' -> '.join(detected_subagents)}"
    }


def handle_completed_step(completed_step: str, message: str):
    """Handle completion of a step and return next action."""
    state = load_workflow_state()
    context = load_revision_context()

    if not state:
        return {
            "status": "error",
            "message": "No workflow state found. Initialize workflow first."
        }

    steps = state.get("steps", [])
    if completed_step not in steps:
        return {
            "status": "error",
            "message": f"Step '{completed_step}' not in current workflow: {steps}"
        }

    # Update completed steps
    if completed_step not in state.get("completed_steps", []):
        state.setdefault("completed_steps", []).append(completed_step)

    # Record completion
    history_entry = {
        "step": completed_step,
        "message": message,
        "completed_at": datetime.now().isoformat()
    }

    # Progressive Supabase update for non-verification steps
    if completed_step != "verification":
        revised_data = read_content_file(completed_step)
        if revised_data:
            user_plan_id = state.get("user_plan_id")
            success = update_supabase_field(user_plan_id, completed_step, revised_data)
            history_entry["supabase_updated"] = success

    state.setdefault("history", []).append(history_entry)

    # Determine next step
    current_idx = steps.index(completed_step)

    if current_idx + 1 >= len(steps):
        # Workflow complete - finalize
        state["status"] = "completed"
        state["completed_at"] = datetime.now().isoformat()
        save_workflow_state(state)

        # Finalize in Supabase
        finalize_result = finalize_revision(state, context)

        return {
            "status": "complete",
            "message": "Revision workflow complete! All changes applied.",
            "completed_steps": state["completed_steps"],
            "supabase": finalize_result
        }

    # Move to next step
    next_step = steps[current_idx + 1]
    state["current_step"] = current_idx + 1
    save_workflow_state(state)

    return {
        "status": "continue",
        "next_step": next_step,
        "prompt": get_step_prompt(next_step, context),
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
        "user_plan_id": state.get("user_plan_id"),
        "requests": state.get("requests", []),
        "detected_subagents": state.get("detected_subagents", []),
        "current_step": state.get("current_step", 0),
        "steps": state.get("steps", []),
        "completed_steps": state.get("completed_steps", [])
    }


def main():
    parser = argparse.ArgumentParser(description="Orchestrate revision workflow")
    parser.add_argument("--init", action="store_true", help="Initialize workflow and analyze requests")
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
        # Default to init
        result = handle_init()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
