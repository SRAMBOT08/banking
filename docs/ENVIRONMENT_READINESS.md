# Environment Readiness Report

## Summary

The local environment is **not ready yet** for the first live ServiceNow execution.

The main blockers are:

- No active Hermes virtual environment
- `uv` is not installed on the current PATH
- Required Python packages are missing from the active interpreter
- Required ServiceNow environment variables are not set

## 1. Python Environment

| Item | Status | Details |
|---|---|---|
| Python interpreter | Present | `/usr/local/bin/python3` |
| Python version | Present | `Python 3.13.0` |
| Active virtual environment | Not active | `VIRTUAL_ENV` is unset and `sys.prefix == sys.base_prefix` |
| Hermes project venv | Not detected | No `.venv/` or `venv/` exists in the repository root |
| Package manager expected by Hermes | `uv` | The repository docs and install scripts use `uv sync` / `uv pip install` |
| Authoritative dependency file | `pyproject.toml` + `uv.lock` | `pyproject.toml` defines the runtime dependencies; `uv.lock` pins the resolved set |

## 2. Dependency Status

### Checked Packages

| Package | Status | Why it matters |
|---|---|---|
| `requests` | Missing | Required by `plugins/servicenow_pipeline/servicenow_client.py` |
| `httpx` | Missing | Required elsewhere in Hermes runtime and commonly expected in the active install |
| `PyYAML` (`yaml`) | Missing | Required by Hermes plugin/config loading paths |
| `python-dotenv` (`dotenv`) | Installed | Used by the smoke script to load environment variables |

### ServiceNow Capability Dependencies

The ServiceNow capability currently relies on:

- `requests`
- `python-dotenv`
- `PyYAML` for surrounding Hermes plugin/config loading
- `httpx` for the broader Hermes runtime environment

The ServiceNow smoke test failed at import time because `requests` was not installed in the active interpreter.

## 3. Environment Variables

| Variable | Status | Notes |
|---|---|---|
| `SERVICENOW_INSTANCE_URL` | Missing | Must point to the ServiceNow developer instance, for example `https://<instance>.service-now.com` |
| `SERVICENOW_USERNAME` | Missing | Required for basic authentication |
| `SERVICENOW_PASSWORD` | Missing | Required for basic authentication |

## 4. Smoke Test Review

File reviewed:

- [`scripts/test_create_incident.py`](/Users/user/hermes/hermes-agent/scripts/test_create_incident.py)

### Observations

- It correctly loads `.env` from the repository root and `~/.hermes/.env` via `python-dotenv`.
- It composes the ServiceNow capability using the ServiceNow client, table executor, payload builder, incident service, and verifier.
- It fails before any incident creation when the environment is missing dependencies.
- It would benefit from a slightly earlier validation message for missing ServiceNow credentials, but the current behavior is acceptable for a smoke test.

## 5. Installation Commands

### Preferred Hermes Path

The repository’s documented path uses `uv`:

```bash
uv venv .venv --python 3.13
source .venv/bin/activate
uv sync --locked
```

If you want the full developer stack used by Hermes, the README also documents:

```bash
uv pip install -e ".[all,dev]"
```

### If `uv` Is Not Installed

Install `uv` first using the Hermes-supported installer path for your platform, then rerun the commands above.

If you must use a plain pip-based fallback in a temporary environment, the missing packages are:

```bash
python -m pip install requests httpx pyyaml python-dotenv
```

That fallback is less ideal than the repository’s `uv` workflow because Hermes’ lockfile-driven setup is designed around `uv`.

## 6. Commands Required Before the Next Execution

### Environment Setup Checklist

1. Install or enable `uv`.
2. Create and activate a Hermes virtual environment.
3. Sync dependencies from `pyproject.toml` / `uv.lock`.
4. Set ServiceNow credentials.
5. Re-run the smoke test.

### ServiceNow Credential Setup

If you are using a local `.env` file, add:

```bash
SERVICENOW_INSTANCE_URL=https://<your-instance>.service-now.com
SERVICENOW_USERNAME=<your-username>
SERVICENOW_PASSWORD=<your-password>
```

If you prefer shell exports:

```bash
export SERVICENOW_INSTANCE_URL="https://<your-instance>.service-now.com"
export SERVICENOW_USERNAME="<your-username>"
export SERVICENOW_PASSWORD="<your-password>"
```

The smoke script already supports dotenv loading, so a local `.env` file is the cleanest option when working in this repository.

## 7. Remaining Blockers

- `uv` is not installed on the current PATH.
- No Hermes virtual environment is active.
- Core runtime dependencies are missing from the active Python interpreter.
- ServiceNow environment variables are not configured.

## 8. Recommended Next Steps

1. Install `uv` and create a project virtual environment.
2. Run `uv sync --locked` or `uv pip install -e ".[all,dev]"` in that environment.
3. Create a local `.env` file or export the three ServiceNow variables.
4. Re-run [`scripts/test_create_incident.py`](/Users/user/hermes/hermes-agent/scripts/test_create_incident.py).

## Final Status

❌ Environment is not ready.

### Exact Checklist Before Re-running the Smoke Test

- [ ] `uv` installed and available on PATH
- [ ] Hermes virtual environment created and activated
- [ ] `requests` installed
- [ ] `httpx` installed
- [ ] `PyYAML` installed
- [ ] `python-dotenv` installed
- [ ] `SERVICENOW_INSTANCE_URL` set
- [ ] `SERVICENOW_USERNAME` set
- [ ] `SERVICENOW_PASSWORD` set

