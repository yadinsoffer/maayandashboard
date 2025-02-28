#!/bin/bash

# Exit on any error
set -e

# Base directory - location of the script
BASE_DIR="/home/ubuntu/maayandashboard"
VENV_DIR="$BASE_DIR/venv"
LOG_DIR="$BASE_DIR/logs"
ENV_FILE="$BASE_DIR/.env"
MAIN_SCRIPT="$BASE_DIR/src/main.py"
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
LOG_FILE="$LOG_DIR/cron_$TIMESTAMP.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Set proper permissions
chmod 755 "$LOG_DIR"

# Start logging
exec 1> >(tee -a "${LOG_FILE}")
exec 2> >(tee -a "${LOG_FILE}" >&2)

echo "=== Starting Maayan Dashboard Cron Job ==="
echo "Timestamp: $(date)"
echo "Log file: ${LOG_FILE}"

# Function to check if environment variable exists
check_env_var() {
    if [ -z "${!1}" ]; then
        echo "Error: Required environment variable $1 is not set"
        exit 1
    fi
}

# Load environment variables
echo "Loading environment variables from $ENV_FILE"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "Error: Environment file not found at $ENV_FILE"
    exit 1
fi

# Verify required environment variables
echo "Verifying environment variables..."
check_env_var "FACEBOOK_ADS_TOKEN"
check_env_var "LUMA_API_KEY"
echo "Environment variables verified successfully"

# Activate virtual environment
echo "Activating virtual environment at $VENV_DIR"
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "Error: Virtual environment not found at $VENV_DIR"
    exit 1
fi

# Set Python path
export PYTHONPATH="$BASE_DIR:$PYTHONPATH"

# Change to the project directory
cd "$BASE_DIR"
echo "Changed to directory: $(pwd)"
echo "Using Python: $(which python3)"
echo "PYTHONPATH: $PYTHONPATH"

echo "=== Running Main Script ==="
python3 "$MAIN_SCRIPT"
echo "=== Main Script Completed ==="

echo "=== Cron Job Finished ==="
echo "Timestamp: $(date)"

# Create a symlink to the latest log
ln -sf "${LOG_FILE}" "$LOG_DIR/cron_latest.log" 
