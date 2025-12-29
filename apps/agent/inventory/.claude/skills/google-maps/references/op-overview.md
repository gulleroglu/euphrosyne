# About the Places API (New)

## Overview

The Places API (New) is a comprehensive suite of web services providing detailed place information, photos, search capabilities, and autocomplete functionality. It includes five main components:

- **Place Details (New)**
- **Place Photos (New)**
- **Nearby Search (New)**
- **Text Search (New)**
- **Autocomplete (New)**

## Core APIs

### Place Details (New)

This endpoint retrieves comprehensive information about a specific location using its Place ID. A Place ID uniquely identifies establishments and points of interest in Google's database.

**When to use:** Calling Place Details is more cost-effective than search APIs when you already possess a Place ID.

**Information returned:** Complete address, phone number, user ratings, and reviews.

**Ways to obtain a Place ID:**
- Text Search (New)
- Nearby Search (New)
- Geocoding API
- Routes API
- Address Validation API
- Autocomplete (New)

### Place Photos (New)

Grants access to millions of high-quality photographs from Google's Places database. Photos can be resized for optimal application integration.

**Requirements:** Each request needs a photo resource name, which identifies the specific image to retrieve.

**How to get photo resource names:** Include photos in the field mask when calling:
- Place Details (New)
- Text Search (New)
- Nearby Search (New)

### Text Search (New) and Nearby Search (New)

**Text Search (New):**
Searches using arbitrary text strings. Example queries: "Spicy Vegetarian Food in Sydney, Australia" or "Fine seafood dining near Palo Alto, CA."

Refinement options include price levels, opening status, ratings, and place types. Results can be location-biased or location-restricted.

**Nearby Search (New):**
Searches a specified geographic region by defining a circle (latitude, longitude center point, and radius in meters) and specifying one or more place types.

Example use case: Search for pizza restaurants within shopping malls in a specified region.

### Autocomplete (New)

A web service returning place and query predictions as users type. Functionality requires:
- Text search string
- Geographic bounds controlling search area

**Session tokens** group autocomplete queries and selections into discrete sessions for billing purposes. These user-generated strings track interactions and manage costs.

## Enhanced Data Fields

### New Information Fields

| Field | Purpose |
|-------|---------|
| `regularSecondaryOpeningHours` | Specialized operation times (drive-through, delivery hours) |
| `paymentOptions` | Accepted payment methods (credit card, debit, cash, NFC) |
| `parkingOptions` | Available parking types (free/paid lots, street, valet, garage) |
| `subDestinations` | Related unique places (airport terminals of an airport) |
| `fuelOptions` | Gas station fuel availability (diesel, unleaded, premium, EV) |
| `evChargeOptions` | Number of available EV chargers |
| `shortFormattedAddress` | Brief human-readable address |
| `primaryType` | Primary classification (cafe, airport) |
| `primaryTypeDisplayName` | Localized display name of primary type |

### New Attributes

Amenity and service indicators: outdoor seating, live music, children's menu, cocktails, dessert service, coffee service, child-friendly status, dog-friendly policy, restroom availability, group accommodation, and sports-viewing suitability.

### Accessibility Options

- Wheelchair-accessible parking
- Wheelchair-accessible entrance
- Wheelchair-accessible restroom
- Wheelchair-accessible seating

## AI-Powered Summaries

Leveraging Gemini model capabilities, these summaries synthesize diverse data sources to help users make informed decisions.

**Available summary types:**
- **Place summaries:** Short overview of specific locations
- **Review summaries:** Digestible synthesis of user reviews
- **Area summaries:** Neighborhood overviews and EV charging station information

**Requirement:** All AI-powered summaries displayed in applications must include proper attribution per Google policies.
