# Execution Trace Schema

## Purpose

This document describes the early-stage minimal execution trace schema used by
the current reference implementation surface. It supports the existing demo
shape while allowing a small amount of additional trace metadata.

## Required fields

- `status`
- `trace`

## Optional fields

- `metadata`
- `events`

## Minimal example payload

```json
{
  "status": "completed",
  "trace": [
    "persona loaded",
    "agent action executed",
    "audit evidence generated"
  ],
  "metadata": {
    "framework": "minimal-local"
  }
}
```

## Notes / compatibility scope

- This is an early-stage minimal schema.
- It is intended to support the current reference implementation in this
  repository.
- It is not a final standard, complete runtime trace model, or production audit
  format.
- The `events` field is optional and exists only for implementations that need a
  richer event view than the compact `trace` array.
