---
name: orchestrating-workflow
description: Workflow orchestrator and dispatcher between inventory subagents. Validates outputs, cross-checks agent claims, updates execution state, and routes to the next phase. Use when accommodation or activities subagent completes to report what happened and relay/enforce what to do next.
---

# Orchestrating Workflow - Inventory Agent

You act as a **workflow orchestrator** between subagents for building exhaustive masterlists. When invoked:

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

**MANDATORY - READ ENTIRE FILE: `references/validation_and_errors.md` completely from start to finish before any operation.**

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
   - If `accommodations.json` exists but `activities.json` doesn't → resume at activities
   - If neither exists → resume at accommodation
   - If both exist → complete workflow with Supabase update
3. Follow script output for which subagent to invoke next

#### Workflow 2: After Accommodation Subagent
```
Accommodation research complete. Found 45 accommodations.
```

**MANDATORY - READ ENTIRE FILE: `references/post-accommodation.md` completely from start to finish.**

**Action:**
1. Parse count from message (e.g., "45")
2. Call `python3 scripts/orchestrate.py --agent accommodation --accommodation-count 45`
3. Script validates:
   - files/context/accommodations.json exists
   - File contains array with id, source, name fields
   - Cross-checks claimed count vs actual count
4. Invoke **activities** subagent with prompt from script output

#### Workflow 3: After Activities Subagent (FINAL)
```
Activities research complete. Found 120 activities.
```

**MANDATORY - READ ENTIRE FILE: `references/post-activities.md` completely from start to finish.**

**Action:**
1. Parse count from message (e.g., "120")
2. Call `python3 scripts/orchestrate.py --agent activities --activities-count 120`
3. Script validates:
   - files/context/activities.json exists
   - files/context/accommodations.json still exists
   - Compiles results and updates Supabase
4. Workflow complete!

---

## Two-Folder Architecture

The system uses **two separate output directories** for different purposes:

**1. files/content/ (Raw API Outputs)**
- `accommodations/*.json` - Raw hotel data from Duffel and Google Maps
- `activities/*.json` - Raw place data from Google Maps (one file per category)
- Contains ALL results from API calls
- Used for debugging and full data access

**2. files/context/ (Curated Lists for Supabase)**
- `accommodations.json` - Deduplicated, validated array of accommodations
- `activities.json` - Deduplicated, validated array of activities
- **Source of truth** for Supabase update
- Must have required fields: `id`, `source`, `name`

**Why two folders?** Raw API data (content) vs curated masterlists (context) separated.

---

## Orchestration Script Usage

```bash
# Initialize workflow (FRESH START - cleans old files)
python3 scripts/orchestrate.py --agent init

# Resume interrupted workflow (checks context files to determine resume point)
python3 scripts/orchestrate.py --agent resume

# After accommodation subagent
python3 scripts/orchestrate.py --agent accommodation --accommodation-count 45

# After activities subagent (triggers Supabase update)
python3 scripts/orchestrate.py --agent activities --activities-count 120

# Check status
python3 scripts/orchestrate.py --agent status
```

The script will:
1. Validate context files exist with proper structure
2. Cross-check agent claims vs actual file contents
3. Update execution_state.json with history (audit trail)
4. On final step: Update Supabase occasions table
5. Return next action instructions

---

## Validation Requirements

### Context File Structure

Each item in context files must have:

```json
{
  "id": "place_abc123",
  "source": "google_maps",
  "name": "Hotel Example",
  ...
}
```

### Validation Checks

1. **File exists**: `files/context/{type}.json` must exist
2. **Valid JSON array**: File must contain `[...]` not `{...}`
3. **Required fields**: Each item must have `id`, `source`, `name`
4. **Count validation**: Claimed count should match actual count

---

## Subagent Sequence

```
                        ┌──────────────────┐
                        │  init OR resume  │
                        └────────┬─────────┘
                                 │
        ┌────────────────────────┴────────────────────────┐
        │ (resume checks context files to determine point)│
        └────────────────────────┬────────────────────────┘
                                 │
                                 ▼
1. accommodation  →  Search all hotels (Duffel + Google Maps)
       │
       ▼
   [validation: context/accommodations.json exists]
       │
       ▼
2. activities     →  Search all places (Google Maps)
       │
       ▼
   [validation: context/activities.json exists]
       │
       ▼
   [Supabase UPDATE occasions SET accommodations=..., activities=...]
       │
       ▼
   COMPLETE
```

**Resume Logic:**
- If `accommodations.json` exists but `activities.json` doesn't → skip to activities
- If neither exists → start at accommodation
- If both exist → just run Supabase update and complete

---

## Error Handling

When validation fails, the script exits with error code 1 and prints diagnostic information.

**You should:**
1. Read the error message
2. Determine what went wrong
3. Retry the subagent with a warning about the issue

Example validation failure:
```
❌ VALIDATION ERROR: Context file not found: files/context/accommodations.json
   Accommodation subagent must write curated list to files/context/accommodations.json

⚠️  RETRY: Re-run accommodation subagent with warning about missing context file
```

**Response:**
```
Re-invoke accommodation subagent with warning:

⚠️ Previous attempt failed validation. You MUST write the curated list to files/context/accommodations.json.

Build exhaustive masterlist of accommodations...
[rest of prompt]
```
