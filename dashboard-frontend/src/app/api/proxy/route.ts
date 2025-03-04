import { NextRequest, NextResponse } from 'next/server';
//new deployment to github
// Server-side environment variables need to be accessed directly
const EC2_API_URL = 'http://ec2-100-27-189-61.compute-1.amazonaws.com:5001';
// Hardcode the API key directly since we're having issues with environment variables
const API_KEY = 'maayan-dashboard-secure-api-key-2024';

export async function POST(request: NextRequest) {
  try {
    console.log('Proxy endpoint called');
    console.log('Using EC2_API_URL:', EC2_API_URL);
    
    const body = await request.json();
    const { endpoint } = body;
    
    console.log('Request body:', JSON.stringify(body));
    
    if (!endpoint) {
      console.error('No endpoint specified');
      return NextResponse.json(
        { error: 'Endpoint not specified' },
        { status: 400 }
      );
    }
    
    let requestBody = {};
    
    // Add the key to the request body for validate-key endpoint
    if (endpoint === 'validate-key' && body.key) {
      requestBody = { key: body.key };
    }
    
    const url = `${EC2_API_URL}/api/${endpoint}`;
    console.log('Forwarding request to:', url);
    
    // Use the hardcoded API key
    const authHeader = `Bearer ${API_KEY}`;
    console.log('Using Authorization header with hardcoded API key');
    
    // Forward the request to the EC2 API
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader
      },
      body: Object.keys(requestBody).length > 0 ? JSON.stringify(requestBody) : undefined
    });
    
    console.log('EC2 API response status:', response.status);
    
    // Parse the response body
    const responseText = await response.text();
    console.log('EC2 API response text:', responseText);
    
    let responseData;
    
    try {
      responseData = JSON.parse(responseText);
      console.log('EC2 API response data:', JSON.stringify(responseData));
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (_) {
      console.error('Failed to parse response as JSON:', responseText);
      responseData = { 
        success: false, 
        error: 'PARSE_ERROR', 
        message: 'Failed to parse response from server' 
      };
    }
    
    // Special handling for KEY_ERROR responses
    if (responseData.error === 'KEY_ERROR' || 
        (responseData.details && responseData.details.includes('KEY_ERROR'))) {
      console.log('Detected KEY_ERROR in response');
      return NextResponse.json({
        success: false,
        error: 'KEY_ERROR',
        message: responseData.message || 'Invalid or expired key'
      }, { status: 400 });
    }
    
    // For other error responses
    if (!response.ok) {
      console.error('EC2 API returned error:', response.status, response.statusText, responseText);
      return NextResponse.json(responseData, { status: response.status });
    }
    
    return NextResponse.json(responseData);
  } catch (error) {
    console.error('Error proxying request to EC2:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'PROXY_ERROR',
        message: `Failed to proxy request to EC2 API: ${error instanceof Error ? error.message : String(error)}`
      },
      { status: 500 }
    );
  }
}    
