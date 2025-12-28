# Workflow After Activities Subagent (FINAL)

## Checklist

- [ ] **Step 1: Parse the message and extract:**
  - Agent: activities
  - Count: N (from "Found N activities")

- [ ] **Step 2: Call orchestrate.py using Bash tool:**
```bash
python3 scripts/orchestrate.py --agent activities --activities-count N
```

**orchestrate.py validates (internal):**
- files/context/activities.json exists
- File contains valid JSON array
- Each item has required fields: id, source, name
- Cross-checks claimed count vs actual count
- Verifies files/context/accommodations.json still exists (from previous step)

**orchestrate.py compiles results:**
- Loads files/context/accommodations.json
- Loads files/context/activities.json
- Updates Supabase occasions table

**orchestrate.py updates execution_state.json (internal):**
- Appends to `history`: `{"event": "completed", "agent": "activities", "details": {...}}`
- Appends to `history`: `{"event": "workflow_completed", "details": {...}}`
- Updates `workflow.status` to "completed"
- Updates `workflow.workflow_complete` to true

- [ ] **Step 3: Check validation result:**

**If validation passes:**
```
✅ files/context/activities.json exists
✅ Structure validated (id, source, name fields present)
✅ Count validated: N activities
✅ Accommodations context preserved: M items

📦 Compiling results for Supabase update...
   Accommodations: M items
   Activities: N items
✅ Supabase update successful
```

Workflow complete! Return success message.

**If validation fails:**
```
❌ VALIDATION ERROR: Context file not found: files/context/activities.json
```

Re-invoke activities subagent with warning:
```
⚠️ Previous attempt failed validation. You MUST write the curated list to files/context/activities.json.

Build exhaustive masterlist of activities for [occasion] in [location].
...
```

- [ ] **Step 4: Return completion message:**

```
🎉 Workflow complete! Inventory masterlist built for [occasion].

Summary:
- Accommodations: M items
- Activities: N items
- Supabase update: ✅ Success

Context files ready at:
- files/context/accommodations.json
- files/context/activities.json
```

## Expected Output Files After Activities

**Content (raw):**
- `files/content/activities/restaurants.json` - Raw Google Maps results
- `files/content/activities/attractions.json` - Raw Google Maps results
- `files/content/activities/museums.json` - Raw Google Maps results
- (one file per category searched)

**Context (curated):**
- `files/context/activities.json` - Deduplicated, validated array

## Context File Format

```json
[
  {
    "id": "ChIJ...",
    "source": "google_maps",
    "name": "Le Louis XV",
    "category": "restaurant",
    "rating": 4.8,
    "rating_count": 1234,
    "address": "Place du Casino",
    "latitude": 43.7394,
    "longitude": 7.4276,
    "price_level": 4,
    "types": ["restaurant", "food", "point_of_interest"]
  },
  ...
]
```

## Supabase Update

The orchestrate.py script updates the occasions table:

```sql
UPDATE occasions
SET
  accommodations = [...],
  activities = [...],
  updated_at = '2025-01-15T10:30:00Z'
WHERE id = 'occasion_uuid'
```

Both `accommodations` and `activities` columns are JSONB arrays.
