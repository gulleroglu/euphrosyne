#!/usr/bin/env python3
"""
UserPromptSubmit hook for Revision Agent

Input: JSON with user_plan_id and revision requests
  {"user_plan_id": "uuid", "requests": ["I want a cheaper hotel", ...]}

This hook:
1. Parses the JSON input
2. Fetches user_plan from Supabase
3. Fetches user from Supabase (for preferences)
4. Fetches occasion from Supabase (for masterlists)
5. Writes revision_context.json with all data
6. Initializes workflow_state.json
7. Outputs message to invoke orchestrating-workflow skill
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file in revision folder
project_root = Path(__file__).parent.parent.parent
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
project_root = Path(__file__).parent.parent.parent
process_dir = project_root / "files" / "process"
revision_context_file = process_dir / "revision_context.json"
workflow_state_file = process_dir / "workflow_state.json"


def get_supabase_client() -> Client:
    """Create Supabase client from environment variables."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables required")

    return create_client(url, key)


def fetch_user_plan(client: Client, user_plan_id: str) -> dict:
    """Fetch user_plan from Supabase."""
    response = client.table("user_plans").select("*").eq("id", user_plan_id).single().execute()
    return response.data


def fetch_user(client: Client, user_id: str) -> dict:
    """Fetch user from Supabase."""
    response = client.table("users").select("*").eq("id", user_id).single().execute()
    return response.data


def fetch_occasion(client: Client, occasion_id: str) -> dict:
    """Fetch occasion from Supabase (includes masterlists)."""
    response = client.table("occasions").select("*").eq("id", occasion_id).single().execute()
    return response.data


def parse_input() -> dict:
    """Parse JSON input from stdin."""
    try:
        input_data = json.load(sys.stdin)
        prompt = input_data.get("prompt", "").strip()

        # Try to parse as JSON
        try:
            parsed = json.loads(prompt)
            return parsed
        except json.JSONDecodeError:
            # Not JSON, try to extract user_plan_id and requests from natural language
            # For now, require proper JSON format
            raise ValueError("Input must be valid JSON with 'user_plan_id' and 'requests' fields")

    except json.JSONDecodeError:
        raise ValueError("Failed to parse input from stdin")


def build_revision_context(user_plan: dict, user: dict, occasion: dict, requests: list) -> dict:
    """Build the revision context with all necessary data."""
    return {
        "user_plan_id": user_plan["id"],
        "requests": requests,
        "user": {
            "id": user["id"],
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "email": user.get("email"),
            "preferences": user.get("preferences")  # Markdown text
        },
        "occasion": {
            "id": occasion["id"],
            "occasion": occasion.get("occasion"),
            "description": occasion.get("description"),
            "city": occasion.get("city"),
            "country": occasion.get("country"),
            "full_address": occasion.get("full_address"),
            "start_date": occasion.get("start_date"),
            "end_date": occasion.get("end_date"),
            "accommodations": occasion.get("accommodations"),  # Masterlist
            "activities": occasion.get("activities")  # Masterlist
        },
        "existing_plan": {
            "transportation": user_plan.get("transportation"),
            "accommodation": user_plan.get("accommodation"),
            "activities": user_plan.get("activities"),
            "plan": user_plan.get("plan")
        },
        "fetched_at": datetime.now().isoformat()
    }


def initialize_workflow_state(user_plan_id: str, requests: list) -> dict:
    """Create initial workflow state (steps will be set by orchestrator after analysis)."""
    return {
        "user_plan_id": user_plan_id,
        "requests": requests,
        "detected_subagents": [],  # Will be populated by orchestrate.py --init
        "current_step": 0,
        "steps": [],  # Will be populated by orchestrate.py --init
        "completed_steps": [],
        "status": "initialized",
        "started_at": datetime.now().isoformat(),
        "history": []
    }


# =============================================================================
# MAIN EXECUTION
# =============================================================================

try:
    # Parse input
    input_data = parse_input()

    user_plan_id = input_data.get("user_plan_id")
    requests = input_data.get("requests", [])

    if not user_plan_id:
        print("Error: 'user_plan_id' is required in the input JSON")
        sys.exit(1)

    if not requests or not isinstance(requests, list):
        print("Error: 'requests' must be a non-empty list of revision requests")
        sys.exit(1)

    # Connect to Supabase
    client = get_supabase_client()

    # Fetch user_plan
    user_plan = fetch_user_plan(client, user_plan_id)
    if not user_plan:
        print(f"Error: user_plan with id '{user_plan_id}' not found")
        sys.exit(1)

    # Fetch user
    user = fetch_user(client, user_plan["user_id"])
    if not user:
        print(f"Error: user with id '{user_plan['user_id']}' not found")
        sys.exit(1)

    # Fetch occasion (includes masterlists)
    occasion = fetch_occasion(client, user_plan["occasion_id"])
    if not occasion:
        print(f"Error: occasion with id '{user_plan['occasion_id']}' not found")
        sys.exit(1)

    # Build revision context
    revision_context = build_revision_context(user_plan, user, occasion, requests)

    # Create process directory if needed
    process_dir.mkdir(parents=True, exist_ok=True)

    # Save revision context
    with open(revision_context_file, 'w') as f:
        json.dump(revision_context, f, indent=2, default=str)

    # Initialize workflow state
    workflow_state = initialize_workflow_state(user_plan_id, requests)
    with open(workflow_state_file, 'w') as f:
        json.dump(workflow_state, f, indent=2)

    # Output success message
    print(f"""Revision workflow initialized.

User Plan: {user_plan_id}
User: {user.get('first_name')} {user.get('last_name')}
Occasion: {occasion.get('occasion')}
Revision Requests: {len(requests)}

Requests to process:
{chr(10).join(f'  - {r}' for r in requests)}

Context saved to: files/process/revision_context.json
State saved to: files/process/workflow_state.json

Use Skill tool to invoke 'orchestrating-workflow' skill to analyze requests and start revision workflow.""")

except ValueError as e:
    print(f"Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error initializing revision workflow: {e}")
    sys.exit(1)
