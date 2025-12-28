# Inventory Agent - Implementation Plan

## Overview

| Aspect | Detail |
|--------|--------|
| Location | `apps/agent/inventory/` |
| Purpose | Build exhaustive masterlist of accommodations & activities for an occasion |
| Frequency | Quarterly per occasion |
| Input | `occasion_id` |
| Output | UPDATE `occasions.accommodations` and `occasions.activities` |
| Subagents | `accommodation`, `activities` |
| Skills | `orchestrating-workflow`, `duffel`, `google-maps` |

---

## Tables Reference

```sql
occasions:
  id              UUID PRIMARY KEY
  occasion        TEXT           -- "Monaco Grand Prix 2025"
  description     TEXT           -- Context for activity search
  city            TEXT           -- "Monaco"
  country         TEXT           -- "Monaco"
  full_address    TEXT           -- "Circuit de Monaco, Monte Carlo"
  start_date      DATE
  end_date        DATE
  accommodations  JSONB          -- [flat list of hotels]
  activities      JSONB          -- [flat list of activities]
  created_at      TIMESTAMPTZ
  updated_at      TIMESTAMPTZ
```

---

## Architecture

```
INPUT: occasion_id
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  HOOK: workflow_init.py                                     │
│  • Fetch occasion from Supabase                             │
│  • Write occasion_context.json                              │
│  • Initialize workflow_state.json                           │
│  • Invoke orchestrating-workflow                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATING-WORKFLOW (init)                              │
│  • orchestrate.py --init                                    │
│  • Returns: next_step = "accommodation"                     │
│  • Invoke accommodation subagent                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  SUBAGENT: accommodation                                    │
│  • Read occasion_context.json                               │
│  • Use duffel + google-maps skills                          │
│  • Write to files/content/accommodations/                   │
│  • Invoke orchestrating-workflow                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATING-WORKFLOW (after accommodation)               │
│  • orchestrate.py --completed-step accommodation            │
│  • Update workflow_state.json                               │
│  • Returns: next_step = "activities"                        │
│  • Invoke activities subagent                               │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  SUBAGENT: activities                                       │
│  • Read occasion_context.json (including description)       │
│  • Use google-maps skill for multiple categories            │
│  • Write to files/content/activities/                       │
│  • Invoke orchestrating-workflow                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATING-WORKFLOW (after activities - FINAL)          │
│  • orchestrate.py --completed-step activities               │
│  • Compile all results from files/content/                  │
│  • UPDATE occasions SET accommodations=..., activities=...  │
│  • Returns: status = "complete"                             │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
      DONE
```

---

## Directory Structure

```
apps/agent/inventory/
├── .claude/
│   ├── settings.json
│   ├── hooks/
│   │   └── workflow_init.py
│   ├── agents/
│   │   ├── accommodation.md
│   │   └── activities.md
│   └── skills/
│       ├── orchestrating-workflow/
│       │   ├── SKILL.md
│       │   └── scripts/
│       │       └── orchestrate.py
│       ├── duffel/
│       │   ├── SKILL.md
│       │   ├── scripts/
│       │   │   ├── duffel_client.py
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
    │   ├── occasion_context.json
    │   └── workflow_state.json
    └── content/
        ├── accommodations/
        └── activities/
```

---

## Implementation Checklist

### Phase 1: Directory Structure

- [ ] Create `apps/agent/inventory/.claude/` directory
- [ ] Create `apps/agent/inventory/.claude/hooks/` directory
- [ ] Create `apps/agent/inventory/.claude/agents/` directory
- [ ] Create `apps/agent/inventory/.claude/skills/orchestrating-workflow/scripts/` directory
- [ ] Create `apps/agent/inventory/.claude/skills/duffel/scripts/` directory
- [ ] Create `apps/agent/inventory/.claude/skills/duffel/references/` directory
- [ ] Create `apps/agent/inventory/.claude/skills/google-maps/scripts/` directory
- [ ] Create `apps/agent/inventory/.claude/skills/google-maps/references/` directory
- [ ] Create `apps/agent/inventory/files/process/` directory
- [ ] Create `apps/agent/inventory/files/content/accommodations/` directory
- [ ] Create `apps/agent/inventory/files/content/activities/` directory

### Phase 2: Settings & Configuration

- [ ] Create `apps/agent/inventory/.claude/settings.json`
  - [ ] Configure UserPromptSubmit hook
  - [ ] Configure Stop hook
  - [ ] Set permissions for Bash, Skills

### Phase 3: Hook System

- [ ] Create `apps/agent/inventory/.claude/hooks/workflow_init.py`
  - [ ] Parse `occasion_id` from stdin input
  - [ ] Connect to Supabase using environment variables
  - [ ] Fetch occasion row: `SELECT * FROM occasions WHERE id = occasion_id`
  - [ ] Validate occasion exists
  - [ ] Write `files/process/occasion_context.json`
  - [ ] Initialize `files/process/workflow_state.json`
  - [ ] Output message to invoke orchestrating-workflow skill

### Phase 4: Orchestrating-Workflow Skill

- [ ] Create `apps/agent/inventory/.claude/skills/orchestrating-workflow/SKILL.md`
  - [ ] Define sequence: `accommodation → activities`
  - [ ] Document input message formats for each transition
  - [ ] Document Supabase update on completion

- [ ] Create `apps/agent/inventory/.claude/skills/orchestrating-workflow/scripts/orchestrate.py`
  - [ ] Implement `--init` handler
    - [ ] Read occasion_context.json to get occasion_id
    - [ ] Create/update workflow_state.json
    - [ ] Return first step: accommodation
  - [ ] Implement `--completed-step <step>` handler
    - [ ] Update workflow_state.json with completed step
    - [ ] Append to history with timestamp
    - [ ] Determine next step or completion
  - [ ] Implement `--status` handler
  - [ ] Implement Supabase update on final completion
    - [ ] Read all files from `files/content/accommodations/`
    - [ ] Read all files from `files/content/activities/`
    - [ ] Deduplicate and merge into flat lists
    - [ ] UPDATE occasions SET accommodations=..., activities=...

### Phase 5: Duffel Skill (Hotels)

- [ ] Create `apps/agent/inventory/.claude/skills/duffel/SKILL.md`
  - [ ] Focus on hotel search only (no flights)
  - [ ] Document exhaustive search approach (no filters)

- [ ] Create `apps/agent/inventory/.claude/skills/duffel/scripts/duffel_client.py`
  - [ ] Supabase client with auth from environment

- [ ] Create `apps/agent/inventory/.claude/skills/duffel/scripts/search_hotels.py`
  - [ ] Accept location, dates parameters
  - [ ] Search without price/availability constraints
  - [ ] Output flat list format with source tagging

- [ ] Create `apps/agent/inventory/.claude/skills/duffel/references/api.md`

### Phase 6: Google Maps Skill (Places)

- [ ] Create `apps/agent/inventory/.claude/skills/google-maps/SKILL.md`
  - [ ] Focus on place search only (no directions)
  - [ ] Document multi-category search approach

- [ ] Create `apps/agent/inventory/.claude/skills/google-maps/scripts/maps_client.py`
  - [ ] Google Maps client with auth from environment

- [ ] Create `apps/agent/inventory/.claude/skills/google-maps/scripts/search_places.py`
  - [ ] Accept location, category, query parameters
  - [ ] Support multiple place types
  - [ ] Output flat list format with source tagging

- [ ] Create `apps/agent/inventory/.claude/skills/google-maps/references/api.md`

### Phase 7: Subagents

- [ ] Create `apps/agent/inventory/.claude/agents/accommodation.md`
  - [ ] Instructions to read occasion_context.json
  - [ ] Instructions to use duffel skill for hotel search
  - [ ] Instructions to use google-maps skill for lodging places
  - [ ] Instructions to write results to files/content/accommodations/
  - [ ] Instructions to invoke orchestrating-workflow on completion

- [ ] Create `apps/agent/inventory/.claude/agents/activities.md`
  - [ ] Instructions to read occasion_context.json (including description)
  - [ ] Instructions to use google-maps skill for multiple categories:
    - [ ] Restaurants, cafes, bars
    - [ ] Tourist attractions, museums, art galleries
    - [ ] Parks, spas, shopping
    - [ ] Occasion-specific venues (based on description)
  - [ ] Instructions to write results to files/content/activities/
  - [ ] Instructions to invoke orchestrating-workflow on completion

### Phase 8: Testing & Validation

- [ ] Set environment variables:
  - [ ] SUPABASE_URL
  - [ ] SUPABASE_KEY
  - [ ] DUFFEL_API_KEY
  - [ ] GOOGLE_MAPS_API_KEY
- [ ] Create test occasion row in Supabase
- [ ] Run inventory agent with test occasion_id
- [ ] Verify workflow_state.json updates correctly at each step
- [ ] Verify accommodations written to files/content/accommodations/
- [ ] Verify activities written to files/content/activities/
- [ ] Verify Supabase occasions row updated with masterlists
- [ ] Verify flat list format is correct

---

## File Schemas

### occasion_context.json

```json
{
  "id": "uuid",
  "occasion": "Monaco Grand Prix 2025",
  "description": "Formula 1 World Championship race weekend featuring practice, qualifying, and race day. High-end clientele, motorsport enthusiasts, luxury experiences expected.",
  "city": "Monaco",
  "country": "Monaco",
  "full_address": "Circuit de Monaco, Monte Carlo",
  "start_date": "2025-05-23",
  "end_date": "2025-05-25"
}
```

### workflow_state.json

```json
{
  "occasion_id": "uuid",
  "current_step": 1,
  "steps": ["accommodation", "activities"],
  "completed_steps": ["accommodation"],
  "status": "in_progress",
  "started_at": "2025-01-15T10:00:00Z",
  "history": [
    {
      "step": "accommodation",
      "message": "Found 45 hotels from duffel and google-maps",
      "completed_at": "2025-01-15T10:05:00Z"
    }
  ]
}
```

### occasions.accommodations (flat list)

```json
[
  {
    "id": "hotel_abc123",
    "source": "duffel",
    "name": "Hotel Hermitage Monte-Carlo",
    "stars": 5,
    "rating": 4.8,
    "rating_count": 1234,
    "address": "Square Beaumarchais, Monaco",
    "latitude": 43.7384,
    "longitude": 7.4246,
    "amenities": ["pool", "spa", "restaurant"],
    "price_range": null
  }
]
```

### occasions.activities (flat list)

```json
[
  {
    "id": "place_xyz789",
    "source": "google_maps",
    "name": "Café de Paris Monte-Carlo",
    "category": "restaurant",
    "rating": 4.5,
    "rating_count": 2500,
    "address": "Place du Casino, Monaco",
    "latitude": 43.7392,
    "longitude": 7.4277,
    "price_level": 3,
    "types": ["restaurant", "cafe", "food"],
    "occasion_relevance": "luxury dining near casino"
  }
]
```

---

## Environment Variables Required

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_service_role_key

# Duffel (Hotels)
DUFFEL_API_KEY=duffel_live_xxx

# Google Maps (Places)
GOOGLE_MAPS_API_KEY=AIzaSyxxx
```

---

## Key Principles

1. **Orchestrating-workflow is ALWAYS in between steps** - it decides what happens next
2. **No constraints on inventory** - build exhaustive masterlist regardless of price/availability
3. **Use occasion description** - to understand context when searching activities
4. **Flat list format** - simple array of objects, tagged with source
5. **Supabase update at end** - compile all results and update occasions table
