# Planning Agent - Implementation Plan

## Overview

| Aspect | Detail |
|--------|--------|
| Location | `apps/agent/planning/` |
| Purpose | Create initial personalized travel plan for a user attending an occasion |
| Frequency | Per user request |
| Input | `{"user_id": "...", "occasion_id": "..."}` |
| Output | INSERT/UPDATE `user_plans` (transportation, accommodation, activities, plan, change_log) |
| Subagents | `transportation`, `accommodation`, `activities`, `verification` |
| Skills | `orchestrating-workflow`, `duffel`, `google-maps` |

---

## Tables Reference

```sql
users:
  id              UUID PRIMARY KEY
  first_name      TEXT
  last_name       TEXT
  email           TEXT
  mobile_number   TEXT
  preferences     TEXT           -- Markdown text with user preferences
  created_at      TIMESTAMPTZ
  updated_at      TIMESTAMPTZ

occasions:
  id              UUID PRIMARY KEY
  occasion        TEXT
  description     TEXT
  city            TEXT
  country         TEXT
  full_address    TEXT
  start_date      DATE
  end_date        DATE
  accommodations  JSONB          -- Masterlist from inventory agent
  activities      JSONB          -- Masterlist from inventory agent
  created_at      TIMESTAMPTZ
  updated_at      TIMESTAMPTZ

user_plans:
  id              UUID PRIMARY KEY
  occasion_id     UUID REFERENCES occasions(id)
  user_id         UUID REFERENCES users(id)
  transportation  JSONB          -- Selected flights
  accommodation   JSONB          -- Selected hotel (from masterlist)
  activities      JSONB          -- Selected activities (from masterlist)
  plan            JSONB          -- Day-by-day itinerary
  change_log      JSONB          -- History of changes
  created_at      TIMESTAMPTZ
  updated_at      TIMESTAMPTZ
```

---

## Architecture

```
INPUT: {"user_id": "...", "occasion_id": "..."}
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  HOOK: workflow_init.py                                     │
│  • Fetch user from Supabase (preferences)                   │
│  • Fetch occasion from Supabase (masterlists)               │
│  • CREATE user_plans row (get user_plan_id)                 │
│  • Write context files                                      │
│  • Invoke orchestrating-workflow                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATING-WORKFLOW (init)                              │
│  • orchestrate.py --init                                    │
│  • Returns: next_step = "transportation"                    │
│  • Invoke transportation subagent                           │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  SUBAGENT: transportation                                   │
│  • Read user preferences + occasion context                 │
│  • Use duffel skill: LIVE flight search                     │
│  • Find flights with fares and seat options                 │
│  • Write to files/content/transportation/                   │
│  • Invoke orchestrating-workflow                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATING-WORKFLOW (after transportation)              │
│  • orchestrate.py --completed-step transportation           │
│  • UPDATE user_plans SET transportation = {...}             │
│  • Returns: next_step = "accommodation"                     │
│  • Invoke accommodation subagent                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  SUBAGENT: accommodation                                    │
│  • Read occasion.accommodations masterlist                  │
│  • Apply user preferences to filter/rank                    │
│  • SELECT 3 best options from masterlist                    │
│  • Write to files/content/accommodation/                    │
│  • Invoke orchestrating-workflow                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATING-WORKFLOW (after accommodation)               │
│  • orchestrate.py --completed-step accommodation            │
│  • UPDATE user_plans SET accommodation = {...}              │
│  • Returns: next_step = "activities"                        │
│  • Invoke activities subagent                               │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  SUBAGENT: activities                                       │
│  • Read occasion.activities masterlist                      │
│  • Calculate available hours (based on stay length)         │
│  • Apply user preferences to filter/rank                    │
│  • SELECT appropriate activities to fill schedule           │
│  • Write to files/content/activities/                       │
│  • Invoke orchestrating-workflow                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATING-WORKFLOW (after activities)                  │
│  • orchestrate.py --completed-step activities               │
│  • UPDATE user_plans SET activities = {...}                 │
│  • Returns: next_step = "verification"                      │
│  • Invoke verification subagent                             │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  SUBAGENT: verification                                     │
│  • Read all selections (transportation, accommodation,      │
│    activities)                                              │
│  • Verify schedule compatibility                            │
│  • Verify budget compliance (if specified in preferences)   │
│  • Create day-by-day plan                                   │
│  • Write to files/content/verification/                     │
│  • Invoke orchestrating-workflow                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATING-WORKFLOW (after verification - FINAL)        │
│  • orchestrate.py --completed-step verification             │
│  • UPDATE user_plans SET                                    │
│      plan = {...day-by-day itinerary...},                   │
│      change_log = [{"action": "initial_plan", ...}]         │
│  • Returns: status = "complete"                             │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
      DONE
```

---

## Directory Structure

```
apps/agent/planning/
├── .claude/
│   ├── settings.json
│   ├── hooks/
│   │   └── workflow_init.py
│   ├── agents/
│   │   ├── transportation.md
│   │   ├── accommodation.md
│   │   ├── activities.md
│   │   └── verification.md
│   └── skills/
│       ├── orchestrating-workflow/
│       │   ├── SKILL.md
│       │   └── scripts/
│       │       └── orchestrate.py
│       ├── duffel/
│       │   ├── SKILL.md
│       │   ├── scripts/
│       │   │   ├── duffel_client.py
│       │   │   └── search_flights.py
│       │   └── references/
│       │       └── api.md
│       └── google-maps/
│           ├── SKILL.md
│           ├── scripts/
│           │   ├── maps_client.py
│           │   └── get_directions.py
│           └── references/
│               └── api.md
└── files/
    ├── process/
    │   ├── user_context.json
    │   ├── occasion_context.json
    │   ├── plan_context.json
    │   └── workflow_state.json
    └── content/
        ├── transportation/
        ├── accommodation/
        ├── activities/
        └── verification/
```

---

## Implementation Checklist

### Phase 1: Directory Structure

- [ ] Create `apps/agent/planning/.claude/` directory
- [ ] Create `apps/agent/planning/.claude/hooks/` directory
- [ ] Create `apps/agent/planning/.claude/agents/` directory
- [ ] Create `apps/agent/planning/.claude/skills/orchestrating-workflow/scripts/` directory
- [ ] Create `apps/agent/planning/.claude/skills/duffel/scripts/` directory
- [ ] Create `apps/agent/planning/.claude/skills/duffel/references/` directory
- [ ] Create `apps/agent/planning/.claude/skills/google-maps/scripts/` directory
- [ ] Create `apps/agent/planning/.claude/skills/google-maps/references/` directory
- [ ] Create `apps/agent/planning/files/process/` directory
- [ ] Create `apps/agent/planning/files/content/transportation/` directory
- [ ] Create `apps/agent/planning/files/content/accommodation/` directory
- [ ] Create `apps/agent/planning/files/content/activities/` directory
- [ ] Create `apps/agent/planning/files/content/verification/` directory

### Phase 2: Settings & Configuration

- [ ] Create `apps/agent/planning/.claude/settings.json`
  - [ ] Configure UserPromptSubmit hook
  - [ ] Configure Stop hook
  - [ ] Set permissions for Bash, Skills

### Phase 3: Hook System

- [ ] Create `apps/agent/planning/.claude/hooks/workflow_init.py`
  - [ ] Parse `{"user_id": "...", "occasion_id": "..."}` from stdin
  - [ ] Connect to Supabase
  - [ ] Fetch user row: `SELECT * FROM users WHERE id = user_id`
  - [ ] Fetch occasion row: `SELECT * FROM occasions WHERE id = occasion_id`
  - [ ] Validate both exist
  - [ ] INSERT new user_plans row, get user_plan_id
  - [ ] Write `files/process/user_context.json`
  - [ ] Write `files/process/occasion_context.json` (includes masterlists)
  - [ ] Write `files/process/plan_context.json` (user_plan_id, user_id, occasion_id)
  - [ ] Initialize `files/process/workflow_state.json`
  - [ ] Output message to invoke orchestrating-workflow skill

### Phase 4: Orchestrating-Workflow Skill

- [ ] Create `apps/agent/planning/.claude/skills/orchestrating-workflow/SKILL.md`
  - [ ] Define sequence: `transportation → accommodation → activities → verification`
  - [ ] Document input message formats for each transition
  - [ ] Document progressive Supabase updates after each step

- [ ] Create `apps/agent/planning/.claude/skills/orchestrating-workflow/scripts/orchestrate.py`
  - [ ] Implement `--init` handler
    - [ ] Read plan_context.json to get user_plan_id
    - [ ] Create/update workflow_state.json
    - [ ] Return first step: transportation
  - [ ] Implement `--completed-step <step>` handler
    - [ ] Update workflow_state.json
    - [ ] Read results from files/content/<step>/
    - [ ] UPDATE user_plans SET <field> = results
    - [ ] Determine next step
  - [ ] Step-to-field mapping:
    - [ ] transportation → user_plans.transportation
    - [ ] accommodation → user_plans.accommodation
    - [ ] activities → user_plans.activities
    - [ ] verification → user_plans.plan + user_plans.change_log
  - [ ] Implement `--status` handler

### Phase 5: Duffel Skill (Flights)

- [ ] Create `apps/agent/planning/.claude/skills/duffel/SKILL.md`
  - [ ] Focus on LIVE flight search with pricing
  - [ ] Document fare and seat selection options

- [ ] Create `apps/agent/planning/.claude/skills/duffel/scripts/duffel_client.py`

- [ ] Create `apps/agent/planning/.claude/skills/duffel/scripts/search_flights.py`
  - [ ] Accept origin, destination, dates, passengers, cabin class
  - [ ] Return flight options with fares
  - [ ] Include seat availability if possible

- [ ] Create `apps/agent/planning/.claude/skills/duffel/references/api.md`

### Phase 6: Google Maps Skill (Directions)

- [ ] Create `apps/agent/planning/.claude/skills/google-maps/SKILL.md`
  - [ ] Focus on directions/routes for itinerary planning
  - [ ] Calculate travel times between locations

- [ ] Create `apps/agent/planning/.claude/skills/google-maps/scripts/maps_client.py`

- [ ] Create `apps/agent/planning/.claude/skills/google-maps/scripts/get_directions.py`
  - [ ] Calculate routes between accommodation and activities
  - [ ] Support different travel modes

- [ ] Create `apps/agent/planning/.claude/skills/google-maps/references/api.md`

### Phase 7: Subagents

- [ ] Create `apps/agent/planning/.claude/agents/transportation.md`
  - [ ] Read user preferences (markdown text)
  - [ ] Read occasion context (city, dates)
  - [ ] Determine origin from user preferences or ask
  - [ ] Use duffel skill for LIVE flight search
  - [ ] Apply preferences (cabin class, budget, timing)
  - [ ] Write selected options to files/content/transportation/
  - [ ] Invoke orchestrating-workflow on completion

- [ ] Create `apps/agent/planning/.claude/agents/accommodation.md`
  - [ ] Read occasion.accommodations masterlist
  - [ ] Read user preferences
  - [ ] Filter masterlist by preferences (stars, amenities, location)
  - [ ] Rank and SELECT top 3 options
  - [ ] Write to files/content/accommodation/
  - [ ] Invoke orchestrating-workflow on completion

- [ ] Create `apps/agent/planning/.claude/agents/activities.md`
  - [ ] Read occasion.activities masterlist
  - [ ] Read user preferences (interests)
  - [ ] Calculate trip duration and available hours
  - [ ] Filter by preferences and occasion relevance
  - [ ] SELECT activities to fill schedule appropriately
  - [ ] Consider meal times (restaurants for breakfast/lunch/dinner)
  - [ ] Write to files/content/activities/
  - [ ] Invoke orchestrating-workflow on completion

- [ ] Create `apps/agent/planning/.claude/agents/verification.md`
  - [ ] Read all selected items from files/content/
  - [ ] Verify flight times vs check-in/check-out
  - [ ] Verify activity schedule doesn't conflict
  - [ ] Calculate travel times between locations (google-maps)
  - [ ] Verify budget if specified in preferences
  - [ ] Create day-by-day plan structure
  - [ ] Write verification report + plan to files/content/verification/
  - [ ] Invoke orchestrating-workflow on completion

### Phase 8: Testing & Validation

- [ ] Set environment variables
- [ ] Create test user row in Supabase (with preferences markdown)
- [ ] Ensure test occasion has masterlists populated (run inventory first)
- [ ] Run planning agent with test user_id + occasion_id
- [ ] Verify progressive Supabase updates:
  - [ ] user_plans.transportation updated after transportation step
  - [ ] user_plans.accommodation updated after accommodation step
  - [ ] user_plans.activities updated after activities step
  - [ ] user_plans.plan + change_log updated after verification
- [ ] Verify final user_plans row is complete

---

## File Schemas

### user_context.json

```json
{
  "id": "user-uuid",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "mobile_number": "+1234567890",
  "preferences": "## Travel Preferences\n\n### Flights\n- Prefer business class for long haul\n- Window seat\n- Morning departures\n\n### Accommodation\n- Minimum 4-star hotels\n- Must have gym and pool\n- Central location preferred\n\n### Interests\n- Fine dining\n- Motorsport events\n- Luxury experiences\n\n### Budget\n- Flexible, quality over cost\n\n### Dietary\n- No restrictions"
}
```

### occasion_context.json

```json
{
  "id": "occasion-uuid",
  "occasion": "Monaco Grand Prix 2025",
  "description": "Formula 1 World Championship race weekend...",
  "city": "Monaco",
  "country": "Monaco",
  "full_address": "Circuit de Monaco, Monte Carlo",
  "start_date": "2025-05-23",
  "end_date": "2025-05-25",
  "accommodations": [...masterlist from inventory...],
  "activities": [...masterlist from inventory...]
}
```

### plan_context.json

```json
{
  "user_plan_id": "plan-uuid",
  "user_id": "user-uuid",
  "occasion_id": "occasion-uuid",
  "created_at": "2025-01-15T10:00:00Z"
}
```

### workflow_state.json

```json
{
  "user_plan_id": "plan-uuid",
  "current_step": 2,
  "steps": ["transportation", "accommodation", "activities", "verification"],
  "completed_steps": ["transportation", "accommodation"],
  "status": "in_progress",
  "started_at": "2025-01-15T10:00:00Z",
  "history": [
    {
      "step": "transportation",
      "message": "Found 5 flight options, selected business class on Emirates",
      "completed_at": "2025-01-15T10:05:00Z",
      "supabase_updated": true
    },
    {
      "step": "accommodation",
      "message": "Selected 3 hotels from masterlist",
      "completed_at": "2025-01-15T10:08:00Z",
      "supabase_updated": true
    }
  ]
}
```

### user_plans.transportation

```json
{
  "outbound": {
    "flight_id": "offer_abc123",
    "airline": "Emirates",
    "flight_number": "EK073",
    "origin": "JFK",
    "destination": "NCE",
    "departure": "2025-05-22T22:00:00",
    "arrival": "2025-05-23T12:30:00",
    "cabin_class": "business",
    "price": {
      "amount": "2450.00",
      "currency": "USD"
    },
    "seats": ["12A", "12B"]
  },
  "return": {
    "flight_id": "offer_def456",
    "airline": "Emirates",
    "flight_number": "EK074",
    "origin": "NCE",
    "destination": "JFK",
    "departure": "2025-05-26T14:00:00",
    "arrival": "2025-05-26T18:30:00",
    "cabin_class": "business",
    "price": {
      "amount": "2450.00",
      "currency": "USD"
    }
  },
  "total_price": {
    "amount": "4900.00",
    "currency": "USD"
  }
}
```

### user_plans.accommodation

```json
{
  "selected": {
    "id": "hotel_abc123",
    "name": "Hotel Hermitage Monte-Carlo",
    "stars": 5,
    "rating": 4.8,
    "address": "Square Beaumarchais, Monaco",
    "check_in": "2025-05-23",
    "check_out": "2025-05-26",
    "nights": 3,
    "room_type": "Deluxe Sea View",
    "price_per_night": 850,
    "total_price": 2550,
    "currency": "EUR"
  },
  "alternatives": [
    {
      "id": "hotel_def456",
      "name": "Fairmont Monte Carlo",
      "stars": 4,
      "price_per_night": 650
    },
    {
      "id": "hotel_ghi789",
      "name": "Hotel Metropole",
      "stars": 5,
      "price_per_night": 920
    }
  ]
}
```

### user_plans.activities

```json
[
  {
    "id": "activity_001",
    "name": "Café de Paris Monte-Carlo",
    "category": "restaurant",
    "scheduled_for": "2025-05-23",
    "time_slot": "dinner",
    "estimated_duration": "2h",
    "price_level": 3,
    "notes": "Reservation recommended"
  },
  {
    "id": "activity_002",
    "name": "F1 Qualifying Session",
    "category": "event",
    "scheduled_for": "2025-05-24",
    "time_slot": "afternoon",
    "estimated_duration": "3h",
    "notes": "Included in race weekend ticket"
  }
]
```

### user_plans.plan

```json
{
  "summary": {
    "destination": "Monaco",
    "dates": "May 22-26, 2025",
    "duration_nights": 3,
    "total_estimated_cost": {
      "flights": 4900,
      "accommodation": 2550,
      "activities": 500,
      "total": 7950,
      "currency": "USD"
    }
  },
  "days": [
    {
      "date": "2025-05-23",
      "day_number": 1,
      "theme": "Arrival & Orientation",
      "schedule": [
        {
          "time": "12:30",
          "activity": "Arrive Nice Airport (NCE)",
          "type": "travel",
          "notes": "Flight EK073"
        },
        {
          "time": "14:00",
          "activity": "Transfer to Monaco",
          "type": "travel",
          "duration": "45 min"
        },
        {
          "time": "15:00",
          "activity": "Check-in Hotel Hermitage",
          "type": "accommodation"
        },
        {
          "time": "19:00",
          "activity": "Dinner at Café de Paris",
          "type": "dining",
          "reservation": true
        }
      ]
    }
  ]
}
```

### user_plans.change_log

```json
[
  {
    "timestamp": "2025-01-15T10:15:00Z",
    "action": "initial_plan",
    "agent": "planning",
    "summary": "Created initial plan for Monaco GP 2025",
    "details": {
      "transportation": "Emirates business class",
      "accommodation": "Hotel Hermitage Monte-Carlo",
      "activities_count": 8
    }
  }
]
```

---

## Key Differences from Inventory Agent

| Aspect | Inventory | Planning |
|--------|-----------|----------|
| Input | `occasion_id` | `{user_id, occasion_id}` |
| Data source | LIVE API search | Masterlist + LIVE flights |
| Subagents | 2 (accommodation, activities) | 4 (+transportation, +verification) |
| Output table | `occasions` | `user_plans` |
| Supabase updates | At end only | Progressive after each step |
| Filters | None (exhaustive) | User preferences applied |
| Selection | All results | Best matches only |

---

## Environment Variables Required

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_service_role_key

# Duffel (Flights)
DUFFEL_API_KEY=duffel_live_xxx

# Google Maps (Directions)
GOOGLE_MAPS_API_KEY=AIzaSyxxx
```

---

## Key Principles

1. **Orchestrating-workflow is ALWAYS in between steps** - decides next action
2. **Progressive Supabase updates** - update user_plans after each subagent completes
3. **User preferences drive selection** - parse markdown preferences to filter/rank
4. **Masterlist as source** - accommodation and activities come from occasion masterlists
5. **Flights are LIVE** - transportation searches Duffel API in real-time
6. **Verification creates the plan** - synthesizes all selections into day-by-day structure
