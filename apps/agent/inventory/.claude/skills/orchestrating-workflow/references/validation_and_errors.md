# Validation and Error Handling

## Validation Checks

The orchestrate.py script performs these validations after each subagent completes:

### 1. Context File Exists

```python
if not context_file.exists():
    return False, 0, f"Context file not found: files/context/{filename}"
```

**Error:**
```
❌ VALIDATION ERROR: Context file not found: files/context/accommodations.json
   Accommodation subagent must write curated list to files/context/accommodations.json
```

**Fix:** Re-run subagent with explicit instruction to write to `files/context/`.

### 2. Valid JSON Array

```python
if not isinstance(data, list):
    return False, 0, f"Context file must contain a JSON array"
```

**Error:**
```
❌ VALIDATION ERROR: Context file must contain a JSON array: files/context/accommodations.json
```

**Fix:** Context file must be `[...]` not `{...}`.

### 3. Required Fields Present

Each item must have: `id`, `source`, `name`

```python
required_fields = ["id", "source", "name"]
for i, item in enumerate(data[:5]):
    missing = [f for f in required_fields if f not in item]
    if missing:
        return False, actual_count, f"Item {i} missing required fields: {missing}"
```

**Error:**
```
❌ VALIDATION ERROR: Item 0 missing required fields: ['source']
```

**Fix:** Ensure subagent includes all required fields in output.

### 4. Count Cross-Validation

Agent's claimed count is compared to actual file contents.

```
⚠️  VALIDATION WARNING: Agent reported 45 accommodations, but context file has 42
   Proceeding with actual count: 42
```

This is a warning, not an error. Workflow continues with actual count.

### 5. Previous Step Output Preserved

For activities step, checks that accommodations.json still exists.

```python
acc_count = count_context_items("accommodations.json")
if acc_count == 0:
    print("❌ VALIDATION ERROR: files/context/accommodations.json missing or empty")
    sys.exit(1)
```

**Error:**
```
❌ VALIDATION ERROR: files/context/accommodations.json missing or empty
   Previous step output was lost. Cannot proceed with Supabase update
```

**Fix:** Must re-run entire workflow from accommodation step.

---

## When Validation Fails

When the script detects validation errors, it exits with code 1. You should interpret the error and retry the subagent with a warning.

### Example: Missing Context File

**Subagent reports:**
```
Accommodation research complete. Found 45 accommodations.
```

**You call script:**
```bash
python3 scripts/orchestrate.py --agent accommodation --accommodation-count 45
```

**Script returns error:**
```
❌ VALIDATION ERROR: Context file not found: files/context/accommodations.json
   Accommodation subagent must write curated list to files/context/accommodations.json

⚠️  RETRY: Re-run accommodation subagent with warning about missing context file
```

**Response:**
```
Re-invoke accommodation subagent with warning:

⚠️ Previous attempt failed validation. The curated list was NOT written to files/context/accommodations.json.

You MUST:
1. Write raw results to files/content/accommodations/ (one file per source)
2. Write curated list to files/context/accommodations.json (deduplicated array)

Build exhaustive masterlist of accommodations...
[rest of prompt]
```

### Example: Invalid JSON Structure

**Script returns error:**
```
❌ VALIDATION ERROR: Context file must contain a JSON array: files/context/activities.json
```

**Response:**
```
Re-invoke activities subagent with warning:

⚠️ Previous attempt failed validation. The context file contains invalid structure.

files/context/activities.json must be a JSON ARRAY like:
[
  {"id": "...", "source": "...", "name": "..."},
  ...
]

NOT a JSON object like:
{"activities": [...]}

Build exhaustive masterlist of activities...
[rest of prompt]
```

---

## Error Prevention

### Required Output Structure

**For accommodations:**
```
files/content/accommodations/
├── duffel_hotels.json      # Raw Duffel API response
└── google_maps_lodging.json # Raw Google Maps response

files/context/
└── accommodations.json     # Curated, deduplicated array
```

**For activities:**
```
files/content/activities/
├── restaurants.json        # Raw Google Maps response
├── attractions.json        # Raw Google Maps response
├── museums.json            # Raw Google Maps response
└── ...                     # One file per category

files/context/
└── activities.json         # Curated, deduplicated array
```

### Context File Schema

Every item MUST have:

```json
{
  "id": "required - unique identifier from source",
  "source": "required - 'duffel' or 'google_maps'",
  "name": "required - human readable name",
  // ... other fields optional
}
```
