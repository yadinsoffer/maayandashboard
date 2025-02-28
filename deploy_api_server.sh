#!/bin/bash

# This script deploys the API server files to the EC2 instance

# EC2 instance details
EC2_USER="ubuntu"
EC2_HOST="ec2-100-27-189-61.compute-1.amazonaws.com"
EC2_KEY_PATH="maayandashboard.pem"
REMOTE_DIR="/home/ubuntu/maayandashboard"

# Make sure the key file has the right permissions
chmod 400 $EC2_KEY_PATH

# Create necessary directories on the EC2 instance
ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST "mkdir -p $REMOTE_DIR/src/collectors"

# Copy the API server files
scp -i $EC2_KEY_PATH src/api_server.py $EC2_USER@$EC2_HOST:$REMOTE_DIR/src/
scp -i $EC2_KEY_PATH src/run_update.py $EC2_USER@$EC2_HOST:$REMOTE_DIR/src/
scp -i $EC2_KEY_PATH src/start_api_server.sh $EC2_USER@$EC2_HOST:$REMOTE_DIR/src/
scp -i $EC2_KEY_PATH src/.env $EC2_USER@$EC2_HOST:$REMOTE_DIR/src/
scp -i $EC2_KEY_PATH src/collectors/bucketlister.py $EC2_USER@$EC2_HOST:$REMOTE_DIR/src/collectors/

# Copy the deploy.sh script
scp -i $EC2_KEY_PATH deploy.sh $EC2_USER@$EC2_HOST:$REMOTE_DIR/

# Copy the systemd service file
scp -i $EC2_KEY_PATH dashboard-api.service $EC2_USER@$EC2_HOST:/tmp/
ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST "sudo mv /tmp/dashboard-api.service /etc/systemd/system/"

# Make scripts executable
ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST "chmod +x $REMOTE_DIR/src/start_api_server.sh $REMOTE_DIR/src/run_update.py $REMOTE_DIR/deploy.sh"

# Install required packages
ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST "sudo apt-get update && sudo apt-get install -y python3-pip python3-venv"
ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST "cd $REMOTE_DIR && pip3 install flask flask-cors python-dotenv requests"

# Enable and start the service
ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST "sudo systemctl daemon-reload && sudo systemctl enable dashboard-api && sudo systemctl restart dashboard-api"

# Check service status
ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST "sudo systemctl status dashboard-api"

echo "Deployment completed!" 
