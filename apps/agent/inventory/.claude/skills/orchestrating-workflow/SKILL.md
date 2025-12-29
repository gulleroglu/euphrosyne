---
name: orchestrating-workflow
description: Workflow orchestrator and dispatcher between inventory subagents. Validates outputs, cross-checks agent claims, updates execution state, and routes to the next phase. Use when accommodation or activities subagent completes to report what happened and relay/enforce what to do next.
---

# Orchestrating Workflow - Inventory Agent

You act as a **workflow orchestrator** between subagents for building curated masterlists. When invoked:

1. **Read the instructions** passed to the skill from the previous subagent (accommodation or activities)
2. **Parse the message** to extract parameters:
   - Which subagent completed
   - What data they produced (count of items)
3. **Use Bash tool** to call the orchestration script:
   - **`scripts/orchestrate.py`** - Validates outputs, updates execution_state.json (audit trail), checks context files
4. **Interpret script output** and return next action:
   - **If validation passes**: Proceed to next subagent or complete workflow
   - **If validation fails**: Retry the same subagent with warning about what went wrong
5. **CRITICAL** Relay and enforce what to do next

Check [Workflow Selection](#workflow-selection) for more details per specific handover from a subagent.

## Workflow Selection

The skill is called after either `init`, `accommodation`, or `activities` phase is completed.

Choose the correct input example below to follow the correct workflow checklist.

### Input Examples For Workflow Selection

#### Workflow 1: Initialization (Fresh Start)
```
Workflow initialized. Starting inventory sequence for [occasion].
```

**Action:**
1. Call `python3 scripts/orchestrate.py --agent init`
2. Script validates occasion_context.json exists
3. Script cleans up old files and initializes execution_state.json
4. Invoke **accommodation** subagent with prompt from script output

#### Workflow 1b: Resume (Continue Interrupted Workflow)
```
Resuming workflow. Accommodation complete, proceeding to activities.
```
or
```
Resuming workflow at accommodation step.
```

**Action:**
1. Call `python3 scripts/orchestrate.py --agent resume`
2. Script checks context files to determine where to resume:
   - If `accommodation.json` exists but `activities.json` doesn't → resume at activities
   - If neither exists → resume at accommodation
   - If both exist → complete workflow with Supabase update
3. Follow script output for which subagent to invoke next

#### Workflow 2: After Accommodation Subagent
```
Accommodation research complete. Found 10 hotels matching criteria.
```

**Action:**
1. Parse count from message (e.g., "10")
2. Call `python3 scripts/orchestrate.py --agent accommodation --accommodation-count 10`
3. Script validates context file and returns next action
4. Invoke **activities** subagent with occasion context from script output

#### Workflow 3: After Activities Subagent (FINAL)
```
Activities research complete. Found 45 places across 5 categories.
```

**Action:**
1. Parse count from message (e.g., "45")
2. Call `python3 scripts/orchestrate.py --agent activities --activities-count 45`
3. Script validates context files and updates Supabase
4. Workflow complete!

---

## Context File Structures

### accommodation.json

```json
{
  "occasion_description": "Anniversary celebration in Champagne region",
  "search_location": {
    "type": "coordinates",
    "latitude": 49.0422,
    "longitude": 3.9530,
    "city": "Epernay",
    "country": "FR",
    "radius_km": 25
  },
  "search_criteria": {
    "min_rating": 8.0,
    "min_reviews": 100
  },
  "hotels": [
    {
      "id": "lp55143",
      "name": "Hotel Hermitage",
      "stars": 5,
      "rating": 9.2,
      "rating_count": 1847,
      "address": "Square Beaumarchais",
      "city": "Epernay",
      "country": "FR",
      "latitude": 49.0422,
      "longitude": 3.9530,
      "main_photo": "https://...",
      "review_summary": {
        "overall_score": 9.2,
        "total_reviews": 1847,
        "highlights": [...],
        "what_guests_love": [...],
        "what_to_know": [...],
        "guest_types": "..."
      }
    }
  ],
  "total_hotels": 10,
  "generated_at": "2025-12-28T20:30:00Z"
}
```

### activities.json

```json
{
  "occasion": {
    "name": "Anniversary of Avenue de Champagne",
    "description": "...",
    "dates": "December 15-18, 2026",
    "season": "winter"
  },
  "location": {
    "primary": "Avenue de Champagne, Epernay",
    "city": "Epernay",
    "country": "FR",
    "region": "Champagne"
  },
  "research_insights": {
    "region_identity": "Heart of Champagne production...",
    "unique_experiences": ["Cellar tours", "Tastings"],
    "seasonal_considerations": "December is off-season...",
    "excluded_activities": ["Cycling tours"],
    "exclusion_reasoning": "Cold weather..."
  },
  "categories": [
    {
      "name": "Champagne Houses & Tastings",
      "relevance": "Core to region's identity",
      "search_queries": ["champagne house", "champagne tasting"],
      "places": [
        {
          "id": "ChIJ...",
          "name": "Moët & Chandon",
          "rating": 4.6,
          "rating_count": 5420,
          "address": "20 Avenue de Champagne",
          "latitude": 49.0422,
          "longitude": 3.9530,
          "why_included": "Most famous champagne house",
          "review_summary": {
            "what_guests_love": [...],
            "negatives": [...],
            "practical_tips": [...],
            "best_for": "...",
            "skip_if": "..."
          }
        }
      ]
    }
  ],
  "total_places": 45,
  "generated_at": "2025-12-28T21:00:00Z"
}
```

---

## Validation Requirements

### Accommodation Validation

1. **File exists**: `files/context/accommodation.json` must exist
2. **Structure**: Must be object with `hotels` array
3. **Required fields per hotel**: `id`, `name`, `rating`
4. **Review summary**: Each hotel must have `review_summary`

### Activities Validation

1. **File exists**: `files/context/activities.json` must exist
2. **Structure**: Must be object with `categories` array
3. **Research insights**: Must have `research_insights` section
4. **Required fields per category**: `name`, `relevance`, `places`
5. **Required fields per place**: `id`, `name`
6. **Review summary**: Each place must have `review_summary`

---

## Subagent Sequence

```
                        ┌──────────────────┐
                        │  init OR resume  │
                        └────────┬─────────┘
                                 │
                                 ▼
1. accommodation subagent  →  (follows its own instructions)
       │
       ▼
   [orchestrator validates context/accommodation.json]
       │
       ▼
2. activities subagent     →  (follows its own instructions)
       │
       ▼
   [orchestrator validates context/activities.json]
       │
       ▼
   [Supabase UPDATE occasions SET accommodations=..., activities=...]
       │
       ▼
   COMPLETE
```

**Resume Logic:**
- If `accommodation.json` exists but `activities.json` doesn't → skip to activities
- If neither exists → start at accommodation
- If both exist → just run Supabase update and complete

**Separation of Concerns:**
- Orchestrator: validates outputs, routes to next step, passes occasion context
- Subagents: follow their own instructions in `.claude/agents/*.md`

---

## Orchestration Script Usage

```bash
# Initialize workflow (FRESH START - cleans old files)
python3 scripts/orchestrate.py --agent init

# Resume interrupted workflow (checks context files to determine resume point)
python3 scripts/orchestrate.py --agent resume

# After accommodation subagent
python3 scripts/orchestrate.py --agent accommodation --accommodation-count 10

# After activities subagent (triggers Supabase update)
python3 scripts/orchestrate.py --agent activities --activities-count 45

# Check status
python3 scripts/orchestrate.py --agent status
```

The script will:
1. Validate context files exist with proper structure
2. Validate each item has `review_summary`
3. Cross-check agent claims vs actual file contents
4. Update execution_state.json with history (audit trail)
5. On final step: Update Supabase occasions table
6. Return next action instructions

---

## Error Handling

When validation fails, the script exits with error code 1 and prints diagnostic information.

**You should:**
1. Read the error message
2. Determine what went wrong
3. Retry the subagent with a warning about the issue

Example validation failure:
```
❌ VALIDATION ERROR: Hotel 0 (Hotel Example) missing review_summary
   Accommodation subagent must write curated list to files/context/accommodation.json

⚠️  RETRY: Re-run accommodation subagent with warning about missing review_summary
```

**Response:**
```
Re-invoke accommodation subagent with warning:

⚠️ Previous attempt failed validation. Each hotel MUST have review_summary with analyzed reviews.

Find suitable accommodations...
[rest of prompt]
```
