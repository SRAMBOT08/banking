# Payload Builder Design

## Purpose

The payload builder is a pure transformation layer that converts internal
`IncidentRequest` objects into normalized `IncidentPayload` objects.

It exists so later layers can work with a stable ServiceNow-shaped payload
without embedding mapping rules inside the executor or pipeline.

## Inputs

| Input | Description |
|---|---|
| `IncidentRequest` | Internal business request produced by the planner |

## Outputs

| Output | Description |
|---|---|
| `IncidentPayload` | Normalized payload ready for the table executor |

## Transformation Rules

- `short_description` and `description` are preserved as trimmed text.
- `priority`, `urgency`, `impact`, and `category` are normalized to stable
  string values.
- `assignment_group` remains human-readable and is not resolved to `sys_id`.
- `caller` remains human-readable and is not resolved to `sys_id`.
- No network access is performed.
- No lookup-based enrichment is performed.
- No execution or persistence occurs here.

## Future Integration with Reference Resolver

Future reference resolution should be implemented outside this module.

Likely future responsibilities:

- convert `assignment_group` display values into ServiceNow references
- resolve `caller` into a ServiceNow user reference
- enrich payloads with lookup-backed identifiers when required

The payload builder should remain unchanged and continue to produce only the
normalized, lookup-free payload.

