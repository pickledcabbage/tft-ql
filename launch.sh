#!/bin/bash

# Terminate existing screens if running
./stop.sh

# Sync config files
python scripts/sync_config.py

# Start frontend in a screen session
screen -dmS ql_frontend bash -c "cd frontend/tft-frontend && npm start"

# Start backend in a screen session
screen -dmS ql_backend bash -c "poetry run python tft/interpreter/server.py"

echo "Started screens: ql_frontend, ql_backend"
echo "Use 'screen -r ql_frontend' or 'screen -r ql_backend' to attach"
