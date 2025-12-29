# Place Photos (New) API Documentation

## Overview

The Place Photos (New) service provides read-only access to millions of high-quality photos stored in the Places database. "Place Photos (New) gives you access to the millions of photos stored in the Places database."

Photos are obtained through Place Details (New), Nearby Search (New), or Text Search (New) requests, then accessed via the Place Photo service for resizing and retrieval.

## Request Format

Place Photos (New) requests use HTTP GET with the following structure:

```
https://places.googleapis.com/v1/NAME/media?key=API_KEY&PARAMETERS
```

## Required Parameters

### Photo Name
A unique string identifier returned in the `photos` array from Place Details, Nearby Search, or Text Search responses. Format:
```
places/PLACE_ID/photos/PHOTO_RESOURCE
```

**Important:** "You cannot cache a photo name. Also, the name can expire." Always retrieve fresh names from recent API responses.

### Image Dimensions
Specify maximum dimensions in pixels using:
- `maxHeightPx` — Height (1-4800 pixels)
- `maxWidthPx` — Width (1-4800 pixels)

At least one parameter is required. "If the image is smaller than the values specified, the original image will be returned."

## Optional Parameters

### skipHttpRedirect
- `false` (default) — Returns HTTP redirect to image
- `true` — Returns JSON response with image details

Example JSON response:
```json
{
  "name": "places/ChIJj61dQgK6j4AR4GeTYWZsKWw/photos/Aaw_FcKly...",
  "photoUri": "https://lh3.googleusercontent.com/..."
}
```

## Getting Photo Names

Photo information from Place Details includes:
- `name` — Resource identifier for Photo requests
- `heightPx` — Maximum image height
- `widthPx` — Maximum image width
- `authorAttributions[]` — Required attribution details

Example Place Details request including photos:
```bash
curl -X GET \
-H 'Content-Type: application/json' \
-H "X-Goog-Api-Key: API_KEY" \
-H "X-Goog-FieldMask: id,displayName,photos" \
https://places.googleapis.com/v1/places/ChIJ2fzCmcW7j4AR2JzfXBBoh6E
```

Sample `photos` array response:
```json
"photos": [
  {
    "name": "places/ChIJ2fzCmcW7j4AR2JzfXBBoh6E/photos/AUacShh3_Dd8...",
    "widthPx": 6000,
    "heightPx": 4000,
    "authorAttributions": [
      {
        "displayName": "John Smith",
        "uri": "//maps.google.com/maps/contrib/101563",
        "photoUri": "//lh3.googleusercontent.com/..."
      }
    ]
  }
]
```

## Example Request

```
https://places.googleapis.com/v1/places/ChIJ2fzCmcW7j4AR2JzfXBBoh6E/photos/ATKogpeivkIjQ1FT7Qm.../media?maxHeightPx=400&maxWidthPx=400&key=API_KEY
```

Response: Direct image file (JPEG, PNG, GIF formats supported)

## Attribution Requirements

When displaying photos, include any attributions from the `authorAttributions` field. "if the returned photo element includes a value in the authorAttributions field, you must include the additional attribution in your application wherever you display the image."

## Error Codes

| Status | Issue | Solution |
|--------|-------|----------|
| 403 | Quota exceeded | Contact support for increase |
| 400 | Invalid request | Verify photo name format, include dimension parameters, ensure name not expired |
| 429 | Too many requests | Load photos on-demand; contact support for quota increase |

## Best Practices

- Retrieve photo names from fresh API responses only
- Load photos on-demand rather than all at once
- Include required attributions when displaying images
- Use field masks (`photos` or `places.photos`) to include photo data in responses
