import requests
import re
import os

url = "https://insights.bucketlisters.com/v2/1045/?_data=routes%2Fv2%2F%24partnerId%2Findex"

# Only include the BLT_partner_session cookie
cookies = {
    "BLT_partner_session": "eyJ0b2tlbiI6ImV5SmhiR2NpT2lKSVV6VXhNaUo5LmV5SnpkV0lpT2lJeE1USTRNemt3SWl3aVlYVjBhQ0k2SWxKUFRFVmZWVk5GVWl4U1QweEZYMUJCVWxST1JWSmZRVVJOU1U0c1VrOU1SVjlRUVZKVVRrVlNYMEpCVTBsRElpd2ljSEowYm5JaU9pSXhNRFExSWl3aVpYaHdJam94TnpRd05UTXlNVFEwZlEuSEpIU09qbGJIT2xfRm1uLUtRMXg4cFV3VTBKM0huQVFJeFlOTi1TQ29INWEwbVNGSFFYdG1GX04xcE9yYVMzMjYwdmNrSnVlLTN3bTctU3NQTk9oMWciLCJyZWZyZXNoVG9rZW4iOiJkZWRjNWZlMWUxMTk0NTRjYjdjOWY5ZGJjYjYzMjhlZSJ9.DtlpP7c0S0XGGAdFOMmwfE5FabZ1lUzV3S19NfZ125Y"
}

def get_bucketlister_data():
    # Send the GET request with the specified cookie
    response = requests.get(url, cookies=cookies)       
    return response.json()

def actual_get_tickets_sold():
    data = get_bucketlister_data()
    return data['salesByExperience']['overallSummary']['ticketsSold']

def bucketlister_daily():
    data = get_bucketlister_data()
    daily_data = {}
    for summary in data['salesByExperience']['intervalSummaries']:
        date = summary['intervalStart'].split('T')[0]  # Get just the date part
        if date not in daily_data:
            daily_data[date] = 0
        daily_data[date] += summary['ticketsSold']
    return daily_data

# gets a getter function for the tickets sold
class get_tickets_sold:
    def __init__(self):
        pass

    def get(self,a,b):
        return actual_get_tickets_sold()

def update_session_key(new_key):
    """
    Update the BLT_partner_session cookie value in this file.
    
    Args:
        new_key (str): The new session key value
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the path to this file
        file_path = os.path.abspath(__file__)
        
        # Read the current file content
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Define the pattern to match the cookie definition
        pattern = r'cookies = \{\s*"BLT_partner_session": "(.*?)"\s*\}'
        
        # Replace the key with the new one
        updated_content = re.sub(pattern, f'cookies = {{\n    "BLT_partner_session": "{new_key}"\n}}', content)
        
        # Write the updated content back to the file
        with open(file_path, 'w') as file:
            file.write(updated_content)
        
        # Update the cookies dictionary in memory
        global cookies
        cookies = {
            "BLT_partner_session": new_key
        }
        
        return True
    except Exception as e:
        print(f"Error updating session key: {str(e)}")
        return False

if __name__ == "__main__":
    print(get_tickets_sold().get())
