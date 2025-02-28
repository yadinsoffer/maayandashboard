#!/bin/bash

# Change to the project directory
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install required packages if not already installed
pip install -r requirements.txt
pip install flask flask-cors python-dotenv

# Load environment variables
if [ -f "src/.env" ]; then
    export $(grep -v '^#' src/.env | xargs)
fi

# Start the API server
echo "Starting API server on port ${PORT:-5000}..."
python3 src/api_server.py

# Keep the script running
wait 