# Developer Setup Guide

## 1. Clone Repository

```bash
git clone <repository-url>
cd hermes-agent
```

## 2. Install uv

Hermes expects `uv` for reproducible Python environment management.

- macOS/Linux: follow the Hermes install instructions or install `uv` directly from Astral
- Windows: use the Hermes installer or ensure `uv.exe` is on PATH

Verify:

```bash
uv --version
```

## 3. Create Virtual Environment

```bash
uv venv .venv --python 3.13
source .venv/bin/activate
```

## 4. Install Dependencies

Install the repository dependencies from `pyproject.toml` and `uv.lock`:

```bash
uv sync --locked
```

If you are setting up the full developer stack:

```bash
uv pip install -e ".[all,dev]"
```

## 5. Configure .env

Copy the example file and fill in your ServiceNow credentials:

```bash
cp .env.example .env
```

Set at minimum:

```bash
SERVICENOW_INSTANCE_URL=https://<your-instance>.service-now.com
SERVICENOW_USERNAME=<your-username>
SERVICENOW_PASSWORD=<your-password>
```

## 6. Run Environment Validation

```bash
python scripts/check_environment.py
```

You want to see `Overall: PASS`.

## 7. Run Smoke Test

```bash
python scripts/test_create_incident.py
```

## 8. Expected Successful Output

When everything is configured correctly, the script should print:

- `Success: True`
- `Incident Number: ...`
- `sys_id: ...`
- `Execution Message: ...`

## 9. Troubleshooting

### Missing `uv`

Install `uv` first, then rerun the setup script.

### Missing Python Packages

If `requests`, `httpx`, `yaml`, or `dotenv` are missing, the virtual environment has not been synced correctly.

Run:

```bash
uv sync --locked
```

### Missing ServiceNow Variables

If the environment checker reports missing credentials, update `.env` or export the variables in your shell.

### Invalid ServiceNow URL

Ensure the instance URL includes the scheme:

```bash
https://<your-instance>.service-now.com
```

### Smoke Test Import Failure

If the smoke test fails before request execution, it usually indicates a missing dependency or a Python environment mismatch.

### Authentication Failure

Check the username/password pair and confirm the developer instance is reachable.

