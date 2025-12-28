# Workflow After Accommodation Subagent

## Checklist

- [ ] **Step 1: Parse the message and extract:**
  - Agent: accommodation
  - Count: N (from "Found N accommodations")

- [ ] **Step 2: Call orchestrate.py using Bash tool:**
```bash
python3 scripts/orchestrate.py --agent accommodation --accommodation-count N
```

**orchestrate.py validates (internal):**
- files/context/accommodations.json exists
- File contains valid JSON array
- Each item has required fields: id, source, name
- Cross-checks claimed count vs actual count

**orchestrate.py updates execution_state.json (internal):**
- Appends to `history`: `{"event": "completed", "agent": "accommodation", "details": {...}}`
- Updates `workflow.current_step` to 1
- Updates `workflow.next_agent` to "activities"

- [ ] **Step 3: Check validation result:**

**If validation passes:**
```
✅ files/context/accommodations.json exists
✅ Structure validated (id, source, name fields present)
✅ Count validated: N accommodations
```

Proceed to Step 4.

**If validation fails:**
```
❌ VALIDATION ERROR: Context file not found: files/context/accommodations.json
```

Re-invoke accommodation subagent with warning:
```
⚠️ Previous attempt failed validation. You MUST write the curated list to files/context/accommodations.json.

Build exhaustive masterlist of accommodations for [occasion] in [location].
...
```

- [ ] **Step 4: Invoke activities subagent using Task tool:**

Use the prompt from orchestrate.py output to invoke the activities subagent.

```
Without stopping or waiting for user confirmation, invoke the 'activities' agent using the Task tool with the prompt provided by orchestrate.py.
```

## Expected Output Files After Accommodation

**Content (raw):**
- `files/content/accommodations/duffel_hotels.json` - Raw Duffel API results
- `files/content/accommodations/google_maps_lodging.json` - Raw Google Maps results

**Context (curated):**
- `files/context/accommodations.json` - Deduplicated, validated array

## Context File Format

```json
[
  {
    "id": "acco_abc123",
    "source": "duffel",
    "name": "Hotel Example",
    "stars": 4,
    "rating": 8.5,
    "address": "123 Main St",
    "latitude": 43.7384,
    "longitude": 7.4246,
    "amenities": ["wifi", "pool"]
  },
  {
    "id": "ChIJ...",
    "source": "google_maps",
    "name": "Another Hotel",
    ...
  }
]
```
