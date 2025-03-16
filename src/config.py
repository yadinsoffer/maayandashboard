import os
from typing import Dict

class Config:
    """Configuration management for the application"""
    
    REQUIRED_ENV_VARS = {
        'YADIN_FACEBOOK_ADS_TOKEN': 'Facebook Ads API token',
        'LUMA_API_KEY': 'Luma API key',
        'GECKOBOARD_API_KEY': 'Geckoboard API key',
        'DIVVY_API_TOKEN': 'Divvy API token'
    }
    
    # Vercel API Configuration
    VERCEL_API_URL = os.getenv('VERCEL_API_URL')
    API_KEY = os.getenv('API_KEY')
    
    @classmethod
    def validate_env(cls) -> None:
        """Validate all required environment variables are set"""
        missing_vars = []
        required_vars = [
            'YADIN_FACEBOOK_ADS_TOKEN',
            'LUMA_API_KEY',
            'VERCEL_API_URL',
            'API_KEY',
            'DIVVY_API_TOKEN'
        ]
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(f"{var}")
        
        if missing_vars:
            raise EnvironmentError(
                "Missing required environment variables:\n" +
                "\n".join(missing_vars)
            )
    
    @classmethod
    def get_facebook_config(cls) -> Dict[str, str]:
        """Get Facebook-specific configuration"""
        cls.validate_env()
        return {
            'access_token': os.getenv('YADIN_FACEBOOK_ADS_TOKEN'),
            'api_version': 'v19.0',
            'ad_account_id': '1770605100340015'  # Facebook Ad Account ID
        }

    @classmethod
    def get_luma_config(cls) -> Dict[str, str]:
        """Get Luma-specific configuration"""
        cls.validate_env()
        return {
            'api_key': os.getenv('LUMA_API_KEY'),
            'base_url': 'https://api.lu.ma/public/v1'
        }
    
    @classmethod
    def get_geckoboard_config(cls) -> Dict[str, str]:
        """Get Geckoboard-specific configuration"""
        cls.validate_env()
        return {
            'api_key': os.getenv('GECKOBOARD_API_KEY'),
            'base_url': 'https://api.geckoboard.com',
            'dataset_id': 'marketing_metrics'  # Consider moving to env var if changes
        } 