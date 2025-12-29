# Place Data Fields (New) - Google Places API

## Overview

Place data fields define the information returned in responses from Place Details, Text Search, and Nearby Search endpoints. Developers must specify at least one field in the field mask when making requests, or the call will return an error.

## Key Information

- Fields are organized by pricing tier (SKU) and availability across Basic, Contact, Atmosphere, and Accessibility categories
- The documentation covers platform-specific implementations for Android, iOS, JavaScript, and Web Service integrations
- "Place data fields define the place data to return in the response" for various search operations

## Place Data Fields by Pricing Tier

### Essential Tier Fields
- `name`, `id`, `attributions`, `photos`
- `location`, `formattedAddress`, `shortFormattedAddress`
- `viewport`, `plusCode`, `postalAddress`
- `types`, `addressComponents`, `addressDescriptor`, `adrFormatAddress`

### Pro Tier Fields
- `displayName`, `businessStatus`, `containingPlaces`
- `googleMapsLinks`, `googleMapsUri`
- `iconBackgroundColor`, `iconMaskBaseUri`
- `primaryType`, `primaryTypeDisplayName`
- `pureServiceAreaBusiness`, `utcOffsetMinutes`
- `subDestinations`

### Enterprise Tier Fields
- `currentOpeningHours`, `currentSecondaryOpeningHours`
- `regularOpeningHours`, `regularSecondaryOpeningHours`
- `internationalPhoneNumber`, `nationalPhoneNumber`
- `priceLevel`, `priceRange`
- `rating`, `userRatingCount`, `websiteUri`

### Enterprise + Atmosphere Tier Fields
- Accessibility and amenity features: `accessibilityOptions`
- Dining options: `servesBreakfast`, `servesBrunch`, `servesLunch`, `servesDinner`, `servesCoffee`, `servesWine`, `servesBeer`, `servesCocktails`, `servesDessert`, `servesVegetarianFood`
- Facilities: `allowsDogs`, `curbsidePickup`, `delivery`, `dineIn`, `outdoorSeating`, `restroom`, `takeout`, `reservable`
- Parking, payment, and parking options
- EV and fuel options: `evChargeOptions`, `evChargeAmenitySummary`, `fuelOptions`
- Entertainment and atmosphere: `liveMusic`, `goodForChildren`, `goodForGroups`, `goodForWatchingSports`
- Reviews and summaries: `reviews`, `reviewSummary`, `editorialSummary`
- AI-powered features: `generativeSummary`, `neighborhoodSummary`, `routingSummaries`
