# Revision Agent - Implementation Plan

## Overview

| Aspect | Detail |
|--------|--------|
| Location | `apps/agent/revision/` |
| Purpose | Handle user revision requests for existing travel plans |
| Frequency | On-demand per user request |
| Input | `{"user_plan_id": "uuid", "requests": ["I want a cheaper hotel", ...]}` |
| Output | UPDATE `user_plans` (affected fields + `plan` + `change_log`) |
| Subagents | `transportation`, `accommodation`, `activities`, `verification` (dynamic selection) |
| Skills | `orchestrating-workflow`, `duffel`, `google-maps` |

---

## Tables Reference

```sql
user_plans:
  id              UUID PRIMARY KEY
  occasion_id     UUID REFERENCES occasions(id)
  user_id         UUID REFERENCES users(id)
  transportation  JSONB          -- flight options + routes
  accommodation   JSONB          -- selected hotels
  activities      JSONB          -- selected activities
  plan            JSONB          -- day-by-day itinerary
  change_log      JSONB          -- revision history
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
  accommodations  JSONB          -- masterlist
  activities      JSONB          -- masterlist

users:
  id              UUID PRIMARY KEY
  first_name      TEXT
  last_name       TEXT
  email           TEXT
  mobile_number   TEXT
  preferences     TEXT           -- markdown
```

---

## Architecture

```
INPUT: {"user_plan_id": "uuid", "requests": ["cheaper hotel", "posh restaurant"]}
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  HOOK: workflow_init.py                                             │
│  • Parse user_plan_id and requests from stdin                       │
│  • Fetch user_plan from Supabase (includes existing data)           │
│  • Fetch user from Supabase (for preferences)                       │
│  • Fetch occasion from Supabase (for masterlists)                   │
│  • Write revision_context.json                                      │
│  • Initialize workflow_state.json                                   │
│  • Invoke orchestrating-workflow --init                             │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATING-WORKFLOW (init)                                      │
│  • orchestrate.py --init                                            │
│  • ANALYZE requests to determine which subagents needed             │
│  • Build dynamic subagent sequence                                  │
│  • Returns: subagents_to_run = ["accommodation", "activities"]      │
│  • Invoke first detected subagent                                   │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  DYNAMIC SUBAGENT EXECUTION                                         │
│  • Each subagent reads revision_context.json                        │
│  • Each subagent uses EXISTING DATA as starting point               │
│  • Each subagent applies revision constraints                       │
│  • Each subagent writes updated results                             │
│  • Each subagent invokes orchestrating-workflow                     │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATING-WORKFLOW (between steps)                             │
│  • orchestrate.py --completed-step <step>                           │
│  • Update workflow_state.json                                       │
│  • UPDATE user_plans SET <field>=... (progressive)                  │
│  • Returns: next subagent or "verification" if all done             │
│  • Invoke next subagent                                             │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  VERIFICATION (always runs last)                                    │
│  • Validate revised plan consistency                                │
│  • Check no conflicts introduced                                    │
│  • Regenerate day-by-day plan with changes                          │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATING-WORKFLOW (final)                                     │
│  • orchestrate.py --completed-step verification                     │
│  • UPDATE user_plans SET plan=..., change_log=...                   │
│  • Returns: status = "complete"                                     │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
      DONE
```

---

## Request Analysis Logic

The orchestrating-workflow skill must analyze revision requests to determine which subagents to invoke.

### Keyword Mapping

| Request Keywords | Subagent | Examples |
|-----------------|----------|----------|
| flight, airline, departure, arrival, layover, direct | `transportation` | "I want a direct flight", "Earlier departure" |
| hotel, accommodation, room, stay, lodging, cheaper | `accommodation` | "Cheaper hotel", "5-star hotel", "Closer to venue" |
| restaurant, activity, tour, museum, dinner, lunch, brunch | `activities` | "More upscale restaurants", "Add museum tours" |
| route, transfer, taxi, uber, drive | `transportation` | "Better airport transfer" |

### Analysis Rules

1. **Multiple keywords** → invoke multiple subagents
2. **Price-related** → infer from context (hotel price vs restaurant price)
3. **Location-related** → may affect accommodation AND activities
4. **Unknown** → default to verification only (human review)
5. **Always** → verification runs last regardless of other subagents

---

## Directory Structure

```
apps/agent/revision/
├── PLAN.md
├── .claude/
│   ├── settings.json
│   ├── hooks/
│   │   └── workflow_init.py
│   ├── agents/
│   │   ├── transportation.md        # Revision-aware
│   │   ├── accommodation.md         # Revision-aware
│   │   ├── activities.md            # Revision-aware
│   │   └── verification.md          # Revision-aware
│   └── skills/
│       ├── orchestrating-workflow/
│       │   ├── SKILL.md
│       │   └── scripts/
│       │       └── orchestrate.py   # With request analyzer
│       ├── duffel/
│       │   ├── SKILL.md
│       │   ├── scripts/
│       │   │   ├── duffel_client.py
│       │   │   ├── search_flights.py
│       │   │   └── search_hotels.py
│       │   └── references/
│       │       └── api.md
│       └── google-maps/
│           ├── SKILL.md
│           ├── scripts/
│           │   ├── maps_client.py
│           │   └── search_places.py
│           └── references/
│               └── api.md
└── files/
    ├── process/
    │   ├── revision_context.json    # Full context including existing data
    │   └── workflow_state.json
    └── content/
        ├── transportation/          # Revised results
        ├── accommodation/           # Revised results
        └── activities/              # Revised results
```

---

## Implementation Checklist

### Phase 1: Directory Structure

- [ ] Create `apps/agent/revision/.claude/` directory
- [ ] Create `apps/agent/revision/.claude/hooks/` directory
- [ ] Create `apps/agent/revision/.claude/agents/` directory
- [ ] Create `apps/agent/revision/.claude/skills/orchestrating-workflow/scripts/` directory
- [ ] Create `apps/agent/revision/.claude/skills/duffel/scripts/` directory
- [ ] Create `apps/agent/revision/.claude/skills/duffel/references/` directory
- [ ] Create `apps/agent/revision/.claude/skills/google-maps/scripts/` directory
- [ ] Create `apps/agent/revision/.claude/skills/google-maps/references/` directory
- [ ] Create `apps/agent/revision/files/process/` directory
- [ ] Create `apps/agent/revision/files/content/transportation/` directory
- [ ] Create `apps/agent/revision/files/content/accommodation/` directory
- [ ] Create `apps/agent/revision/files/content/activities/` directory

### Phase 2: Settings & Configuration

- [ ] Create `apps/agent/revision/.claude/settings.json`
  - [ ] Configure UserPromptSubmit hook
  - [ ] Configure Stop hook
  - [ ] Set permissions for Bash, Skills

### Phase 3: Hook System

- [ ] Create `apps/agent/revision/.claude/hooks/workflow_init.py`
  - [ ] Parse `{"user_plan_id": "...", "requests": [...]}` from stdin
  - [ ] Connect to Supabase
  - [ ] Fetch user_plan row: `SELECT * FROM user_plans WHERE id = user_plan_id`
  - [ ] Fetch user row: `SELECT * FROM users WHERE id = user_plan.user_id`
  - [ ] Fetch occasion row: `SELECT * FROM occasions WHERE id = user_plan.occasion_id`
  - [ ] Validate all data exists
  - [ ] Write `files/process/revision_context.json`
  - [ ] Initialize `files/process/workflow_state.json`
  - [ ] Output message to invoke orchestrating-workflow skill

### Phase 4: Orchestrating-Workflow Skill (Revision-Specific)

- [ ] Create `apps/agent/revision/.claude/skills/orchestrating-workflow/SKILL.md`
  - [ ] Document request analysis logic
  - [ ] Document dynamic subagent selection
  - [ ] Document progressive Supabase updates
  - [ ] Document change_log format

- [ ] Create `apps/agent/revision/.claude/skills/orchestrating-workflow/scripts/orchestrate.py`
  - [ ] Implement `--init` handler
    - [ ] Read revision_context.json (includes requests)
    - [ ] **ANALYZE REQUESTS** to determine subagents needed
    - [ ] Build dynamic subagents list
    - [ ] Create workflow_state.json with dynamic sequence
    - [ ] Return first subagent to invoke
  - [ ] Implement `--completed-step <step>` handler
    - [ ] Update workflow_state.json
    - [ ] Read results from files/content/<step>/
    - [ ] **UPDATE user_plans SET <field>=... WHERE id=user_plan_id**
    - [ ] Determine next step or verification
  - [ ] Implement `--status` handler
  - [ ] Implement final completion handler
    - [ ] Regenerate `plan` field (day-by-day itinerary)
    - [ ] Append to `change_log` with timestamp and requests
    - [ ] UPDATE user_plans SET plan=..., change_log=...

### Phase 5: Request Analyzer (Within orchestrate.py)

- [ ] Implement `analyze_requests(requests: list[str])` function
  - [ ] Define keyword mappings for each subagent
  - [ ] Parse each request for keywords
  - [ ] Deduplicate detected subagents
  - [ ] Order by dependency (transportation → accommodation → activities)
  - [ ] Always append verification at end
  - [ ] Return ordered list of subagents to run

### Phase 6: Duffel Skill

- [ ] Create `apps/agent/revision/.claude/skills/duffel/SKILL.md`
  - [ ] Document revision-aware search (using existing data as baseline)

- [ ] Create `apps/agent/revision/.claude/skills/duffel/scripts/duffel_client.py`

- [ ] Create `apps/agent/revision/.claude/skills/duffel/scripts/search_flights.py`
  - [ ] Accept existing flight data as input
  - [ ] Apply revision constraints (earlier, cheaper, direct, etc.)
  - [ ] Return alternatives that improve on baseline

- [ ] Create `apps/agent/revision/.claude/skills/duffel/scripts/search_hotels.py`
  - [ ] Accept existing hotel selection as input
  - [ ] Use occasion masterlist for alternatives
  - [ ] Apply revision constraints (cheaper, closer, better rating, etc.)
  - [ ] Return alternatives that improve on baseline

- [ ] Create `apps/agent/revision/.claude/skills/duffel/references/api.md`

### Phase 7: Google Maps Skill

- [ ] Create `apps/agent/revision/.claude/skills/google-maps/SKILL.md`
  - [ ] Document revision-aware search

- [ ] Create `apps/agent/revision/.claude/skills/google-maps/scripts/maps_client.py`

- [ ] Create `apps/agent/revision/.claude/skills/google-maps/scripts/search_places.py`
  - [ ] Accept existing activity selection as input
  - [ ] Use occasion masterlist for alternatives
  - [ ] Apply revision constraints (category, price level, rating, etc.)
  - [ ] Return alternatives or additions

- [ ] Create `apps/agent/revision/.claude/skills/google-maps/references/api.md`

### Phase 8: Subagents (Revision-Aware)

- [ ] Create `apps/agent/revision/.claude/agents/transportation.md`
  - [ ] Read revision_context.json
  - [ ] Identify transportation-related requests
  - [ ] Use **existing transportation data as baseline**
  - [ ] Search for alternatives via duffel skill
  - [ ] Write revised results to files/content/transportation/
  - [ ] Invoke orchestrating-workflow on completion

- [ ] Create `apps/agent/revision/.claude/agents/accommodation.md`
  - [ ] Read revision_context.json
  - [ ] Identify accommodation-related requests
  - [ ] Use **existing accommodation data as baseline**
  - [ ] Select alternatives from occasion masterlist
  - [ ] Optionally search via duffel for non-masterlist options
  - [ ] Write revised results to files/content/accommodation/
  - [ ] Invoke orchestrating-workflow on completion

- [ ] Create `apps/agent/revision/.claude/agents/activities.md`
  - [ ] Read revision_context.json
  - [ ] Identify activities-related requests
  - [ ] Use **existing activities data as baseline**
  - [ ] Select alternatives/additions from occasion masterlist
  - [ ] Write revised results to files/content/activities/
  - [ ] Invoke orchestrating-workflow on completion

- [ ] Create `apps/agent/revision/.claude/agents/verification.md`
  - [ ] Read all revised data
  - [ ] Validate consistency (no schedule conflicts, etc.)
  - [ ] Regenerate day-by-day plan
  - [ ] Write verification results
  - [ ] Invoke orchestrating-workflow on completion

### Phase 9: Testing & Validation

- [ ] Set environment variables
- [ ] Create test user_plan row in Supabase
- [ ] Test single-subagent revision (e.g., "cheaper hotel")
- [ ] Test multi-subagent revision (e.g., "cheaper hotel and better restaurant")
- [ ] Test transportation revision (live Duffel search)
- [ ] Verify workflow_state.json updates correctly
- [ ] Verify progressive Supabase updates after each step
- [ ] Verify change_log appends correctly
- [ ] Verify plan field regenerated

---

## File Schemas

### revision_context.json

```json
{
  "user_plan_id": "uuid",
  "requests": [
    "I want a cheaper hotel",
    "I want a more upscale restaurant for Saturday dinner"
  ],
  "user": {
    "id": "uuid",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "preferences": "## Travel Style\n- Prefer boutique hotels..."
  },
  "occasion": {
    "id": "uuid",
    "occasion": "Monaco Grand Prix 2025",
    "description": "Formula 1 race weekend...",
    "city": "Monaco",
    "country": "Monaco",
    "start_date": "2025-05-23",
    "end_date": "2025-05-25",
    "accommodations": [...],
    "activities": [...]
  },
  "existing_plan": {
    "transportation": {...},
    "accommodation": {...},
    "activities": {...},
    "plan": {...}
  }
}
```

### workflow_state.json (Dynamic Sequence)

```json
{
  "user_plan_id": "uuid",
  "requests": ["cheaper hotel", "upscale restaurant"],
  "detected_subagents": ["accommodation", "activities", "verification"],
  "current_step": 1,
  "steps": ["accommodation", "activities", "verification"],
  "completed_steps": ["accommodation"],
  "status": "in_progress",
  "started_at": "2025-01-15T10:00:00Z",
  "history": [
    {
      "step": "accommodation",
      "message": "Found 3 cheaper alternatives",
      "completed_at": "2025-01-15T10:05:00Z",
      "supabase_updated": true
    }
  ]
}
```

### change_log (Appended on Each Revision)

```json
[
  {
    "revision_id": "uuid",
    "timestamp": "2025-01-15T10:10:00Z",
    "requests": [
      "I want a cheaper hotel",
      "I want a more upscale restaurant for Saturday dinner"
    ],
    "changes": {
      "accommodation": {
        "previous": "Hotel Hermitage (€850/night)",
        "new": "Hotel Ambassador (€450/night)",
        "reason": "50% cost reduction while maintaining 4-star rating"
      },
      "activities": {
        "added": ["Le Louis XV - Alain Ducasse"],
        "removed": ["Café de Paris"],
        "reason": "Upgraded to Michelin 3-star restaurant per request"
      }
    },
    "subagents_invoked": ["accommodation", "activities", "verification"]
  }
]
```

### plan (Regenerated After Each Revision)

```json
{
  "days": [
    {
      "date": "2025-05-23",
      "day_label": "Day 1 - Arrival",
      "items": [
        {
          "time": "14:00",
          "type": "transportation",
          "title": "Arrive Nice Airport",
          "details": "Flight AF1234 from Paris CDG"
        },
        {
          "time": "15:30",
          "type": "transportation",
          "title": "Transfer to Monaco",
          "details": "Helicopter transfer (7 min)"
        },
        {
          "time": "16:00",
          "type": "accommodation",
          "title": "Check-in Hotel Ambassador",
          "details": "Deluxe room, sea view",
          "revision_note": "Changed from Hotel Hermitage per cost reduction request"
        },
        {
          "time": "20:00",
          "type": "activity",
          "title": "Dinner at Le Louis XV",
          "details": "Michelin 3-star, reservation confirmed",
          "revision_note": "Upgraded from Café de Paris per upscale dining request"
        }
      ]
    }
  ],
  "summary": {
    "total_days": 3,
    "accommodations": 1,
    "activities": 8,
    "transfers": 4
  },
  "last_revised": "2025-01-15T10:10:00Z"
}
```

---

## Key Differences from Planning Agent

| Aspect | Planning Agent | Revision Agent |
|--------|---------------|----------------|
| Input | `{user_id, occasion_id}` | `{user_plan_id, requests}` |
| Starting Data | Fresh start | Existing user_plan data |
| Subagent Sequence | Fixed: trans → accom → activ → verif | Dynamic based on requests |
| Transportation | Live Duffel search | Live Duffel search (if requested) |
| Accommodation | Select from masterlist | Select alternatives from masterlist |
| Activities | Select from masterlist | Select alternatives from masterlist |
| Output | Create new user_plan | Update existing user_plan |
| change_log | Initial empty | Append revision entry |

---

## Request Analysis Examples

### Example 1: Single Domain
**Input:** `"I want a cheaper hotel"`

**Analysis:**
- Keywords detected: "hotel", "cheaper"
- Subagents: `["accommodation", "verification"]`

### Example 2: Multiple Domains
**Input:** `["I want a direct flight", "Add some museum tours"]`

**Analysis:**
- Request 1 keywords: "flight", "direct" → transportation
- Request 2 keywords: "museum", "tours" → activities
- Subagents: `["transportation", "activities", "verification"]`

### Example 3: Ambiguous
**Input:** `"I want something closer to the venue"`

**Analysis:**
- Keywords: "closer" (location-related)
- Could affect: accommodation (hotel location) OR activities (restaurant location)
- Subagents: `["accommodation", "activities", "verification"]` (run both)

### Example 4: Price Without Domain
**Input:** `"Make it cheaper overall"`

**Analysis:**
- Keywords: "cheaper" (price-related, no specific domain)
- Affects all: transportation + accommodation + activities
- Subagents: `["transportation", "accommodation", "activities", "verification"]`

---

## Environment Variables Required

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_service_role_key

# Duffel (Flights + Hotels)
DUFFEL_API_KEY=duffel_live_xxx

# Google Maps (Places)
GOOGLE_MAPS_API_KEY=AIzaSyxxx
```

---

## Key Principles

1. **Request analysis is CRITICAL** - determines which subagents run
2. **Existing data as baseline** - never start from scratch
3. **Progressive updates** - UPDATE Supabase after each subagent completes
4. **Always update plan** - regenerate day-by-day itinerary after revisions
5. **Always update change_log** - append revision entry with details
6. **Verification always runs** - ensure consistency after any changes
7. **Use masterlists** - accommodation and activities come from occasion data
8. **Live search only when needed** - transportation may need fresh Duffel search
