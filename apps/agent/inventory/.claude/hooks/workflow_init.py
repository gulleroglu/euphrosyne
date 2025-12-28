#!/usr/bin/env python3
"""
UserPromptSubmit hook for Inventory Agent.

Input: occasion_id (UUID string)
Output: Instruction to invoke orchestrating-workflow skill

This hook:
1. Parses occasion_id from the user prompt
2. Fetches occasion data from Supabase
3. Creates occasion_context.json
4. Initializes workflow_state.json
5. Returns message to invoke orchestrating-workflow skill
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
workflow_state_file = process_dir / "workflow_state.json"
occasion_context_file = process_dir / "occasion_context.json"


def extract_occasion_id(prompt: str) -> str | None:
    """Extract UUID occasion_id from prompt."""
    # Match UUID pattern
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


def initialize_workflow_state(occasion_id: str) -> dict:
    """Create initial workflow state for inventory agent."""
    return {
        "occasion_id": occasion_id,
        "current_step": 0,
        "steps": ["accommodation", "activities"],
        "completed_steps": [],
        "status": "initialized",
        "started_at": datetime.now().isoformat(),
        "history": []
    }


def analyze_existing_workflow() -> tuple:
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
    except Exception:
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
status_type, existing_state = analyze_existing_workflow()

if status_type == "resume":
    existing_occasion_id = existing_state.get("occasion_id")
    if existing_occasion_id == occasion_id:
        current_step = existing_state.get("current_step", 0)
        steps = existing_state.get("steps", [])
        if current_step < len(steps):
            current_agent = steps[current_step]
            print(f"Resuming workflow at step {current_step + 1}: {current_agent}")
            print(f"Use Skill tool to invoke 'orchestrating-workflow' skill to continue.")
            sys.exit(0)
    else:
        print(f"New occasion detected. Starting fresh workflow for: {occasion_id}")

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

# Create process directory if needed
process_dir.mkdir(parents=True, exist_ok=True)

# Save occasion context
with open(occasion_context_file, 'w') as f:
    json.dump(occasion_context, f, indent=2)

# Initialize workflow state
workflow_state = initialize_workflow_state(occasion_id)
with open(workflow_state_file, 'w') as f:
    json.dump(workflow_state, f, indent=2)

# Build initialization message
init_message = f"""Inventory workflow initialized for occasion.

Occasion Context:
- Occasion: {occasion_context.get('occasion', 'Unknown')}
- Description: {occasion_context.get('description', 'No description')[:100]}...
- Location: {occasion_context.get('city', 'Unknown')}, {occasion_context.get('country', 'Unknown')}
- Dates: {occasion_context.get('start_date', 'TBD')} to {occasion_context.get('end_date', 'TBD')}

Use Skill tool to invoke 'orchestrating-workflow' skill with message:
'Workflow initialized. Starting inventory sequence for {occasion_context.get('occasion', 'occasion')}.'"""

print(init_message)
sys.exit(0)
