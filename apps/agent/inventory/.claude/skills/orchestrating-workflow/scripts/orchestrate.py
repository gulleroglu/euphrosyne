#!/usr/bin/env python3
"""
Workflow Orchestrator - Inventory Agent

Receives messages from subagents about what they completed, validates outputs,
updates execution state, and returns next action instructions.

Architecture:
- execution_state.json: TEMPORAL - workflow progress + history (audit trail)
- occasion_context.json: SPATIAL - occasion details from Supabase
- files/content/: Raw API outputs (all hotels, all places)
- files/context/: Curated/filtered lists for Supabase update

Usage:
    # Initialize workflow
    python3 orchestrate.py --agent init

    # After accommodation subagent
    python3 orchestrate.py --agent accommodation --accommodation-count 45

    # After activities subagent
    python3 orchestrate.py --agent activities --activities-count 120

    # Check status
    python3 orchestrate.py --agent status
"""

import argparse
import json
import sys
import os
import fcntl
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

# Paths (scripts -> orchestrating-workflow -> skills -> .claude -> inventory)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

# Load .env from inventory agent root
load_dotenv(PROJECT_ROOT / ".env")

# Directories
PROCESS_DIR = PROJECT_ROOT / "files" / "process"
CONTENT_DIR = PROJECT_ROOT / "files" / "content"
CONTEXT_DIR = PROJECT_ROOT / "files" / "context"
EXECUTION_STATE = PROCESS_DIR / "execution_state.json"
OCCASION_CONTEXT = PROCESS_DIR / "occasion_context.json"
EXECUTION_STATE_LOCK = PROCESS_DIR / "execution_state.lock"

# Fixed sequence for inventory agent
SEQUENCE = ["accommodation", "activities"]


# =============================================================================
# STATE MANAGEMENT FUNCTIONS
# =============================================================================

def load_execution_state():
    """Load execution_state.json or create initial state"""
    if not EXECUTION_STATE.exists():
        return {
            "schema_version": "1.0",
            "workflow": {
                "status": "idle",
                "current_step": None,
                "next_agent": "accommodation",
                "started_at": None,
                "occasion_id": None,
                "workflow_complete": False
            },
            "history": [],
            "metadata": {}
        }
    with open(EXECUTION_STATE, 'r') as f:
        return json.load(f)


def save_execution_state(state):
    """Save execution_state.json atomically with file locking"""
    state['metadata']['last_updated'] = datetime.now().isoformat()

    PROCESS_DIR.mkdir(parents=True, exist_ok=True)

    with open(EXECUTION_STATE_LOCK, 'w') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            temp_file = PROCESS_DIR / 'execution_state.tmp'
            with open(temp_file, 'w') as f:
                json.dump(state, f, indent=2)
            temp_file.rename(EXECUTION_STATE)
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def load_occasion_context():
    """Load occasion_context.json"""
    if not OCCASION_CONTEXT.exists():
        return None
    with open(OCCASION_CONTEXT, 'r') as f:
        return json.load(f)


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_context_file(filename: str, min_count: int = 0) -> tuple:
    """
    Validate a context file exists and has required structure.

    Supports two structures:
    - accommodation.json: {hotels: [...], total_hotels, ...}
    - activities.json: {categories: [...], total_places, ...}

    Returns:
        (success: bool, actual_count: int, error_message: str | None)
    """
    context_file = CONTEXT_DIR / filename

    if not context_file.exists():
        return False, 0, f"Context file not found: files/context/{filename}"

    try:
        with open(context_file, 'r') as f:
            data = json.load(f)

        # Handle accommodation.json structure: {hotels: [...]}
        if filename == "accommodation.json":
            if not isinstance(data, dict):
                return False, 0, f"accommodation.json must be an object with 'hotels' array"

            hotels = data.get("hotels", [])
            if not isinstance(hotels, list):
                return False, 0, f"accommodation.json must have 'hotels' array"

            actual_count = len(hotels)

            if actual_count < min_count:
                return False, actual_count, f"accommodation.json has {actual_count} hotels, expected at least {min_count}"

            # Validate each hotel has required fields
            required_fields = ["id", "name", "rating"]
            for i, item in enumerate(hotels[:5]):
                missing = [f for f in required_fields if f not in item]
                if missing:
                    return False, actual_count, f"Hotel {i} missing required fields: {missing}"

                # Check for review_summary
                if "review_summary" not in item:
                    return False, actual_count, f"Hotel {i} ({item.get('name', 'unknown')}) missing review_summary"

            return True, actual_count, None

        # Handle activities.json structure: {categories: [...]}
        elif filename == "activities.json":
            if not isinstance(data, dict):
                return False, 0, f"activities.json must be an object with 'categories' array"

            categories = data.get("categories", [])
            if not isinstance(categories, list):
                return False, 0, f"activities.json must have 'categories' array"

            # Count total places across all categories
            actual_count = 0
            for cat in categories:
                places = cat.get("places", [])
                actual_count += len(places)

                # Validate category structure
                if "name" not in cat:
                    return False, actual_count, f"Category missing 'name' field"
                if "relevance" not in cat:
                    return False, actual_count, f"Category '{cat.get('name')}' missing 'relevance' field"

                # Validate places have required fields
                for i, place in enumerate(places[:3]):
                    if "id" not in place or "name" not in place:
                        return False, actual_count, f"Place {i} in '{cat.get('name')}' missing id or name"
                    if "review_summary" not in place:
                        return False, actual_count, f"Place '{place.get('name')}' missing review_summary"

            if actual_count < min_count:
                return False, actual_count, f"activities.json has {actual_count} places, expected at least {min_count}"

            # Check for research_insights
            if "research_insights" not in data:
                return False, actual_count, f"activities.json missing 'research_insights' section"

            return True, actual_count, None

        # Fallback for other files (legacy flat array format)
        else:
            if not isinstance(data, list):
                return False, 0, f"Context file must contain a JSON array: files/context/{filename}"

            actual_count = len(data)

            if actual_count < min_count:
                return False, actual_count, f"Context file has {actual_count} items, expected at least {min_count}"

            required_fields = ["id", "source", "name"]
            for i, item in enumerate(data[:5]):
                missing = [f for f in required_fields if f not in item]
                if missing:
                    return False, actual_count, f"Item {i} missing required fields: {missing}"

            return True, actual_count, None

    except json.JSONDecodeError as e:
        return False, 0, f"Invalid JSON in files/context/{filename}: {e}"
    except Exception as e:
        return False, 0, f"Error reading files/context/{filename}: {e}"


def validate_content_files(subdir: str) -> tuple:
    """
    Validate content directory has files.

    Returns:
        (success: bool, file_count: int, total_items: int)
    """
    content_subdir = CONTENT_DIR / subdir

    if not content_subdir.exists():
        return False, 0, 0

    json_files = list(content_subdir.glob("*.json"))
    total_items = 0

    for f in json_files:
        try:
            with open(f, 'r') as fp:
                data = json.load(fp)
                if isinstance(data, list):
                    total_items += len(data)
                elif isinstance(data, dict):
                    total_items += 1
        except:
            pass

    return len(json_files) > 0, len(json_files), total_items


def count_context_items(filename: str) -> int:
    """Count items in a context file."""
    context_file = CONTEXT_DIR / filename
    if not context_file.exists():
        return 0
    try:
        with open(context_file, 'r') as f:
            data = json.load(f)

        # Handle accommodation.json: {hotels: [...]}
        if filename == "accommodation.json" and isinstance(data, dict):
            return len(data.get("hotels", []))

        # Handle activities.json: {categories: [{places: [...]}]}
        if filename == "activities.json" and isinstance(data, dict):
            total = 0
            for cat in data.get("categories", []):
                total += len(cat.get("places", []))
            return total

        # Legacy flat array format
        return len(data) if isinstance(data, list) else 0
    except:
        return 0


# =============================================================================
# SUPABASE UPDATE
# =============================================================================

def update_supabase(occasion_id: str, accommodations: list, activities: list) -> tuple:
    """
    Update Supabase occasions table with masterlists.

    Returns:
        (success: bool, message: str)
    """
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


def update_supabase_column(occasion_id: str, column: str, data: dict) -> tuple:
    """
    Update a single column in Supabase occasions table.

    Args:
        occasion_id: The occasion UUID
        column: Column name ('accommodations' or 'activities')
        data: The data to store

    Returns:
        (success: bool, message: str)
    """
    try:
        from supabase import create_client

        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            return False, "SUPABASE_URL and SUPABASE_KEY environment variables required"

        client = create_client(supabase_url, supabase_key)

        response = client.table("occasions").update({
            column: data,
            "updated_at": datetime.now().isoformat()
        }).eq("id", occasion_id).execute()

        if response.data:
            return True, f"{column} updated successfully"
        else:
            return False, "No rows updated in Supabase"

    except ImportError:
        return False, "supabase-py package not installed"
    except Exception as e:
        return False, str(e)


# =============================================================================
# WORKFLOW HANDLERS
# =============================================================================

def handle_resume(state):
    """Resume an interrupted workflow by checking context files."""
    print("=" * 60)
    print("WORKFLOW ORCHESTRATOR - RESUME CHECK")
    print("=" * 60)

    # Load occasion context
    occasion_context = load_occasion_context()
    if not occasion_context:
        print("\n❌ VALIDATION ERROR: files/process/occasion_context.json not found")
        print("   Cannot resume - no occasion context. Run with fresh occasion_id.")
        sys.exit(1)

    occasion_id = occasion_context.get("id")
    occasion_name = occasion_context.get("occasion", "Unknown")
    city = occasion_context.get("city", "Unknown")
    country = occasion_context.get("country", "")
    location = f"{city}, {country}" if country else city

    print(f"\n🔄 Checking workflow state for: {occasion_name}")
    print(f"📍 Location: {location}")
    print(f"🔑 Occasion ID: {occasion_id}\n")

    # Check existing execution state
    workflow = state.get("workflow", {})
    existing_occasion_id = workflow.get("occasion_id")

    if workflow.get("workflow_complete"):
        print("✅ Workflow already completed!")
        print("   To re-run, use --agent init to start fresh.")
        return None

    # Check context files to determine resume point
    acc_context = CONTEXT_DIR / "accommodation.json"
    act_context = CONTEXT_DIR / "activities.json"

    acc_exists = acc_context.exists() and count_context_items("accommodation.json") > 0
    act_exists = act_context.exists() and count_context_items("activities.json") > 0

    print("📂 Context file status:")
    print(f"   - accommodation.json: {'✅ exists (' + str(count_context_items('accommodation.json')) + ' hotels)' if acc_exists else '❌ not found'}")
    print(f"   - activities.json: {'✅ exists (' + str(count_context_items('activities.json')) + ' places)' if act_exists else '❌ not found'}")

    if acc_exists and act_exists:
        # Both exist - just need to run final Supabase update
        print("\n✅ Both context files exist. Running final Supabase update...")

        # Load context files (now nested structures)
        with open(acc_context, 'r') as f:
            accommodations_data = json.load(f)
        with open(act_context, 'r') as f:
            activities_data = json.load(f)

        # Count items
        acc_count = len(accommodations_data.get("hotels", []))
        act_count = sum(len(cat.get("places", [])) for cat in activities_data.get("categories", []))

        success, message = update_supabase(occasion_id, accommodations_data, activities_data)

        # Update state
        state['workflow']['status'] = 'completed'
        state['workflow']['workflow_complete'] = True
        state['history'].append({
            'timestamp': datetime.now().isoformat(),
            'event': 'workflow_resumed_and_completed',
            'details': {
                'accommodations_count': acc_count,
                'activities_count': act_count,
                'supabase_updated': success,
                'supabase_message': message
            }
        })
        save_execution_state(state)

        return f"""🎉 Workflow complete! Inventory masterlist built for {occasion_name}.

Summary:
- Accommodations: {acc_count} hotels
- Activities: {act_count} places across {len(activities_data.get('categories', []))} categories
- Supabase update: {"✅ Success" if success else "❌ Failed - " + message}"""

    elif acc_exists and not act_exists:
        # Accommodation done, resume at activities
        print("\n🔄 Resuming at activities step...")

        # Update state to reflect resume
        state['workflow']['status'] = 'in_progress'
        state['workflow']['current_step'] = 1
        state['workflow']['next_agent'] = 'activities'
        state['history'].append({
            'timestamp': datetime.now().isoformat(),
            'event': 'workflow_resumed',
            'details': {'resume_point': 'activities'}
        })
        save_execution_state(state)

        description = occasion_context.get("description", "") if occasion_context else ""
        full_address = occasion_context.get("full_address", "") if occasion_context else ""
        start_date = occasion_context.get("start_date", "") if occasion_context else ""
        end_date = occasion_context.get("end_date", "") if occasion_context else ""

        return f"""Invoke activities subagent using Task tool with subagent_type='activities':

Occasion: {occasion_name}
Location: {location}
Venue: {full_address if full_address else 'N/A'}
Dates: {start_date} to {end_date}
Description: {description if description else 'N/A'}"""

    else:
        # No context files or only activities exists (unusual) - start from accommodation
        print("\n🔄 Resuming at accommodation step...")

        # Update state
        state['workflow']['status'] = 'in_progress'
        state['workflow']['current_step'] = 0
        state['workflow']['next_agent'] = 'accommodation'
        state['workflow']['occasion_id'] = occasion_id
        state['history'].append({
            'timestamp': datetime.now().isoformat(),
            'event': 'workflow_resumed',
            'details': {'resume_point': 'accommodation'}
        })
        save_execution_state(state)

        description = occasion_context.get("description", "") if occasion_context else ""
        full_address = occasion_context.get("full_address", "") if occasion_context else ""
        start_date = occasion_context.get("start_date", "") if occasion_context else ""
        end_date = occasion_context.get("end_date", "") if occasion_context else ""

        return f"""Invoke accommodation subagent using Task tool with subagent_type='accommodation':

Occasion: {occasion_name}
Location: {location}
Venue: {full_address if full_address else 'N/A'}
Dates: {start_date} to {end_date}
Description: {description if description else 'N/A'}"""


def handle_init(state):
    """Initialize workflow: cleanup and prepare for accommodation subagent (FRESH START)"""
    print("=" * 60)
    print("WORKFLOW ORCHESTRATOR - INITIALIZATION (FRESH START)")
    print("=" * 60)

    # Load occasion context
    occasion_context = load_occasion_context()
    if not occasion_context:
        print("\n❌ VALIDATION ERROR: files/process/occasion_context.json not found")
        print("   Hook workflow_init.py must run first to fetch occasion from Supabase")
        sys.exit(1)

    occasion_id = occasion_context.get("id")
    occasion_name = occasion_context.get("occasion", "Unknown")
    city = occasion_context.get("city", "Unknown")
    country = occasion_context.get("country", "")

    print(f"\n🎬 Workflow initialization for: {occasion_name}")
    print(f"📍 Location: {city}, {country}")
    print(f"🔑 Occasion ID: {occasion_id}\n")

    # Cleanup: Remove old files from previous runs
    print("🧹 Cleaning up old files (FRESH START)...")

    cleanup_files = [
        CONTEXT_DIR / "accommodation.json",
        CONTEXT_DIR / "activities.json",
        EXECUTION_STATE
    ]

    for file_path in cleanup_files:
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"   Deleted: {file_path.name}")
            except Exception as e:
                print(f"   Failed to delete {file_path}: {e}")

    # Cleanup content directories
    for subdir in ["accommodation", "activities"]:
        content_subdir = CONTENT_DIR / subdir
        if content_subdir.exists():
            for f in content_subdir.glob("*.json"):
                try:
                    f.unlink()
                    print(f"   Deleted: {subdir}/{f.name}")
                except Exception as e:
                    print(f"   Failed to delete {f}: {e}")

    # Ensure directories exist
    CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    (CONTENT_DIR / "accommodation").mkdir(parents=True, exist_ok=True)
    (CONTENT_DIR / "activities").mkdir(parents=True, exist_ok=True)

    print("✅ Cleanup complete\n")

    # Initialize execution state
    state['schema_version'] = '1.0'
    state['workflow'] = {
        'status': 'in_progress',
        'current_step': 0,
        'next_agent': 'accommodation',
        'started_at': datetime.now().isoformat(),
        'occasion_id': occasion_id,
        'workflow_complete': False
    }

    # Initialize history
    state['history'] = [{
        'timestamp': datetime.now().isoformat(),
        'event': 'workflow_initialized',
        'details': {
            'occasion_id': occasion_id,
            'occasion': occasion_name,
            'city': city,
            'country': country
        }
    }]

    state['metadata'] = {}
    save_execution_state(state)

    # Build prompt for accommodation subagent - just pass occasion context
    location = f"{city}, {country}" if country else city
    description = occasion_context.get("description", "") if occasion_context else ""
    full_address = occasion_context.get("full_address", "") if occasion_context else ""
    start_date = occasion_context.get("start_date", "") if occasion_context else ""
    end_date = occasion_context.get("end_date", "") if occasion_context else ""

    instruction = f"""Invoke accommodation subagent using Task tool with subagent_type='accommodation':

Occasion: {occasion_name}
Location: {location}
Venue: {full_address if full_address else 'N/A'}
Dates: {start_date} to {end_date}
Description: {description if description else 'N/A'}"""

    return instruction


def handle_accommodation(state, claimed_count):
    """After accommodation subagent: validate outputs and proceed to activities"""
    print("=" * 60)
    print("WORKFLOW ORCHESTRATOR - POST-ACCOMMODATION")
    print("=" * 60)

    print(f"\n🏨 Accommodation subagent completed")
    print(f"📊 Agent claims: {claimed_count} hotels\n")

    # VALIDATION 1: Context file exists with proper structure
    success, actual_count, error = validate_context_file("accommodation.json", min_count=1)

    if not success:
        print(f"❌ VALIDATION ERROR: {error}")
        print(f"   Accommodation subagent must write curated list to files/context/accommodation.json")
        print(f"\n⚠️  RETRY: Re-run accommodation subagent with warning about missing context file")
        sys.exit(1)

    print(f"✅ files/context/accommodation.json exists")
    print(f"✅ Structure validated (hotels array with id, name, rating, review_summary)")

    # VALIDATION 2: Cross-check agent claims vs reality
    if actual_count != claimed_count:
        print(f"\n⚠️  VALIDATION WARNING: Agent reported {claimed_count} hotels, but context file has {actual_count}")
        print(f"   Proceeding with actual count: {actual_count}")
    else:
        print(f"✅ Count validated: {actual_count} hotels")

    # VALIDATION 3: Content files exist (raw API outputs) - optional for liteapi workflow
    has_content, file_count, total_raw = validate_content_files("accommodation")
    if has_content:
        print(f"✅ Raw content: {file_count} files, {total_raw} total items in files/content/accommodation/")
    else:
        print(f"ℹ️  Note: No raw content files in files/content/accommodation/ (liteapi workflow uses direct output)")

    # INCREMENTAL SUPABASE UPDATE: Save accommodation immediately
    print("\n📤 Updating Supabase with accommodation data...")
    occasion_id = state['workflow'].get('occasion_id')
    with open(CONTEXT_DIR / "accommodation.json", 'r') as f:
        accommodations_data = json.load(f)

    acc_success, acc_message = update_supabase_column(occasion_id, "accommodations", accommodations_data)
    if acc_success:
        print(f"✅ Supabase accommodations column updated ({actual_count} hotels)")
    else:
        print(f"⚠️  Supabase update failed: {acc_message} (will retry at end)")

    # Append to history (audit trail)
    state['history'].append({
        'timestamp': datetime.now().isoformat(),
        'event': 'completed',
        'agent': 'accommodation',
        'details': {
            'claimed_count': claimed_count,
            'actual_count': actual_count,
            'raw_file_count': file_count,
            'raw_item_count': total_raw,
            'supabase_updated': acc_success
        }
    })

    # Update workflow state
    state['workflow']['current_step'] = 1
    state['workflow']['next_agent'] = 'activities'

    save_execution_state(state)

    # Build prompt for activities subagent - just pass occasion context
    occasion_context = load_occasion_context()
    occasion_name = occasion_context.get("occasion", "the occasion") if occasion_context else "the occasion"
    city = occasion_context.get("city", "the city") if occasion_context else "the city"
    country = occasion_context.get("country", "") if occasion_context else ""
    description = occasion_context.get("description", "") if occasion_context else ""
    full_address = occasion_context.get("full_address", "") if occasion_context else ""
    start_date = occasion_context.get("start_date", "") if occasion_context else ""
    end_date = occasion_context.get("end_date", "") if occasion_context else ""

    location = f"{city}, {country}" if country else city

    instruction = f"""Invoke activities subagent using Task tool with subagent_type='activities':

Occasion: {occasion_name}
Location: {location}
Venue: {full_address if full_address else 'N/A'}
Dates: {start_date} to {end_date}
Description: {description if description else 'N/A'}"""

    return instruction


def handle_activities(state, claimed_count):
    """After activities subagent: validate, compile results, update Supabase"""
    print("=" * 60)
    print("WORKFLOW ORCHESTRATOR - POST-ACTIVITIES (FINAL)")
    print("=" * 60)

    print(f"\n🎯 Activities subagent completed")
    print(f"📊 Agent claims: {claimed_count} places\n")

    # VALIDATION 1: Context file exists with proper structure
    success, actual_count, error = validate_context_file("activities.json", min_count=1)

    if not success:
        print(f"❌ VALIDATION ERROR: {error}")
        print(f"   Activities subagent must write curated list to files/context/activities.json")
        print(f"\n⚠️  RETRY: Re-run activities subagent with warning about missing context file")
        sys.exit(1)

    print(f"✅ files/context/activities.json exists")
    print(f"✅ Structure validated (categories with places, research_insights, review_summary per place)")

    # VALIDATION 2: Cross-check agent claims vs reality
    if actual_count != claimed_count:
        print(f"\n⚠️  VALIDATION WARNING: Agent reported {claimed_count} places, but context file has {actual_count}")
        print(f"   Proceeding with actual count: {actual_count}")
    else:
        print(f"✅ Count validated: {actual_count} places")

    # VALIDATION 3: Content files exist (optional for google-maps workflow)
    has_content, file_count, total_raw = validate_content_files("activities")
    if has_content:
        print(f"✅ Raw content: {file_count} files, {total_raw} total items in files/content/activities/")
    else:
        print(f"ℹ️  Note: No raw content files in files/content/activities/ (direct output workflow)")

    # VALIDATION 4: Accommodation context still exists (from previous step)
    acc_count = count_context_items("accommodation.json")
    if acc_count == 0:
        print(f"\n❌ VALIDATION ERROR: files/context/accommodation.json missing or empty")
        print(f"   Previous step output was lost. Cannot proceed with Supabase update")
        sys.exit(1)
    print(f"✅ Accommodation context preserved: {acc_count} hotels")

    # Append to history
    state['history'].append({
        'timestamp': datetime.now().isoformat(),
        'event': 'completed',
        'agent': 'activities',
        'details': {
            'claimed_count': claimed_count,
            'actual_count': actual_count,
            'raw_file_count': file_count,
            'raw_item_count': total_raw
        }
    })

    # Load context files for Supabase update (nested structures)
    print("\n📦 Compiling results for Supabase update...")

    with open(CONTEXT_DIR / "accommodation.json", 'r') as f:
        accommodations_data = json.load(f)

    with open(CONTEXT_DIR / "activities.json", 'r') as f:
        activities_data = json.load(f)

    # Count items
    hotel_count = len(accommodations_data.get("hotels", []))
    category_count = len(activities_data.get("categories", []))
    place_count = sum(len(cat.get("places", [])) for cat in activities_data.get("categories", []))

    print(f"   Accommodations: {hotel_count} hotels")
    print(f"   Activities: {place_count} places across {category_count} categories")

    # Update Supabase
    occasion_id = state['workflow'].get('occasion_id')
    success, message = update_supabase(occasion_id, accommodations_data, activities_data)

    if success:
        print(f"✅ Supabase update successful")
    else:
        print(f"❌ Supabase update failed: {message}")

    # Mark workflow complete
    state['workflow']['status'] = 'completed'
    state['workflow']['workflow_complete'] = True
    state['workflow']['next_agent'] = None

    state['history'].append({
        'timestamp': datetime.now().isoformat(),
        'event': 'workflow_completed',
        'details': {
            'accommodations_count': hotel_count,
            'activities_count': place_count,
            'activities_categories': category_count,
            'supabase_updated': success,
            'supabase_message': message
        }
    })

    save_execution_state(state)

    # Build completion message
    occasion_context = load_occasion_context()
    occasion_name = occasion_context.get("occasion", "occasion") if occasion_context else "occasion"

    instruction = f"""🎉 Workflow complete! Inventory masterlist built for {occasion_name}.

Summary:
- Accommodations: {hotel_count} hotels with review summaries
- Activities: {place_count} places across {category_count} categories with review summaries
- Supabase update: {"✅ Success" if success else "❌ Failed - " + message}

Context files ready at:
- files/context/accommodation.json
- files/context/activities.json"""

    return instruction


def handle_status(state):
    """Return current workflow status."""
    print("=" * 60)
    print("WORKFLOW STATUS")
    print("=" * 60)

    workflow = state.get('workflow', {})

    print(f"\nStatus: {workflow.get('status', 'unknown')}")
    print(f"Current step: {workflow.get('current_step', 'N/A')}")
    print(f"Next agent: {workflow.get('next_agent', 'N/A')}")
    print(f"Occasion ID: {workflow.get('occasion_id', 'N/A')}")
    print(f"Started: {workflow.get('started_at', 'N/A')}")
    print(f"Complete: {workflow.get('workflow_complete', False)}")

    # Show history
    history = state.get('history', [])
    if history:
        print(f"\nHistory ({len(history)} events):")
        for event in history[-5:]:  # Last 5 events
            print(f"  - {event.get('event')} @ {event.get('timestamp', 'unknown')[:19]}")

    # Show context file status
    print("\nContext files:")
    acc_count = count_context_items("accommodation.json")
    act_count = count_context_items("activities.json")
    print(f"  - accommodation.json: {'✅ ' + str(acc_count) + ' hotels' if acc_count > 0 else '❌ not found'}")
    print(f"  - activities.json: {'✅ ' + str(act_count) + ' places' if act_count > 0 else '❌ not found'}")

    return None


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Workflow Orchestrator - Inventory Agent')
    parser.add_argument('--agent', required=True,
                       choices=['init', 'resume', 'accommodation', 'activities', 'status'],
                       help='Which agent just completed (or init/resume/status)')
    parser.add_argument('--accommodation-count', type=int,
                       help='Accommodation count (accommodation agent only)')
    parser.add_argument('--activities-count', type=int,
                       help='Activities count (activities agent only)')

    args = parser.parse_args()

    # Validate required parameters
    if args.agent == 'accommodation' and args.accommodation_count is None:
        print("❌ ERROR: --accommodation-count required for accommodation agent")
        sys.exit(1)

    if args.agent == 'activities' and args.activities_count is None:
        print("❌ ERROR: --activities-count required for activities agent")
        sys.exit(1)

    # Load state
    state = load_execution_state()

    # Route to handler
    result = None

    if args.agent == 'init':
        result = handle_init(state)
    elif args.agent == 'resume':
        result = handle_resume(state)
    elif args.agent == 'accommodation':
        result = handle_accommodation(state, args.accommodation_count)
    elif args.agent == 'activities':
        result = handle_activities(state, args.activities_count)
    elif args.agent == 'status':
        result = handle_status(state)

    if result:
        print("\n" + "=" * 60)
        print("NEXT ACTION:")
        print("=" * 60)
        print(result)


if __name__ == '__main__':
    main()
