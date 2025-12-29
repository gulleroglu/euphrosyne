# Choose Fields to Return - Places API

## Overview

When calling Place Details (New), Nearby Search (New), or Text Search (New) methods, you must specify desired fields using a response field mask. As the documentation states: "There is no default list of returned fields. If you omit this list, the methods return an error."

## Why Field Masks Matter

Field masking serves multiple purposes:

- **Cost Reduction**: Requesting only necessary data minimizes billing charges
- **Performance**: "Decreases processing times, so your results are returned with a lower latency"
- **Stability**: Protects against future API changes that add computationally expensive fields
- **Network Efficiency**: Results in smaller response sizes and higher throughput

## Creating Response Field Masks

### Basic Structure

Field masks use comma-separated paths with dot notation:
```
topLevelField[.secondLevelField][.thirdLevelField][...]
```

**Critical rule**: Don't use spaces in field path lists.

### For Nearby Search and Text Search

Since these APIs return an array in the `places` field, start paths with `places`:
```
places.formattedAddress,places.displayName
```

To select nested fields:
```
places.displayName.text
```

### For Place Details

Place Details returns a single object, so omit the top-level wrapper:
```
formattedAddress,displayName
```

## Development vs. Production

The wildcard operator `*` requests all fields but carries important caveats. While acceptable during development, production implementations should specify only required fields. The documentation cautions: "don't use the wildcard (*) response field mask in production. The cost may be higher than expected."

## Field Default Values

Note that when response messages are parsed, fields containing default values may be omitted from responses even if specified in the field mask, per protobuf3 specifications.
