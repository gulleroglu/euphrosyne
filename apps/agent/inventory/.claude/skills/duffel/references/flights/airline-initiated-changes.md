# Airline-Initiated Changes API Documentation

## Overview

Sometimes there can be changes to your order initiated by the airline, for example a flight being delayed. The API enables tracking and managing these changes through dedicated endpoints.

## Key Concepts

- **Added field**: Contains updated slices following the change with potentially new IDs
- **Removed field**: Contains slices and segments as they existed before the change
- **Action tracking**: Records whether the change was accepted, cancelled, or resulted in order modification

## Schema

### Airline-Initiated Change Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (e.g., `aic_00001876aqC8c5umZmrRds`) |
| `order_id` | string | Associated order identifier |
| `created_at` | datetime | ISO 8601 timestamp of detection |
| `updated_at` | datetime | ISO 8601 timestamp of last update |
| `action_taken` | enum | `"accepted"`, `"cancelled"`, or `"changed"` |
| `action_taken_at` | datetime | ISO 8601 timestamp of action |
| `available_actions` | string[] | `"accept"`, `"cancel"`, `"change"`, `"update"` |
| `added` | list | Updated slices and segments post-change |
| `removed` | list | Original slices and segments pre-change |
| `travel_agent_ticket` | object | Associated ticket if applicable |

---

## Endpoints

### 1. List Airline-Initiated Changes

**Endpoint:** `GET https://api.duffel.com/air/airline_initiated_changes`

**Query Parameters:**
- `order_id` (optional): Filter by specific order ID

**Example:**
```bash
curl -X GET "https://api.duffel.com/air/airline_initiated_changes?order_id=ord_xxx" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Duffel-Version: v2"
```

---

### 2. Accept Airline-Initiated Change

**Endpoint:** `POST https://api.duffel.com/air/airline_initiated_changes/{id}/actions/accept`

**URL Parameters:**
- `id` (required): Change identifier

**Response:** Returns the accepted change with `action_taken: "accepted"`

---

### 3. Update Airline-Initiated Change

**Endpoint:** `PATCH https://api.duffel.com/air/airline_initiated_changes/{id}`

**Availability:** Only for changes Duffel cannot accept automatically

**Request Body:**
```json
{
  "data": {
    "action_taken": "accepted"
  }
}
```

---

## Example Response

```json
{
  "data": {
    "id": "aic_00001876aqC8c5umZmrRds",
    "order_id": "ord_00009hthhsUZ8W4LxQgkjo",
    "created_at": "2020-04-11T15:48:11.642Z",
    "updated_at": "2020-01-17T10:12:14.545Z",
    "action_taken": "accepted",
    "action_taken_at": "2022-01-17T10:12:14.545Z",
    "available_actions": ["accept", "cancel", "change"],
    "added": [...],
    "removed": [...]
  }
}
```

---

## Available Actions

| Action | Description |
|--------|-------------|
| `accept` | Accept the airline's changes |
| `cancel` | Cancel the order |
| `change` | Request different flights |
| `update` | Update passenger details |

---

## Handling Changes

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2"
}

# List changes for an order
url = "https://api.duffel.com/air/airline_initiated_changes"
params = {"order_id": "ord_xxx"}
response = requests.get(url, params=params, headers=headers)
changes = response.json()["data"]

for change in changes:
    print(f"Change ID: {change['id']}")
    print(f"Available actions: {change['available_actions']}")

    # Accept the change if that's the desired action
    if "accept" in change["available_actions"]:
        accept_url = f"{url}/{change['id']}/actions/accept"
        response = requests.post(accept_url, headers=headers)
        print(f"Accepted: {response.json()['data']['action_taken']}")
```

## Implementation Notes

- Manual updates required when orders booked with merchant's IATA number
- Slices and segments may receive new IDs upon change
- Use filtering by `order_id` to retrieve specific order changes
- Consider setting up webhooks to be notified of changes
