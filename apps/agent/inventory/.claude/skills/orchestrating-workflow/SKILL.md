---
name: orchestrating-workflow
description: "Workflow orchestrator for inventory agent. Routes between subagents in sequence: 1. accommodation → 2. activities. Updates Supabase occasions table with masterlists on completion."
---

# Orchestrating Workflow - Inventory Agent

You act as a **workflow orchestrator** for building exhaustive masterlists of accommodations and activities for an occasion.

## Subagent Sequence

```
1. accommodation  →  Search all hotels via Duffel + Google Maps
2. activities     →  Search all activities via Google Maps
```

After all steps complete, the orchestrator updates Supabase:
```sql
UPDATE occasions SET accommodations=..., activities=... WHERE id=occasion_id
```

## When Invoked

1. **Read workflow_state.json** from `files/process/workflow_state.json`
2. **Read occasion_context.json** from `files/process/occasion_context.json`
3. **Call orchestrate.py** to update state and get next action
4. **Invoke the next subagent** using the Task tool

## Input Messages

### Workflow Start
```
Workflow initialized. Starting inventory sequence for [occasion].
```
→ Call `orchestrate.py --init`
→ Invoke **accommodation** subagent

### After Accommodation
```
Accommodation research complete. [details]
```
→ Call `orchestrate.py --completed-step accommodation --message "..."`
→ Invoke **activities** subagent

### After Activities (FINAL)
```
Activities research complete. [details]
```
→ Call `orchestrate.py --completed-step activities --message "..."`
→ orchestrate.py compiles results and updates Supabase
→ Workflow complete!

## Orchestration Script

Use Bash to call the orchestration script:

```bash
# Initialize workflow
python3 .claude/skills/orchestrating-workflow/scripts/orchestrate.py --init

# After accommodation completes
python3 .claude/skills/orchestrating-workflow/scripts/orchestrate.py \
  --completed-step accommodation \
  --message "Found 45 hotels from duffel and google-maps"

# After activities completes (triggers Supabase update)
python3 .claude/skills/orchestrating-workflow/scripts/orchestrate.py \
  --completed-step activities \
  --message "Found 120 activities across 8 categories"
```

The script will:
1. Update `workflow_state.json` with completed step
2. Append to history with timestamp
3. On final step: compile all results and UPDATE Supabase occasions table
4. Return the next step to invoke (or complete status)

## Invoking Subagents

After determining the next step, invoke the subagent using the Task tool:

```
Use Task tool to invoke the '{next_step}' agent with prompt from orchestrate.py output.
```

## Subagent Prompts

### Accommodation
```
Build exhaustive masterlist of accommodations for [occasion] in [city], [country].

1. Read files/process/occasion_context.json for location and date context
2. Use the duffel skill to search for all hotels in the area
3. Use the google-maps skill to search for lodging places
4. Write results to files/content/accommodations/ as JSON files
5. Include all hotels regardless of price or availability

When complete, use Skill tool to invoke 'orchestrating-workflow' with message:
'Accommodation research complete. Found [count] hotels from duffel and google-maps.'
```

### Activities
```
Build exhaustive masterlist of activities for [occasion] in [city], [country].

1. Read files/process/occasion_context.json for location and description context
2. Use the occasion description to understand what activities are relevant
3. Use the google-maps skill to search for:
   - Restaurants, cafes, bars
   - Tourist attractions, museums, art galleries
   - Parks, spas, shopping centers
   - Occasion-specific venues (based on description)
4. Write results to files/content/activities/ as JSON files
5. Include all places regardless of price level

When complete, use Skill tool to invoke 'orchestrating-workflow' with message:
'Activities research complete. Found [count] activities across [categories] categories.'
```

## Workflow Completion

When all steps are complete, the orchestrate.py script will:

1. Read all files from `files/content/accommodations/`
2. Read all files from `files/content/activities/`
3. Deduplicate and merge into flat lists
4. UPDATE Supabase: `occasions SET accommodations=..., activities=... WHERE id=occasion_id`

Output:
```
Workflow complete! Inventory masterlist built for [occasion].

Summary:
- Accommodations: [count] hotels (sources: duffel, google_maps)
- Activities: [count] places (categories: restaurants, attractions, etc.)

Supabase occasions table updated successfully.
```

## Key Principles

1. **No filtering** - Build exhaustive masterlist regardless of price/availability
2. **Use occasion description** - Context for relevant activity categories
3. **Flat list format** - Simple array of objects tagged with source
4. **Supabase update at end** - Compile and update occasions table
