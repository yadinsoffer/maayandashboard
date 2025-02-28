"""
Facebook Ads data collector
"""

import requests
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

from src.collectors import DataCollector
from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger('facebook_collector')

class FacebookAdsCollector(DataCollector):
    """Collects data from Facebook Ads API"""
    
    def __init__(self):
        config = Config.get_facebook_config()
        self.access_token = config['access_token']
        self.api_version = config['api_version']
        self.ad_account_id = config['ad_account_id']
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to Facebook Ads API with retry logic"""
        url = f"{self.base_url}/{endpoint}"
        params['access_token'] = self.access_token
        
        logger.info(f"Making request to: {endpoint}")
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            logger.error(f"Facebook API Error: {response.text}")
            response.raise_for_status()
        
        return response.json()
    
    def _get_ad_status(self, ad_data: Dict[str, Any]) -> str:
        """Get the effective status of an ad"""
        return ad_data.get('effective_status', 'UNKNOWN')
    
    def _get_all_ads(self) -> List[Dict[str, Any]]:
        """Get list of all ads regardless of status"""
        endpoint = f"act_{self.ad_account_id}/ads"
        fields = [
            'id',
            'name',
            'status',
            'effective_status',
            'configured_status',
            'campaign{name}',
            'adset{name}'
        ]
        
        params = {
            'fields': ','.join(fields),
            'limit': 1000
        }
        
        ads_data = self._make_request(endpoint, params)
        all_ads = ads_data.get('data', [])
        
        # Log count by status
        status_counts = {}
        for ad in all_ads:
            status = self._get_ad_status(ad)
            status_counts[status] = status_counts.get(status, 0) + 1
        
        logger.info(f"Found {len(all_ads)} total ads")
        logger.info(f"Status breakdown: {status_counts}")
        return all_ads
    
    def _get_ads_insights(self, ad_ids: List[str]) -> List[Dict[str, Any]]:
        """Get insights for all ads"""
        endpoint = f"act_{self.ad_account_id}/insights"
        fields = [
            'ad_id',
            'ad_name',
            'spend',
            'impressions',
            'clicks',
            'ctr',
            'cpc',
            'reach',
            'frequency'
        ]
        
        params = {
            'fields': ','.join(fields),
            'date_preset': 'maximum',
            'level': 'ad'
        }
        
        insights_data = self._make_request(endpoint, params)
        
        # Get insights for all ads
        all_insights = [
            insight for insight in insights_data.get('data', [])
            if insight.get('ad_id') in ad_ids
        ]
        
        return all_insights
    
    def collect(self) -> Dict[str, Any]:
        """Collect Facebook Ads data"""
        try:
            # Get all ads
            all_ads = self._get_all_ads()
            ad_ids = [ad['id'] for ad in all_ads]
            
            # Get insights for all ads
            insights = self._get_ads_insights(ad_ids)
            
            # Calculate total spend - directly use spend values without conversion
            total_spend = sum(
                float(insight.get('spend', '0'))
                for insight in insights
            )
            
            # Log individual ad spends for debugging
            for insight in insights:
                logger.info(f"Ad '{insight.get('ad_name')}' spend: ${float(insight.get('spend', '0')):.2f}")
            
            # Count active ads
            active_ads_count = sum(1 for ad in all_ads if self._get_ad_status(ad) == 'ACTIVE')
            
            # Prepare standardized output
            data = {
                'total_spend': total_spend,
                'total_ads_count': len(all_ads),
                'active_ads_count': active_ads_count,
                'total_impressions': sum(int(i.get('impressions', 0)) for i in insights),
                'total_clicks': sum(int(i.get('clicks', 0)) for i in insights),
                'ads': [{
                    'id': ad['id'],
                    'name': ad['name'],
                    'status': self._get_ad_status(ad),
                    'campaign': ad.get('campaign', {}).get('name', 'N/A'),
                    'metrics': next(
                        (m for m in insights if m['ad_id'] == ad['id']),
                        {}
                    )
                } for ad in all_ads]
            }
            
            if self.validate_data(data):
                logger.info("Successfully collected Facebook Ads data")
                return data
            else:
                raise ValueError("Collected data failed validation")
                
        except Exception as e:
            logger.error(f"Error collecting Facebook Ads data: {str(e)}")
            raise
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected data"""
        required_fields = ['total_spend', 'total_ads_count', 'active_ads_count', 'ads']
        
        # Check required fields exist
        if not all(field in data for field in required_fields):
            logger.error("Missing required fields in data")
            return False
        
        # Validate total spend is non-negative
        if data['total_spend'] < 0:
            logger.error("Total spend is negative")
            return False
        
        # Validate ads list matches count
        if len(data['ads']) != data['total_ads_count']:
            logger.error("Ads count mismatch")
            return False
        
        # Validate active ads count
        active_count = sum(1 for ad in data['ads'] if ad['status'] == 'ACTIVE')
        if active_count != data['active_ads_count']:
            logger.error("Active ads count mismatch")
            return False
        
        return True 