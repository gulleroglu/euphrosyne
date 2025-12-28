---
name: orchestrating-workflow
description: "Workflow orchestrator for planning agent. Routes between subagents in fixed sequence: transportation → accommodation → activities → verification. Performs progressive Supabase updates after each step. Invoke at workflow start and after each subagent completes."
---

# Orchestrating Workflow - Planning Agent

You act as a **workflow orchestrator** that routes between travel planning subagents in a fixed sequence, updating Supabase progressively after each step.

## Subagent Sequence

```
1. transportation  →  LIVE flight search via duffel
2. accommodation   →  SELECT from occasion masterlist
3. activities      →  SELECT from occasion masterlist
4. verification    →  Create day-by-day plan
```

**Key Principle**: This skill is ALWAYS invoked between steps. It decides what happens next and updates Supabase with results.

## When Invoked

1. **Run orchestrate.py** to update state and get next action
2. **If step completed**: Read results from `files/content/<step>/`, update Supabase
3. **Invoke the next subagent** using the Task tool
4. **If workflow complete**: Report final status

## Input Messages

### Workflow Start
```
Workflow initialized. Starting planning sequence for [user] attending [occasion].
```
→ Run `orchestrate.py --init`
→ Invoke **transportation** subagent

### After Transportation
```
Transportation research complete. [summary]
```
→ Run `orchestrate.py --completed-step transportation --message "[summary]"`
→ Updates `user_plans.transportation` in Supabase
→ Invoke **accommodation** subagent

### After Accommodation
```
Accommodation selection complete. [summary]
```
→ Run `orchestrate.py --completed-step accommodation --message "[summary]"`
→ Updates `user_plans.accommodation` in Supabase
→ Invoke **activities** subagent

### After Activities
```
Activities selection complete. [summary]
```
→ Run `orchestrate.py --completed-step activities --message "[summary]"`
→ Updates `user_plans.activities` in Supabase
→ Invoke **verification** subagent

### After Verification (FINAL)
```
Verification complete. Created day-by-day plan. [summary]
```
→ Run `orchestrate.py --completed-step verification --message "[summary]"`
→ Updates `user_plans.plan` and `user_plans.change_log` in Supabase
→ Workflow complete!

## Orchestration Script

Use Bash to call the orchestration script:

```bash
# Initialize workflow
python3 .claude/skills/orchestrating-workflow/scripts/orchestrate.py --init

# Mark step complete (triggers Supabase update)
python3 .claude/skills/orchestrating-workflow/scripts/orchestrate.py \
  --completed-step transportation \
  --message "Selected Emirates business class at $2450"

# Check status
python3 .claude/skills/orchestrating-workflow/scripts/orchestrate.py --status
```

The script will:
1. Read results from `files/content/<step>/results.json`
2. Update `user_plans` in Supabase with results
3. Update `workflow_state.json` with completion
4. Return the next step to invoke

## Invoking Subagents

After determining the next step, invoke the subagent using the Task tool:

```
Use Task tool to invoke the '{next_step}' agent with the prompt returned by orchestrate.py.
```

## Subagent Prompts

### Transportation
- Read user preferences and occasion context
- Use duffel skill for LIVE flight search
- Apply preferences (cabin class, timing, budget)
- Write results to `files/content/transportation/results.json`

### Accommodation
- Read occasion masterlist (NOT external search)
- Apply user preferences to filter/rank
- Select 1 primary + 2 alternatives
- Write results to `files/content/accommodation/results.json`

### Activities
- Read occasion masterlist (NOT external search)
- Calculate available time
- Apply user interests to filter
- Write results to `files/content/activities/results.json`

### Verification
- Read all selections from `files/content/`
- Verify schedule compatibility
- Calculate travel times (google-maps)
- Create day-by-day plan
- Write results to `files/content/verification/results.json`

## Progressive Supabase Updates

After each step, the orchestrate.py script updates Supabase:

| Step | Supabase Field Updated |
|------|------------------------|
| transportation | `user_plans.transportation` |
| accommodation | `user_plans.accommodation` |
| activities | `user_plans.activities` |
| verification | `user_plans.plan`, `user_plans.change_log` |

## Workflow Completion

When all steps are complete, output:

```
Workflow complete! Planning finished.

User Plan ID: [user_plan_id]
Completed Steps: transportation, accommodation, activities, verification

Summary:
- Flights: [airline] [cabin] at $[price]
- Hotel: [hotel_name] ([stars] stars)
- Activities: [count] planned
- Plan: Day-by-day itinerary created

View plan: user_plans table, id = [user_plan_id]
```

## Context Files

The workflow uses these context files:

| File | Purpose |
|------|---------|
| `files/process/user_context.json` | User preferences (markdown) |
| `files/process/occasion_context.json` | Occasion + masterlists |
| `files/process/plan_context.json` | user_plan_id reference |
| `files/process/workflow_state.json` | Workflow progress tracking |

## Key Principles

1. **Always between steps** - This skill decides what happens next
2. **Progressive updates** - Supabase updated after each step completes
3. **Masterlists for selection** - Accommodation and activities come from occasion data
4. **LIVE for transportation** - Flights searched in real-time via duffel
5. **Verification creates plan** - Final step synthesizes all selections
