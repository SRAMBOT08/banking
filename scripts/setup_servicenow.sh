#!/usr/bin/env bash
# Prepare a local Hermes environment for ServiceNow incident testing.
#
# This script is intentionally conservative:
# - it does not overwrite existing files
# - it does not create credentials
# - it only prepares a reproducible Python environment and validates the
#   ServiceNow-related dependencies needed by the smoke test

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$REPO_ROOT/.venv"

log() {
  printf '%s\n' "$*"
}

fail() {
  log "error: $*"
  exit 1
}

if ! command -v uv >/dev/null 2>&1; then
  fail "uv is not installed or not on PATH. Install uv first, then rerun this script."
fi

PYTHON_VERSION="${HERMES_PYTHON_VERSION:-3.13}"

if [ ! -d "$VENV_DIR" ]; then
  log "Creating virtual environment at $VENV_DIR"
  uv venv "$VENV_DIR" --python "$PYTHON_VERSION"
else
  log "Virtual environment already exists at $VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

log "Installing Hermes dependencies from pyproject.toml / uv.lock"
uv sync --locked

log "Verifying required packages"
python - <<'PY'
import importlib
required = ["requests", "httpx", "yaml", "dotenv"]
missing = []
for name in required:
    try:
        importlib.import_module(name)
        print(f"OK  {name}")
    except Exception as exc:
        print(f"MISS {name}: {exc}")
        missing.append(name)

if missing:
    raise SystemExit(f"Missing required packages: {', '.join(missing)}")
PY

log ""
log "Environment preparation complete."
log "Next:"
log "  1. Copy .env.example to .env"
log "  2. Set SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, SERVICENOW_PASSWORD"
log "  3. Run: python scripts/check_environment.py"
log "  4. Run: python scripts/test_create_incident.py"

