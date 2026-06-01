# Data Contract

This document defines the canonical crime record used across backend, frontend, notebooks, and ML workflows.

## Required fields

- id: number
- date: YYYY-MM-DD
- borough: string
- crime_type: string
- latitude: number
- longitude: number

## Validation rules

- `id` must be unique.
- `date` must be a valid ISO date.
- `borough` should use normalized borough names.
- `crime_type` should be a normalized categorical label.
- `latitude` and `longitude` must represent a valid NYC coordinate pair.
