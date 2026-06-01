# API Contract

## Endpoints

### GET /crimes
Returns a paginated list of crimes.

### GET /crimes/search
Search crimes by date range, borough, and crime type.

### GET /stats
Returns global dashboard statistics.

### GET /heatmap
Returns aggregated geographic data for map visualization.

### GET /prediction
Returns crime forecast results.

## Crime object schema

```json
{
  "id": 1,
  "date": "YYYY-MM-DD",
  "borough": "string",
  "crime_type": "string",
  "latitude": 40.7128,
  "longitude": -74.006
}
```
