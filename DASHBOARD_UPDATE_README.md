# Dashboard Auto-Update System

This system enables automatic updates of the dashboard data when accessing the dashboard URL, with a key validation fallback mechanism.

## Architecture Overview

- **Frontend (Vercel)**: Triggers the update process when the dashboard is loaded and conditionally renders the dashboard or a key input form.
- **Backend (EC2)**: Exposes API endpoints to run the update script and validate/update the key.

## Deployment Instructions

### 1. EC2 Backend Setup

1. **Update Configuration**:
   - Edit `deploy_api_server.sh` and update the EC2 instance details:
     ```bash
     EC2_USER="ubuntu"
     EC2_HOST="ec2-100-27-189-61.compute-1.amazonaws.com"
     EC2_KEY_PATH="maayandashboard.pem"
     ```

2. **Deploy to EC2**:
   ```bash
   ./deploy_api_server.sh
   ```

3. **Verify Deployment**:
   - Check if the service is running:
     ```bash
     ssh -i maayandashboard.pem ubuntu@ec2-100-27-189-61.compute-1.amazonaws.com "sudo systemctl status dashboard-api"
     ```

### 2. Vercel Frontend Setup

1. **Update Environment Variables**:
   - In the Vercel dashboard, add the following environment variables:
     ```
     NEXT_PUBLIC_EC2_API_URL=http://ec2-100-27-189-61.compute-1.amazonaws.com:5001
     NEXT_PUBLIC_EC2_API_KEY=maayan-dashboard-secure-api-key-2024
     ```
   - Or update the `.env.local` file locally and redeploy.

2. **Deploy to Vercel**:
   ```bash
   cd dashboard-frontend
   vercel --prod
   ```

## How It Works

1. **Dashboard Loading**:
   - When a user visits the dashboard URL, the frontend automatically triggers an update request to the EC2 API.
   - If the update is successful, the dashboard displays with the latest data.
   - If the update fails due to an invalid key, the key input form is displayed.

2. **Key Validation**:
   - When a user submits a new key through the form, it's sent to the EC2 API for validation.
   - The API updates the key in the `bucketlister.py` file and retries the update process.
   - If successful, the dashboard is displayed with the latest data.

## Testing

1. **Local API Testing**:
   ```bash
   # Start the API server
   cd src && python api_server.py
   
   # In another terminal, run the test script
   ./test_api.py
   ```

2. **Frontend Testing**:
   ```bash
   cd dashboard-frontend
   npm run dev
   ```

## Troubleshooting

1. **API Server Issues**:
   - Check the logs: `sudo journalctl -u dashboard-api`
   - Restart the service: `sudo systemctl restart dashboard-api`

2. **Key Update Issues**:
   - Verify the key format is correct
   - Check permissions on the `bucketlister.py` file

3. **Frontend Connection Issues**:
   - Verify the EC2 instance is accessible from the internet
   - Check that the API key matches between frontend and backend

## Security Considerations

- The API key should be kept secure and rotated periodically
- Consider implementing HTTPS for the EC2 API server
- Implement rate limiting to prevent abuse

## Maintenance

- Monitor the EC2 instance for resource usage
- Periodically check the logs for any errors
- Update dependencies as needed 
