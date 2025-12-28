#!/usr/bin/env python3
"""
UserPromptSubmit hook: Initialize planning workflow for a user and occasion.

Input: {"user_id": "...", "occasion_id": "..."}
Output: Instruction to invoke orchestrating-workflow skill

This hook:
1. Parses user_id and occasion_id from input
2. Fetches user from Supabase (with preferences)
3. Fetches occasion from Supabase (with masterlists)
4. Creates user_plans row in Supabase
5. Writes context files (user_context.json, occasion_context.json, plan_context.json)
6. Initializes workflow_state.json
7. Returns message to invoke orchestrating-workflow skill
"""
import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv

# Paths
project_root = Path(__file__).parent.parent.parent
process_dir = project_root / "files" / "process"

# Load .env from planning agent root
load_dotenv(project_root / ".env")

workflow_state_file = process_dir / "workflow_state.json"
user_context_file = process_dir / "user_context.json"
occasion_context_file = process_dir / "occasion_context.json"
plan_context_file = process_dir / "plan_context.json"

# Supabase setup
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def get_supabase_client():
    """Create Supabase client."""
    try:
        from supabase import create_client
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables required")
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except ImportError:
        raise ImportError("supabase package not installed. Run: pip install supabase")


def parse_input(prompt: str) -> dict:
    """
    Parse input to extract user_id and occasion_id.

    Accepts:
    - JSON: {"user_id": "...", "occasion_id": "..."}
    - Text: user_id=xxx occasion_id=yyy
    """
    # Try JSON first
    try:
        data = json.loads(prompt)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # Try key=value parsing
    result = {}

    # Match user_id
    user_match = re.search(r'user_id[=:\s]+(["\']?)([a-f0-9-]+)\1', prompt, re.IGNORECASE)
    if user_match:
        result["user_id"] = user_match.group(2)

    # Match occasion_id
    occasion_match = re.search(r'occasion_id[=:\s]+(["\']?)([a-f0-9-]+)\1', prompt, re.IGNORECASE)
    if occasion_match:
        result["occasion_id"] = occasion_match.group(2)

    return result


def fetch_user(client, user_id: str) -> dict:
    """Fetch user from Supabase."""
    response = client.table("users").select("*").eq("id", user_id).single().execute()
    return response.data


def fetch_occasion(client, occasion_id: str) -> dict:
    """Fetch occasion from Supabase (includes masterlists)."""
    response = client.table("occasions").select("*").eq("id", occasion_id).single().execute()
    return response.data


def create_user_plan(client, user_id: str, occasion_id: str) -> dict:
    """Create new user_plans row and return it."""
    now = datetime.now().isoformat()

    plan_data = {
        "user_id": user_id,
        "occasion_id": occasion_id,
        "transportation": None,
        "accommodation": None,
        "activities": None,
        "plan": None,
        "change_log": [
            {
                "timestamp": now,
                "action": "plan_created",
                "agent": "planning",
                "summary": "Initiated planning workflow"
            }
        ],
        "created_at": now,
        "updated_at": now
    }

    response = client.table("user_plans").insert(plan_data).execute()
    return response.data[0]


def write_context_files(user: dict, occasion: dict, plan: dict):
    """Write all context files to process directory."""
    process_dir.mkdir(parents=True, exist_ok=True)

    # Write user context
    user_context = {
        "id": user["id"],
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "email": user.get("email"),
        "mobile_number": user.get("mobile_number"),
        "preferences": user.get("preferences")  # Markdown text
    }
    with open(user_context_file, 'w') as f:
        json.dump(user_context, f, indent=2)

    # Write occasion context (includes masterlists)
    occasion_context = {
        "id": occasion["id"],
        "occasion": occasion.get("occasion"),
        "description": occasion.get("description"),
        "city": occasion.get("city"),
        "country": occasion.get("country"),
        "full_address": occasion.get("full_address"),
        "start_date": occasion.get("start_date"),
        "end_date": occasion.get("end_date"),
        "accommodations": occasion.get("accommodations") or [],  # Masterlist
        "activities": occasion.get("activities") or []  # Masterlist
    }
    with open(occasion_context_file, 'w') as f:
        json.dump(occasion_context, f, indent=2, default=str)

    # Write plan context
    plan_context = {
        "user_plan_id": plan["id"],
        "user_id": user["id"],
        "occasion_id": occasion["id"],
        "created_at": plan.get("created_at")
    }
    with open(plan_context_file, 'w') as f:
        json.dump(plan_context, f, indent=2)


def initialize_workflow_state(user_plan_id: str) -> dict:
    """Create initial workflow state."""
    state = {
        "user_plan_id": user_plan_id,
        "current_step": 0,
        "steps": ["transportation", "accommodation", "activities", "verification"],
        "completed_steps": [],
        "status": "initialized",
        "started_at": datetime.now().isoformat(),
        "history": []
    }

    with open(workflow_state_file, 'w') as f:
        json.dump(state, f, indent=2)

    return state


def check_existing_workflow() -> tuple:
    """Check if there's an existing workflow in progress."""
    if not workflow_state_file.exists():
        return None, None

    try:
        with open(workflow_state_file, 'r') as f:
            state = json.load(f)

        if state.get("status") == "completed":
            return "complete", state
        elif state.get("status") in ["in_progress", "initialized"]:
            return "resume", state
        else:
            return None, None
    except:
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
    print("Error: No input provided. Please provide user_id and occasion_id.")
    print('Format: {"user_id": "...", "occasion_id": "..."}')
    sys.exit(1)

# Parse input
parsed = parse_input(prompt)
user_id = parsed.get("user_id")
occasion_id = parsed.get("occasion_id")

if not user_id or not occasion_id:
    print("Error: Both user_id and occasion_id are required.")
    print('Format: {"user_id": "...", "occasion_id": "..."}')
    sys.exit(1)

# Check for existing workflow
status_type, existing_state = check_existing_workflow()

if status_type == "resume":
    current_step = existing_state.get("current_step", 0)
    steps = existing_state.get("steps", [])
    if current_step < len(steps):
        current_agent = steps[current_step]
        print(f"Resuming workflow at step {current_step + 1}: {current_agent}")
        print(f"Use Skill tool to invoke 'orchestrating-workflow' skill to continue.")
        sys.exit(0)

# Initialize Supabase client
try:
    client = get_supabase_client()
except Exception as e:
    print(f"Error connecting to Supabase: {e}")
    sys.exit(1)

# Fetch user
try:
    user = fetch_user(client, user_id)
    if not user:
        print(f"Error: User not found: {user_id}")
        sys.exit(1)
except Exception as e:
    print(f"Error fetching user: {e}")
    sys.exit(1)

# Fetch occasion
try:
    occasion = fetch_occasion(client, occasion_id)
    if not occasion:
        print(f"Error: Occasion not found: {occasion_id}")
        sys.exit(1)
except Exception as e:
    print(f"Error fetching occasion: {e}")
    sys.exit(1)

# Validate occasion has masterlists
if not occasion.get("accommodations") or not occasion.get("activities"):
    print(f"Warning: Occasion '{occasion.get('occasion')}' may not have complete masterlists.")
    print("Consider running inventory agent first to populate accommodations and activities.")

# Create user_plans row
try:
    user_plan = create_user_plan(client, user_id, occasion_id)
except Exception as e:
    print(f"Error creating user_plan: {e}")
    sys.exit(1)

# Write context files
try:
    write_context_files(user, occasion, user_plan)
except Exception as e:
    print(f"Error writing context files: {e}")
    sys.exit(1)

# Initialize workflow state
try:
    workflow_state = initialize_workflow_state(user_plan["id"])
except Exception as e:
    print(f"Error initializing workflow state: {e}")
    sys.exit(1)

# Build initialization message
user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "User"
occasion_name = occasion.get("occasion", "Unknown Occasion")
city = occasion.get("city", "")
start_date = occasion.get("start_date", "")
end_date = occasion.get("end_date", "")

init_message = f"""Planning workflow initialized.

**User**: {user_name}
**Occasion**: {occasion_name}
**Location**: {city}, {occasion.get('country', '')}
**Dates**: {start_date} to {end_date}

**Context Files Created**:
- files/process/user_context.json (user preferences)
- files/process/occasion_context.json (occasion + masterlists)
- files/process/plan_context.json (user_plan_id reference)
- files/process/workflow_state.json (workflow tracking)

**Masterlists Available**:
- Accommodations: {len(occasion.get('accommodations') or [])} options
- Activities: {len(occasion.get('activities') or [])} options

Use Skill tool to invoke 'orchestrating-workflow' skill with message:
'Workflow initialized. Starting planning sequence for {user_name} attending {occasion_name}.'"""

print(init_message)
sys.exit(0)
