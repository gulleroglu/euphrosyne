#!/usr/bin/env python3
"""
UserPromptSubmit hook: Parse trip request and initialize workflow

Input: User's travel request (natural language)
Output: Instruction to invoke orchestrating-workflow skill

This hook:
1. Parses the trip request to extract parameters
2. Creates trip_context.json with structured data
3. Initializes workflow_state.json
4. Returns message to invoke orchestrating-workflow skill
"""
import json
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
import dateparser

# Paths
project_root = Path.cwd()
process_dir = project_root / "files" / "process"
workflow_state_file = process_dir / "workflow_state.json"
trip_context_file = process_dir / "trip_context.json"


def parse_travelers(prompt: str) -> dict:
    """Extract traveler counts from prompt."""
    travelers = {"adults": 2, "children": 0, "infants": 0}

    # Match patterns like "2 adults", "for 4 people", "4 travelers"
    adult_patterns = [
        r'(\d+)\s*adult',
        r'for\s*(\d+)\s*(?:people|person|travelers?)',
        r'(\d+)\s*(?:people|person|travelers?)',
    ]

    for pattern in adult_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            travelers["adults"] = int(match.group(1))
            break

    # Match children
    child_match = re.search(r'(\d+)\s*(?:child|children|kids?)', prompt, re.IGNORECASE)
    if child_match:
        travelers["children"] = int(child_match.group(1))

    return travelers


def parse_budget(prompt: str) -> dict:
    """Extract budget from prompt."""
    budget = {"total": None, "currency": "USD"}

    # Match patterns like "$5000", "5000 USD", "budget of 5000"
    patterns = [
        r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|dollars?)',
        r'budget\s*(?:of\s*)?\$?\s*(\d+(?:,\d{3})*)',
    ]

    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            budget["total"] = int(match.group(1).replace(",", "").split(".")[0])
            break

    # Check for EUR
    if re.search(r'EUR|euros?', prompt, re.IGNORECASE):
        budget["currency"] = "EUR"

    return budget


def parse_dates(prompt: str) -> dict:
    """Extract travel dates from prompt."""
    dates = {
        "departure": None,
        "return": None,
        "duration_nights": None,
        "flexible": False
    }

    # Try to find date ranges like "March 15-20" or "March 15 to March 20"
    range_pattern = r'(\w+\s+\d{1,2})(?:\s*[-–]\s*|\s+to\s+)(\d{1,2}|\w+\s+\d{1,2})'
    range_match = re.search(range_pattern, prompt, re.IGNORECASE)

    if range_match:
        start_str = range_match.group(1)
        end_str = range_match.group(2)

        # Parse start date
        start_date = dateparser.parse(start_str, settings={'PREFER_DATES_FROM': 'future'})

        # If end is just a number, it's the same month
        if end_str.isdigit():
            end_str = f"{start_str.split()[0]} {end_str}"

        end_date = dateparser.parse(end_str, settings={'PREFER_DATES_FROM': 'future'})

        if start_date and end_date:
            dates["departure"] = start_date.strftime("%Y-%m-%d")
            dates["return"] = end_date.strftime("%Y-%m-%d")
            dates["duration_nights"] = (end_date - start_date).days

    # Try to find duration like "5 days", "1 week"
    duration_match = re.search(r'(\d+)\s*(?:day|night)s?', prompt, re.IGNORECASE)
    if duration_match and not dates["duration_nights"]:
        dates["duration_nights"] = int(duration_match.group(1))

    week_match = re.search(r'(\d+)\s*weeks?', prompt, re.IGNORECASE)
    if week_match and not dates["duration_nights"]:
        dates["duration_nights"] = int(week_match.group(1)) * 7

    # Check for flexibility
    if re.search(r'flexible|around|approximately', prompt, re.IGNORECASE):
        dates["flexible"] = True

    return dates


def parse_locations(prompt: str) -> tuple:
    """Extract origin and destination from prompt."""
    origin = None
    destination = None

    # Common patterns for origin
    origin_patterns = [
        r'from\s+([A-Z][a-zA-Z\s,]+?)(?:\s+to\s+|\s+departing|\s+leaving)',
        r'departing\s+(?:from\s+)?([A-Z][a-zA-Z\s,]+?)(?:\s+to\s+|\s+on)',
        r'leaving\s+(?:from\s+)?([A-Z][a-zA-Z\s,]+?)(?:\s+to\s+|\s+on)',
    ]

    for pattern in origin_patterns:
        match = re.search(pattern, prompt)
        if match:
            origin = match.group(1).strip().rstrip(',')
            break

    # Fallback: look for common city abbreviations
    if not origin:
        city_abbrevs = {
            'NYC': 'New York, NY',
            'LA': 'Los Angeles, CA',
            'SF': 'San Francisco, CA',
            'CHI': 'Chicago, IL',
            'BOS': 'Boston, MA',
            'SEA': 'Seattle, WA',
            'DEN': 'Denver, CO',
            'MIA': 'Miami, FL',
        }
        for abbrev, city in city_abbrevs.items():
            if re.search(rf'\b{abbrev}\b', prompt):
                origin = city
                break

    # Common patterns for destination
    dest_patterns = [
        r'to\s+([A-Z][a-zA-Z\s,]+?)(?:\s+for\s+|\s+from\s+|\s+departing|\s*[,.]|$)',
        r'trip\s+to\s+([A-Z][a-zA-Z\s,]+?)(?:\s+for\s+|\s*[,.]|$)',
        r'visit(?:ing)?\s+([A-Z][a-zA-Z\s,]+?)(?:\s+for\s+|\s*[,.]|$)',
        r'travel(?:ing)?\s+to\s+([A-Z][a-zA-Z\s,]+?)(?:\s+for\s+|\s*[,.]|$)',
    ]

    for pattern in dest_patterns:
        match = re.search(pattern, prompt)
        if match:
            destination = match.group(1).strip().rstrip(',')
            break

    return origin, destination


def parse_preferences(prompt: str) -> dict:
    """Extract travel preferences from prompt."""
    preferences = {
        "flight_class": "economy",
        "hotel_stars": None,
        "interests": [],
        "dietary": None,
        "accessibility": None
    }

    # Flight class
    if re.search(r'business\s*class', prompt, re.IGNORECASE):
        preferences["flight_class"] = "business"
    elif re.search(r'first\s*class', prompt, re.IGNORECASE):
        preferences["flight_class"] = "first"
    elif re.search(r'premium\s*economy', prompt, re.IGNORECASE):
        preferences["flight_class"] = "premium_economy"

    # Hotel stars
    star_match = re.search(r'(\d)\s*star', prompt, re.IGNORECASE)
    if star_match:
        preferences["hotel_stars"] = int(star_match.group(1))

    # Interests
    interest_keywords = [
        'museum', 'art', 'history', 'food', 'cuisine', 'beach', 'hiking',
        'shopping', 'nightlife', 'nature', 'adventure', 'culture', 'architecture',
        'wine', 'spa', 'relaxation', 'photography', 'music', 'sports'
    ]

    for keyword in interest_keywords:
        if re.search(rf'\b{keyword}s?\b', prompt, re.IGNORECASE):
            preferences["interests"].append(keyword)

    return preferences


def parse_trip_request(prompt: str) -> dict:
    """
    Parse natural language trip request into structured data.
    """
    origin, destination = parse_locations(prompt)
    dates = parse_dates(prompt)
    travelers = parse_travelers(prompt)
    budget = parse_budget(prompt)
    preferences = parse_preferences(prompt)

    context = {
        "parsed_at": datetime.now().isoformat(),
        "raw_prompt": prompt,
        "origin": origin,
        "destination": destination,
        "dates": dates,
        "travelers": travelers,
        "budget": budget,
        "preferences": preferences
    }

    return context


def initialize_workflow_state() -> dict:
    """Create initial workflow state."""
    return {
        "current_step": 0,
        "steps": ["transportation", "accommodation", "activities", "verification", "booking"],
        "completed_steps": [],
        "skip_booking": False,
        "status": "initialized",
        "started_at": datetime.now().isoformat()
    }


def analyze_existing_workflow():
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
    print("Error: No trip request provided. Please describe your trip.")
    sys.exit(1)

# Check for existing workflow
status_type, existing_state = analyze_existing_workflow()

if status_type == "complete":
    print("Previous workflow completed. Starting fresh with new trip request.")
elif status_type == "resume":
    current_step = existing_state.get("current_step", 0)
    steps = existing_state.get("steps", [])
    if current_step < len(steps):
        current_agent = steps[current_step]
        print(f"Resuming workflow at step {current_step + 1}: {current_agent}")
        print(f"Use Skill tool to invoke 'orchestrating-workflow' skill to continue.")
        sys.exit(0)

# Parse trip request
trip_context = parse_trip_request(prompt)

# Create process directory if needed
process_dir.mkdir(parents=True, exist_ok=True)

# Save trip context
with open(trip_context_file, 'w') as f:
    json.dump(trip_context, f, indent=2)

# Initialize workflow state
workflow_state = initialize_workflow_state()
with open(workflow_state_file, 'w') as f:
    json.dump(workflow_state, f, indent=2)

# Build initialization message
init_message = f"""Workflow initialized for trip request.

Trip Context:
- Origin: {trip_context.get('origin', 'Not specified')}
- Destination: {trip_context.get('destination', 'Not specified')}
- Dates: {trip_context.get('dates', {}).get('departure', 'TBD')} to {trip_context.get('dates', {}).get('return', 'TBD')}
- Travelers: {trip_context.get('travelers', {}).get('adults', 2)} adults
- Budget: {trip_context.get('budget', {}).get('total', 'Not specified')} {trip_context.get('budget', {}).get('currency', 'USD')}

Use Skill tool to invoke 'orchestrating-workflow' skill with message:
'Workflow initialized. Starting travel planning sequence.'"""

print(init_message)
sys.exit(0)
