"""
Dashboard API client
"""

import requests
from typing import Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger('dashboard_client')

class DashboardClient:
    """Client for interacting with Dashboard API"""
    
    def __init__(self):
        self.base_url = "http://localhost:3001"  # Local dashboard API
        self.metrics_endpoint = "/api/metrics"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to Dashboard API with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"Making {method} request to: {endpoint}")
        response = requests.request(
            method=method,
            url=url,
            json=data
        )
        
        if response.status_code not in [200, 201, 204]:
            logger.error(f"Dashboard API Error: {response.text}")
            response.raise_for_status()
        
        return response.json() if response.text else {}
    
    def delete_dataset(self, dataset_id: str = None) -> None:
        """No-op as our dashboard doesn't use datasets"""
        pass

    def create_or_update_dataset(self, schema: Dict[str, Any], dataset_id: str = None) -> None:
        """No-op as our dashboard doesn't use datasets"""
        pass
    
    def push_data(self, data: List[Dict[str, Any]], dataset_id: str = None) -> None:
        """Push data to the dashboard API"""
        try:
            # For main metrics, send the first record
            if not dataset_id:
                if data and len(data) > 0:
                    # Send the data directly since it's already in the correct format
                    self._make_request('POST', self.metrics_endpoint, data=data[0])
                    logger.info("Successfully pushed metrics to dashboard")
            # For daily metrics, send with dailyMetrics key
            else:
                payload = {"dailyMetrics": data}
                self._make_request('POST', self.metrics_endpoint, data=payload)
                logger.info(f"Successfully pushed {len(data)} daily records to dashboard")
        except Exception as e:
            logger.error(f"Error pushing data: {str(e)}")
            raise 

