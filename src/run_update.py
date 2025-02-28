#!/usr/bin/env python3
import sys
import os
import subprocess
import json
import traceback
import requests

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import the bucketlister module to test if the key is valid
    from src.collectors.bucketlister import get_bucketlister_data
    
    try:
        # Test if the key is valid by making a request
        data = get_bucketlister_data()
        
        if not data or 'error' in data:
            print("KEY_ERROR: Invalid or expired Bucketlister session key", file=sys.stderr)
            sys.exit(1)
            
    except (json.JSONDecodeError, requests.exceptions.JSONDecodeError):
        # Explicitly catch JSON decode errors and treat them as key errors
        print("KEY_ERROR: Invalid or expired Bucketlister session key (JSON decode error)", file=sys.stderr)
        sys.exit(1)
    
    # First, run the deploy script to ensure the latest code is deployed
    update_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'deploy.sh')
    
    # Run the deploy script
    deploy_result = subprocess.run(['bash', update_script_path], 
                           capture_output=True, 
                           text=True, 
                           check=True)
    
    print(deploy_result.stdout)
    
    # Now run the cron_runner.sh script to collect and calculate data
    print("\n=== Running data collection and calculation ===\n")
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path to the cron_runner.sh script
    cron_runner_path = os.path.join(project_root, 'scripts', 'cron_runner.sh')
    
    # Run the cron_runner.sh script
    main_result = subprocess.run(['bash', cron_runner_path], 
                           capture_output=True, 
                           text=True)
    
    if main_result.returncode == 0:
        print("Data collection and calculation completed successfully!")
        print(main_result.stdout)
    else:
        print("Data collection and calculation failed!")
        print(main_result.stderr)
    
    sys.exit(0)
    
except Exception as e:
    error_message = f"Error running update script: {str(e)}\n{traceback.format_exc()}"
    print(error_message, file=sys.stderr)
    
    # Check if the error is related to the key
    error_str = str(e).lower()
    if any(term in error_str for term in ["401", "unauthorized", "authentication", "jsondecode", "token", "session", "cookie", "login"]):
        print("KEY_ERROR: Invalid or expired Bucketlister session key", file=sys.stderr)
    
    sys.exit(1) 