#!/bin/bash

# EC2 instance details
EC2_USER="ubuntu"
EC2_HOST="ec2-100-27-189-61.compute-1.amazonaws.com"
EC2_KEY_PATH="maayandashboard.pem"
REMOTE_DIR="/home/ubuntu/maayandashboard"

# Make sure the key file has the right permissions
chmod 400 $EC2_KEY_PATH

# Copy the updated run_update.py file
scp -i $EC2_KEY_PATH src/run_update.py $EC2_USER@$EC2_HOST:$REMOTE_DIR/src/

echo "Deployment of updated run_update.py completed!" 