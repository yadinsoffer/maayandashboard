#!/bin/bash

# Set variables
EC2_HOST="ec2-100-27-189-61.compute-1.amazonaws.com"
PEM_FILE="maayandashboard.pem"
REMOTE_DIR="/home/ubuntu/maayandashboard"

# Ensure PEM file has correct permissions
chmod 400 $PEM_FILE

# Create remote directory
ssh -i $PEM_FILE ubuntu@$EC2_HOST "mkdir -p $REMOTE_DIR"

# Copy files to EC2 (excluding venv and other unnecessary files)
rsync -avz --exclude 'venv' \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'deploy.sh' \
    -e "ssh -i $PEM_FILE" \
    ./ ubuntu@$EC2_HOST:$REMOTE_DIR/

# SSH into the instance and set up the environment
ssh -i $PEM_FILE ubuntu@$EC2_HOST "cd $REMOTE_DIR && \
    sudo apt-get update && \
    sudo apt-get install -y python3-pip python3-venv && \
    python3 -m venv venv && \
    source venv/bin/activate && \
    pip install -r requirements.txt && \
    # Set up cron job
    (crontab -l 2>/dev/null; echo '0 0 * * 0 cd /home/ubuntu/maayandashboard && source /home/ubuntu/maayandashboard/venv/bin/activate && python3 /home/ubuntu/maayandashboard/src/main.py >> /home/ubuntu/maayandashboard/cron.log 2>&1') | crontab -" 
