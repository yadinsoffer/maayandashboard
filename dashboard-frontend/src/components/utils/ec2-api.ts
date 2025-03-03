/**
 * Client for interacting with the EC2 backend API
 */

/**
 * Trigger the dashboard update process on the EC2 server
 * @returns Promise with the update result
 */
export async function triggerDashboardUpdate(): Promise<{
  success: boolean;
  error?: string;
  message?: string;
}> {
  try {
    console.log('Triggering dashboard update via proxy');
    // Use the proxy endpoint instead of directly calling the EC2 API
    const response = await fetch('/api/proxy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ endpoint: 'update-dashboard' })
    });

    console.log('Proxy response status:', response.status);
    
    // Parse the response regardless of status code
    const responseText = await response.text();
    console.log('Proxy response text:', responseText);
    
    try {
      // Try to parse the response as JSON
      const data = JSON.parse(responseText);
      console.log('Dashboard update response data:', data);
      
      // Check for KEY_ERROR in the response
      if (data.error === 'KEY_ERROR') {
        console.log('KEY_ERROR detected in response');
        return {
          success: false,
          error: 'KEY_ERROR',
          message: data.message || 'Invalid or expired key'
        };
      }
      
      // For other responses
      return data;
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (_) {
      console.error('Failed to parse response as JSON:', responseText);
      return {
        success: false,
        error: 'PARSE_ERROR',
        message: `Failed to parse response: ${responseText}`
      };
    }
  } catch (error) {
    console.error('Error triggering dashboard update:', error);
    return {
      success: false,
      error: 'CONNECTION_ERROR',
      message: 'Failed to connect to the update server'
    };
  }
}

/**
 * Submit a new key to the EC2 server
 * @param key The new session key
 * @returns Promise with the validation result
 */
export async function submitKey(key: string): Promise<{
  success: boolean;
  error?: string;
  message?: string;
}> {
  try {
    console.log('Submitting key via proxy');
    // Use the proxy endpoint instead of directly calling the EC2 API
    const response = await fetch('/api/proxy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        endpoint: 'validate-key',
        key: key
      })
    });

    console.log('Proxy response status:', response.status);
    
    // Parse the response regardless of status code
    const responseText = await response.text();
    console.log('Proxy response text:', responseText);
    
    try {
      // Try to parse the response as JSON
      const data = JSON.parse(responseText);
      console.log('Key validation response data:', data);
      return data;
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (_) {
      console.error('Failed to parse response as JSON:', responseText);
      return {
        success: false,
        error: 'PARSE_ERROR',
        message: `Failed to parse response: ${responseText}`
      };
    }
  } catch (error) {
    console.error('Error submitting key:', error);
    return {
      success: false,
      error: 'CONNECTION_ERROR',
      message: 'Failed to connect to the update server'
    };
  }
} 