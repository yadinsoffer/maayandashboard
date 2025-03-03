#!/usr/bin/env python3
import requests
import json
import sys
import argparse
# adding another word
# Default API configuration for local testing
LOCAL_API_URL = "http://localhost:5001"
EC2_API_URL = "http://ec2-100-27-189-61.compute-1.amazonaws.com:5001"
API_KEY = "maayan-dashboard-secure-api-key-2024"

def test_update_dashboard(api_url):
    """Test the update-dashboard endpoint"""
    print(f"Testing update-dashboard endpoint on {api_url}...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.post(f"{api_url}/api/update-dashboard", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_validate_key(api_url):
    """Test the validate-key endpoint"""
    print(f"\nTesting validate-key endpoint on {api_url}...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Use a valid key for validation
    data = {
        "key": "eyJ0b2tlbiI6ImV5SmhiR2NpT2lKSVV6VXhNaUo5LmV5SnpkV0lpT2lJeE1USTRNemt3SWl3aVlYVjBhQ0k2SWxKUFRFVmZWVk5GVWl4U1QweEZYMUJCVWxST1JWSmZRVVJOU1U0c1VrOU1SVjlRUVZKVVRrVlNYMEpCVTBsRElpd2ljSEowYm5JaU9pSXhNRFExSWl3aVpYaHdJam94TnpRd05UTXlNVFEwZlEuSEpIU09qbGJIT2xfRm1uLUtRMXg4cFV3VTBKM0huQVFJeFlOTi1TQ29INWEwbVNGSFFYdG1GX04xcE9yYVMzMjYwdmNrSnVlLTN3bTctU3NQTk9oMWciLCJyZWZyZXNoVG9rZW4iOiJkZWRjNWZlMWUxMTk0NTRjYjdjOWY5ZGJjYjYzMjhlZSJ9.DtlpP7c0S0XGGAdFOMmwfE5FabZ1lUzV3S19NfZ125Y"
    }
    
    try:
        response = requests.post(f"{api_url}/api/validate-key", headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test the API endpoints')
    parser.add_argument('--ec2', action='store_true', help='Test against EC2 instance instead of local server')
    args = parser.parse_args()
    
    # Determine which API URL to use
    api_url = EC2_API_URL if args.ec2 else LOCAL_API_URL
    
    print("API Endpoint Testing")
    print("===================")
    print(f"Testing against: {api_url}")
    print()
    
    # Test the update-dashboard endpoint
    update_success = test_update_dashboard(api_url)
    
    # Test the validate-key endpoint
    validate_success = test_validate_key(api_url)
    
    # Print summary
    print("\nTest Summary")
    print("===========")
    print(f"Update Dashboard: {'SUCCESS' if update_success else 'FAILED'}")
    print(f"Validate Key: {'SUCCESS' if validate_success else 'FAILED'}")
    
    # Exit with appropriate status code
    sys.exit(0 if update_success and validate_success else 1) 