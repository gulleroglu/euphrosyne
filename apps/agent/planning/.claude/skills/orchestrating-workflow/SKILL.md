---
name: orchestrating-workflow
description: "Workflow orchestrator that routes between travel planning subagents in a fixed sequence: 1. transportation → 2. accommodation → 3. activities → 4. verification → 5. booking (optional). Invoke after each subagent completes to proceed to the next step. Also invoke at workflow start to begin the sequence."
---

# Orchestrating Workflow

You act as a **workflow orchestrator** that routes between travel planning subagents in a fixed sequence.

## Subagent Sequence

```
1. transportation  →  Research flights and ground transport
2. accommodation   →  Research hotels and stays
3. activities      →  Research things to do
4. verification    →  Validate all options
5. booking         →  Create final itinerary (optional)
```

## When Invoked

1. **Read workflow_state.json** from `files/process/workflow_state.json`
2. **Read trip_context.json** from `files/process/trip_context.json`
3. **Call orchestrate.py** to update state and get next action
4. **Invoke the next subagent** using the Task tool

## Input Messages

### Workflow Start
```
Workflow initialized. Starting travel planning sequence.
```
→ Invoke **transportation** subagent

### After Transportation
```
Transportation research complete. [details]
```
→ Invoke **accommodation** subagent

### After Accommodation
```
Accommodation research complete. [details]
```
→ Invoke **activities** subagent

### After Activities
```
Activities research complete. [details]
```
→ Invoke **verification** subagent

### After Verification
```
Verification complete. [details]
```
→ Invoke **booking** subagent OR finish if skip_booking=true

### After Booking
```
Booking complete. Itinerary created.
```
→ Workflow complete!

## Orchestration Script

Use Bash to call the orchestration script:

```bash
python3 .claude/skills/orchestrating-workflow/scripts/orchestrate.py \
  --completed-step transportation \
  --message "Found 5 flight options, best at $684"
```

The script will:
1. Update `workflow_state.json` with completed step
2. Return the next step to invoke
3. Return status if workflow is complete

## Invoking Subagents

After determining the next step, invoke the subagent using the Task tool:

```
Use Task tool to invoke the '{next_step}' agent with prompt:
"Research {task_description} for the trip. Read files/process/trip_context.json for trip details.
When complete, report back with results summary."
```

## Subagent Prompts

### Transportation
```
Research transportation options for this trip.
1. Read files/process/trip_context.json for trip details
2. Use the duffel skill to search for flights
3. Use the google-maps skill for ground transportation routes (airport to hotel)
4. Write results to files/content/flights/ and files/content/routes/
5. When complete, invoke orchestrating-workflow skill with completion message
```

### Accommodation
```
Research accommodation options for this trip.
1. Read files/process/trip_context.json for trip details
2. Use the duffel skill to search for hotels
3. Write results to files/content/hotels/
4. When complete, invoke orchestrating-workflow skill with completion message
```

### Activities
```
Research activities and things to do for this trip.
1. Read files/process/trip_context.json for trip details and preferences
2. Use the google-maps skill to search for places and attractions
3. Write results to files/content/activities/
4. When complete, invoke orchestrating-workflow skill with completion message
```

### Verification
```
Validate all travel research for this trip.
1. Read all research from files/content/
2. Check price consistency and availability
3. Verify schedule compatibility
4. Write verification report
5. When complete, invoke orchestrating-workflow skill with completion message
```

### Booking
```
Create final trip itinerary with booking information.
1. Read all research from files/content/
2. Read verification report
3. Compile final itinerary with booking links
4. Write to files/output/itinerary.md
5. When complete, invoke orchestrating-workflow skill with completion message
```

## Workflow Completion

When all steps are complete, output:

```
Workflow complete! Trip planning finished.
Final itinerary: files/output/itinerary.md

Summary:
- Flights: [count] options found
- Hotels: [count] options found
- Activities: [count] recommendations
- Total estimated cost: $[amount]
```
