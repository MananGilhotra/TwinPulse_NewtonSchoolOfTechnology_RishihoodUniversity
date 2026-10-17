#!/usr/bin/env bash
# One command to run TwinPulse: sets up Python + the dashboard, then serves everything on http://localhost:8000
set -euo pipefail
cd "$(dirname "$0")"

PY=${PYTHON:-python3.12}
if [ ! -d .venv ]; then
  echo "Creating Python environment (.venv)…"
  "$PY" -m venv .venv
  .venv/bin/pip install -q --upgrade pip
  .venv/bin/pip install -q -r requirements.txt
fi

if [ ! -f dashboard/dist/index.html ]; then
  echo "Building the dashboard…"
  (cd dashboard && npm install --silent && npm run build --silent)
fi

echo "TwinPulse is starting on http://localhost:8000  (Ctrl+C to stop)"
exec .venv/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
