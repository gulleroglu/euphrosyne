#!/usr/bin/env python3
"""
UserPromptSubmit hook for Inventory Agent.

Input: occasion_id (UUID string)
Output: Instruction to invoke orchestrating-workflow skill

This hook:
1. Parses occasion_id from the user prompt
2. Checks for existing in-progress workflow (resume support)
3. Fetches occasion data from Supabase
4. Creates occasion_context.json
5. Returns message to invoke orchestrating-workflow skill

Note: Workflow state (execution_state.json) is managed by orchestrate.py, not this hook.
"""
import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

# Paths (hooks -> .claude -> inventory)
project_root = Path(__file__).parent.parent.parent

# Load .env from inventory agent root
load_dotenv(project_root / ".env")

process_dir = project_root / "files" / "process"
context_dir = project_root / "files" / "context"
execution_state_file = process_dir / "execution_state.json"
occasion_context_file = process_dir / "occasion_context.json"


def extract_occasion_id(prompt: str) -> str | None:
    """Extract UUID occasion_id from prompt."""
    uuid_pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    match = re.search(uuid_pattern, prompt)
    if match:
        return match.group(0)
    return None


def fetch_occasion_from_supabase(occasion_id: str) -> dict | None:
    """Fetch occasion data from Supabase."""
    try:
        from supabase import create_client

        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            print("Error: SUPABASE_URL and SUPABASE_KEY environment variables required.")
            return None

        client = create_client(supabase_url, supabase_key)

        response = client.table("occasions").select("*").eq("id", occasion_id).single().execute()

        if response.data:
            return response.data
        else:
            print(f"Error: No occasion found with id: {occasion_id}")
            return None

    except ImportError:
        print("Error: supabase-py package not installed. Run: pip install supabase")
        return None
    except Exception as e:
        print(f"Error fetching occasion: {e}")
        return None


def analyze_existing_workflow(occasion_id: str) -> tuple:
    """
    Check if there's an existing workflow in progress for this occasion.

    Returns:
        (status, resume_info) where status is one of:
        - None: No existing workflow
        - "resume_accommodation": Resume at accommodation step
        - "resume_activities": Resume at activities step
        - "completed": Workflow already completed
        - "different_occasion": Different occasion in progress
    """
    if not execution_state_file.exists():
        return None, None

    try:
        with open(execution_state_file, 'r') as f:
            state = json.load(f)

        workflow = state.get("workflow", {})
        existing_occasion_id = workflow.get("occasion_id")

        # Different occasion - will start fresh
        if existing_occasion_id != occasion_id:
            return "different_occasion", {"existing_id": existing_occasion_id}

        # Same occasion - check status
        if workflow.get("workflow_complete"):
            return "completed", state

        if workflow.get("status") != "in_progress":
            return None, None

        # Check what step we're on by examining context files
        acc_context = context_dir / "accommodation.json"
        act_context = context_dir / "activities.json"

        acc_exists = acc_context.exists()
        act_exists = act_context.exists()

        if acc_exists and not act_exists:
            # Accommodation done, resume at activities
            return "resume_activities", state
        elif not acc_exists:
            # Resume at accommodation
            return "resume_accommodation", state
        else:
            # Both exist but workflow not complete - unusual, restart
            return None, None

    except Exception as e:
        print(f"Warning: Could not analyze existing workflow: {e}")
        return None, None


# =============================================================================
# MAIN EXECUTION
# =============================================================================

# Load input from stdin
try:
    input_data = json.load(sys.stdin)
    prompt = input_data.get('prompt', '').strip()
except json.JSONDecodeError:
    prompt = ""

if not prompt:
    print("Error: No occasion_id provided. Please provide an occasion UUID.")
    sys.exit(1)

# Extract occasion_id from prompt
occasion_id = extract_occasion_id(prompt)

if not occasion_id:
    print("Error: Could not find a valid UUID in the input. Please provide an occasion_id.")
    sys.exit(1)

# Check for existing workflow
status, existing_state = analyze_existing_workflow(occasion_id)

if status == "completed":
    print(f"Workflow already completed for this occasion.")
    print(f"To re-run, delete files/process/execution_state.json and try again.")
    print(f"\nOr use Skill tool to invoke 'orchestrating-workflow' with --agent status to see details.")
    sys.exit(0)

if status == "resume_activities":
    # Accommodation done, resume at activities
    occasion_context = None
    if occasion_context_file.exists():
        with open(occasion_context_file, 'r') as f:
            occasion_context = json.load(f)

    occasion_name = occasion_context.get("occasion", "occasion") if occasion_context else "occasion"

    print(f"Resuming workflow for {occasion_name}.")
    print(f"Accommodation step already complete (files/context/accommodation.json exists).")
    print(f"\nUse Skill tool to invoke 'orchestrating-workflow' skill with message:")
    print(f"'Resuming workflow. Accommodation complete, proceeding to activities.'")
    sys.exit(0)

if status == "resume_accommodation":
    # Resume at accommodation step
    occasion_context = None
    if occasion_context_file.exists():
        with open(occasion_context_file, 'r') as f:
            occasion_context = json.load(f)

    occasion_name = occasion_context.get("occasion", "occasion") if occasion_context else "occasion"

    print(f"Resuming workflow for {occasion_name}.")
    print(f"Workflow was interrupted. Resuming at accommodation step.")
    print(f"\nUse Skill tool to invoke 'orchestrating-workflow' skill with message:")
    print(f"'Resuming workflow at accommodation step.'")
    sys.exit(0)

if status == "different_occasion":
    print(f"Warning: Different occasion in progress (ID: {existing_state.get('existing_id', 'unknown')}).")
    print(f"Starting fresh workflow for new occasion: {occasion_id}")

# Fetch occasion from Supabase
occasion_data = fetch_occasion_from_supabase(occasion_id)

if not occasion_data:
    sys.exit(1)

# Create occasion context
occasion_context = {
    "id": occasion_data.get("id"),
    "occasion": occasion_data.get("occasion"),
    "description": occasion_data.get("description"),
    "city": occasion_data.get("city"),
    "country": occasion_data.get("country"),
    "full_address": occasion_data.get("full_address"),
    "start_date": occasion_data.get("start_date"),
    "end_date": occasion_data.get("end_date")
}

# Create ALL directories upfront (subagents/skills should never create folders)
process_dir.mkdir(parents=True, exist_ok=True)
context_dir.mkdir(parents=True, exist_ok=True)
(project_root / "files" / "content").mkdir(parents=True, exist_ok=True)
(project_root / "files" / "content" / "accommodation").mkdir(parents=True, exist_ok=True)
(project_root / "files" / "content" / "activities").mkdir(parents=True, exist_ok=True)

# Save occasion context (orchestrate.py will handle execution_state.json)
with open(occasion_context_file, 'w') as f:
    json.dump(occasion_context, f, indent=2)

# Restore existing context files from Supabase if they exist
# This allows resuming from where we left off
accommodations_data = occasion_data.get("accommodations")
activities_data = occasion_data.get("activities")

if accommodations_data:
    acc_context_file = context_dir / "accommodation.json"
    with open(acc_context_file, 'w') as f:
        json.dump(accommodations_data, f, indent=2)
    print(f"Restored accommodation.json from Supabase ({len(accommodations_data.get('hotels', []))} hotels)")

if activities_data:
    act_context_file = context_dir / "activities.json"
    with open(act_context_file, 'w') as f:
        json.dump(activities_data, f, indent=2)
    # Count places across categories
    place_count = sum(len(cat.get('places', [])) for cat in activities_data.get('categories', []))
    print(f"Restored activities.json from Supabase ({place_count} places)")

# Determine workflow action based on what was restored
if accommodations_data and activities_data:
    # Both exist - workflow already complete, just verify
    action = "resume"
    action_msg = "Both accommodation and activities already exist. Verifying and updating Supabase."
elif accommodations_data:
    # Only accommodation - resume at activities
    action = "resume"
    action_msg = "Accommodation already exists. Resuming at activities step."
else:
    # Neither exists - fresh start
    action = "init"
    action_msg = "Starting fresh inventory workflow."

# Build initialization message
init_message = f"""Inventory workflow initialized for occasion.

Occasion Context:
- Occasion: {occasion_context.get('occasion', 'Unknown')}
- Description: {occasion_context.get('description', 'No description')[:100]}...
- Location: {occasion_context.get('city', 'Unknown')}, {occasion_context.get('country', 'Unknown')}
- Dates: {occasion_context.get('start_date', 'TBD')} to {occasion_context.get('end_date', 'TBD')}

Status: {action_msg}

Use Skill tool to invoke 'orchestrating-workflow' skill with message:
'Workflow initialized. Starting inventory sequence for {occasion_context.get('occasion', 'occasion')}.'"""

print(init_message)
sys.exit(0)
