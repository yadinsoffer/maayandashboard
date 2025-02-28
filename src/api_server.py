import os
import json
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Secret key for authentication
API_KEY = os.environ.get('API_KEY', 'default-secret-key')

# Path to the update script
UPDATE_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'run_update.py')

@app.route('/api/update-dashboard', methods=['POST'])
def update_dashboard():
    # Check for API key
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer ') or auth_header[7:] != API_KEY:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        # Run the update script
        result = subprocess.run(['python3', UPDATE_SCRIPT_PATH], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        
        # If script ran successfully
        return jsonify({
            'success': True,
            'message': 'Dashboard updated successfully',
            'output': result.stdout
        })
    except subprocess.CalledProcessError as e:
        # If script failed due to key error
        if 'KEY_ERROR' in e.stderr:
            return jsonify({
                'success': False,
                'error': 'KEY_ERROR',
                'message': 'Update failed due to invalid key'
            }), 400
        # If script failed for other reasons
        return jsonify({
            'success': False,
            'error': 'UPDATE_FAILED',
            'message': 'Update script failed to execute',
            'details': e.stderr
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'SERVER_ERROR',
            'message': str(e)
        }), 500

@app.route('/api/validate-key', methods=['POST'])
def validate_key():
    # Check for API key
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer ') or auth_header[7:] != API_KEY:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        # Get the new key from request
        data = request.json
        if not data or 'key' not in data:
            return jsonify({
                'success': False,
                'error': 'INVALID_REQUEST',
                'message': 'Key not provided'
            }), 400
        
        new_key = data['key']
        
        # Update the key in bucketlister.py
        from collectors.bucketlister import update_session_key
        update_session_key(new_key)
        
        # Run the update script again
        result = subprocess.run(['python3', UPDATE_SCRIPT_PATH], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        
        # If script ran successfully after key update
        return jsonify({
            'success': True,
            'message': 'Key updated and dashboard refreshed successfully',
            'output': result.stdout
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            'success': False,
            'error': 'UPDATE_FAILED',
            'message': 'Update script failed even after key update',
            'details': e.stderr
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'SERVER_ERROR',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Get port from environment variable
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Starting API server on {host}:{port}...")
    app.run(host=host, port=port) 