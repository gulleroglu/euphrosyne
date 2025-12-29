# Accommodation Loyalty Programmes API Documentation

## Overview

The Accommodation Loyalty Programmes API provides access to loyalty programme information supported by Duffel Stays. This endpoint enables retrieval of hotel loyalty programmes that can be associated with accommodations and rates.

## Base Endpoint

```
https://api.duffel.com/stays/loyalty_programmes
```

---

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `reference` | enum | Unique identifier for the loyalty programme |
| `name` | string | Display name of the loyalty programme |
| `logo_url_svg` | string | SVG logo asset URL |
| `logo_url_png_small` | string | PNG logo asset URL (transparent) |

---

## Supported References

| Reference | Programme Name |
|-----------|---------------|
| `wyndham_rewards` | Wyndham Rewards |
| `choice_privileges` | Choice Privileges |
| `marriott_bonvoy` | Marriott Bonvoy |
| `best_western_rewards` | Best Western Rewards |
| `world_of_hyatt` | World of Hyatt |
| `hilton_honors` | Hilton Honors |
| `ihg_one_rewards` | IHG One Rewards |
| `leaders_club` | Leaders Club |
| `stash_rewards` | Stash Rewards |
| `omni_select_guest` | Omni Select Guest |
| `i_prefer` | I Prefer |
| `accor_live_limitless` | Accor Live Limitless |
| `my_6` | My 6 |
| `jumeirah_one` | Jumeirah One |
| `global_hotel_alliance_discovery` | GHA Discovery |
| `duffel_hotel_group_rewards` | Duffel Hotel Group Rewards (test only) |

---

## Endpoint

### List Loyalty Programmes

**Method:** `GET`
**Endpoint:** `/stays/loyalty_programmes`

#### Example

```python
import requests

url = "https://api.duffel.com/stays/loyalty_programmes"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
programmes = response.json()["data"]

for prog in programmes:
    print(f"{prog['name']}: {prog['reference']}")
```

#### Response

```json
{
  "data": [
    {
      "reference": "marriott_bonvoy",
      "name": "Marriott Bonvoy",
      "logo_url_svg": "https://assets.duffel.com/img/stays/loyalty-programmes/full-color-logo/marriott_bonvoy-square.svg",
      "logo_url_png_small": "https://assets.duffel.com/img/stays/loyalty-programmes/transparent-logo/marriott_bonvoy.png"
    }
  ]
}
```

---

## Usage Notes

- The `reference` field matches the `supported_loyalty_programme` field on Accommodation and Rate objects
- Use logo URLs to display programme branding in your UI
- Check both accommodation-level and rate-level loyalty support
- Some rates may require loyalty programme membership (`loyalty_programme_required: true`)

