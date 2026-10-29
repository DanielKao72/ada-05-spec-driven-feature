#!/usr/bin/env bash
# Single verification contract shared by humans, coding agents and CI.
set -euo pipefail

cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-python}"

echo "[1/2] Running tests"
"$PYTHON" -m pytest -q

echo "[2/2] Repository contract checks"
"$PYTHON" scripts/check_repo_contract.py

echo "VERIFY_REPO: PASS"
