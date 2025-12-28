---
name: orchestrating-workflow
description: "Revision workflow orchestrator that dynamically selects subagents based on user revision requests. Analyzes requests for keywords to determine which of transportation/accommodation/activities subagents to invoke. Always runs verification last. Manages progressive Supabase updates and change_log."
---

# Orchestrating Workflow - Revision Agent

You act as a **workflow orchestrator** for the revision agent that dynamically selects and routes between subagents based on user revision requests.

## Key Difference from Planning Agent

Unlike the planning agent's fixed sequence, this orchestrator:
1. **Analyzes requests** to determine which subagents to run
2. **Builds dynamic sequence** based on detected needs
3. **Uses existing data** as baseline for revisions
4. **Updates change_log** with revision history

## Dynamic Subagent Selection

The orchestrator analyzes revision requests using keyword matching:

| Request Keywords | Subagent | Examples |
|-----------------|----------|----------|
| flight, airline, departure, direct, layover | `transportation` | "I want a direct flight" |
| hotel, room, stay, lodging, suite | `accommodation` | "Cheaper hotel please" |
| restaurant, activity, tour, museum, dining | `activities` | "More upscale dining" |

### Special Cases

- **Price keywords** (cheaper, expensive, budget, luxury): Infer domain from context
- **Location keywords** (closer, nearby, central): Affect accommodation AND activities
- **Generic requests**: May trigger multiple subagents
- **Unknown requests**: Default to verification only

## When Invoked

1. **Read workflow_state.json** from `files/process/workflow_state.json`
2. **Read revision_context.json** from `files/process/revision_context.json`
3. **Call orchestrate.py** to update state and get next action
4. **Invoke the next subagent** using the Task tool

## Input Messages

### Workflow Start (after hook)
```
Use orchestrating-workflow to analyze requests and start revision workflow.
```
→ Analyzes requests → Returns first subagent to invoke

### After Any Subagent
```
[Step] revision complete. [summary of changes]
```
→ Updates Supabase → Returns next subagent or completion

## Orchestration Script

Use Bash to call the orchestration script:

### Initialize and Analyze Requests
```bash
python3 .claude/skills/orchestrating-workflow/scripts/orchestrate.py --init
```

Returns:
```json
{
  "status": "start",
  "detected_subagents": ["accommodation", "activities", "verification"],
  "next_step": "accommodation",
  "prompt": "..."
}
```

### Complete a Step
```bash
python3 .claude/skills/orchestrating-workflow/scripts/orchestrate.py \
  --completed-step accommodation \
  --message "Found 3 cheaper alternatives"
```

The script will:
1. Update `workflow_state.json` with completed step
2. Read revised data from `files/content/<step>/revised.json`
3. Update `user_plans.<field>` in Supabase (progressive update)
4. Return the next step to invoke or completion status

### Check Status
```bash
python3 .claude/skills/orchestrating-workflow/scripts/orchestrate.py --status
```

## Invoking Subagents

After determining the next step, invoke the subagent using the Task tool:

```
Use Task tool to invoke the '{next_step}' agent with prompt:
"Revise {step} based on user requests. Read files/process/revision_context.json for:
- existing_plan.{step} (current selection as baseline)
- occasion.{plural} (masterlist for alternatives)
- requests (what to change)
Write revised results to files/content/{step}/revised.json
When complete, invoke orchestrating-workflow skill."
```

## Subagent Prompts (Revision-Aware)

### Transportation (if detected)
```
Revise transportation based on user requests.
1. Read files/process/revision_context.json
2. Use existing_plan.transportation as BASELINE
3. Search for alternatives via duffel skill
4. Apply revision constraints (cheaper, direct, earlier, etc.)
5. Write to files/content/transportation/revised.json
6. Invoke orchestrating-workflow when complete
```

### Accommodation (if detected)
```
Revise accommodation based on user requests.
1. Read files/process/revision_context.json
2. Use existing_plan.accommodation as BASELINE
3. Select alternatives from occasion.accommodations masterlist
4. Apply revision constraints (cheaper, closer, better-rated, etc.)
5. Write to files/content/accommodation/revised.json
6. Invoke orchestrating-workflow when complete
```

### Activities (if detected)
```
Revise activities based on user requests.
1. Read files/process/revision_context.json
2. Use existing_plan.activities as BASELINE
3. Select alternatives from occasion.activities masterlist
4. Apply revision constraints (upscale, add/remove, category change)
5. Write to files/content/activities/revised.json
6. Invoke orchestrating-workflow when complete
```

### Verification (always runs last)
```
Verify revised plan consistency.
1. Read all revised data from files/content/*/revised.json
2. Compare with existing_plan from revision_context.json
3. Validate no schedule conflicts introduced
4. Regenerate day-by-day plan with revision notes
5. Write to files/content/verification/verified.json
6. Invoke orchestrating-workflow when complete
```

## Progressive Supabase Updates

After each subagent (except verification):
```
user_plans UPDATE:
  - <field> = revised data
  - updated_at = now
```

After verification (final):
```
user_plans UPDATE:
  - plan = regenerated itinerary
  - change_log = existing + new entry
  - updated_at = now
```

## Change Log Entry Format

```json
{
  "revision_id": "uuid",
  "timestamp": "2025-01-15T10:10:00Z",
  "requests": ["I want a cheaper hotel", "More upscale dining"],
  "changes": {
    "accommodation": {
      "revised": true,
      "summary": "Changed from Hotel Hermitage to Hotel Ambassador"
    },
    "activities": {
      "revised": true,
      "summary": "Upgraded dinner reservation to Le Louis XV"
    }
  },
  "subagents_invoked": ["accommodation", "activities", "verification"]
}
```

## Example Flow

```
Input: {"user_plan_id": "uuid", "requests": ["cheaper hotel", "upscale restaurant"]}

1. Hook creates revision_context.json with existing plan + masterlists

2. orchestrate.py --init:
   - Analyzes "cheaper hotel" → accommodation
   - Analyzes "upscale restaurant" → activities
   - Returns steps: ["accommodation", "activities", "verification"]

3. Accommodation subagent runs:
   - Uses existing hotel as baseline
   - Finds cheaper alternatives from masterlist
   - Writes revised.json

4. orchestrate.py --completed-step accommodation:
   - Updates user_plans.accommodation in Supabase
   - Returns next_step: activities

5. Activities subagent runs:
   - Uses existing activities as baseline
   - Finds upscale restaurant in masterlist
   - Writes revised.json

6. orchestrate.py --completed-step activities:
   - Updates user_plans.activities in Supabase
   - Returns next_step: verification

7. Verification subagent runs:
   - Validates all changes
   - Regenerates day-by-day plan
   - Writes verified.json

8. orchestrate.py --completed-step verification:
   - Updates user_plans.plan with new itinerary
   - Appends to user_plans.change_log
   - Returns status: complete

Output: "Revision complete! Changed hotel to save 50%, upgraded dinner reservation."
```

## Workflow Completion

When all steps are complete, output:

```
Revision workflow complete!

Changes applied:
- Accommodation: [summary]
- Activities: [summary]

Supabase updated:
- user_plans.accommodation
- user_plans.activities
- user_plans.plan (regenerated)
- user_plans.change_log (entry appended)
```
