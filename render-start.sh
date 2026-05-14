#!/usr/bin/env bash
set -euo pipefail

# Delegate to the backend start script so Render can call this from the repo root.
cd backend
exec bash render-start.sh "$@"