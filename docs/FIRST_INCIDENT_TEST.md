# First Incident Test

This guide explains how to run the Hermes ServiceNow capability against a
ServiceNow Developer Instance and create the first incident.

## Required Environment Variables

| Variable | Purpose |
|---|---|
| `SERVICENOW_INSTANCE_URL` | Base URL of the ServiceNow instance |
| `SERVICENOW_USERNAME` | Username for basic authentication |
| `SERVICENOW_PASSWORD` | Password for basic authentication |

Optional variables:

| Variable | Purpose |
|---|---|
| `SERVICENOW_AUTHENTICATION_TYPE` | Defaults to `basic` |
| `SERVICENOW_ACCESS_TOKEN` | Token-based auth support |
| `SERVICENOW_TIMEOUT` | Request timeout in seconds |
| `SERVICENOW_VERIFY_SSL` | SSL verification toggle |

## How to Execute

1. Set the required environment variables.
2. Run the smoke test:

```bash
python scripts/test_create_incident.py
```

## Expected Output

```text
Success: True
Incident Number: INC...
sys_id: ...
Execution Message: Incident creation completed.
```

## Common Errors

| Error | Likely Cause |
|---|---|
| `instance_url is required` | Missing `SERVICENOW_INSTANCE_URL` |
| `Basic authentication requires username and password` | Missing credentials |
| `Invalid ServiceNow instance_url` | URL is malformed or missing scheme |
| `Incident creation failed` | Table executor or client transport failure |
| `ExecutionResult.sys_id is required for verification` | ServiceNow response did not return the required identifiers |

## Troubleshooting

- Confirm the developer instance URL includes `https://`.
- Verify the user has permission to create incidents.
- Ensure the instance is reachable from the machine running the script.
- Start with `SERVICENOW_VERIFY_SSL=true`; only disable SSL verification for local testing.
- If the script fails during transport, review the structured error message and
  re-run after correcting the environment variables.

