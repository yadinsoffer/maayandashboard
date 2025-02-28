"""
Test script for Facebook Ads collector
"""

from src.collectors.facebook_collector import FacebookAdsCollector
from src.utils.logger import setup_logger

logger = setup_logger('test_facebook')

def test_facebook_collector():
    """Test Facebook Ads data collection"""
    try:
        collector = FacebookAdsCollector()
        logger.info("Initialized Facebook Ads collector")
        
        data = collector.collect()
        logger.info("Successfully collected Facebook Ads data")
        
        # Print summary
        logger.info("\nFacebook Ads Summary:")
        logger.info(f"Total Spend: ${data['total_spend']:.2f}")
        logger.info(f"Active Ads: {data['active_ads_count']}")
        logger.info(f"Total Impressions: {data['total_impressions']}")
        logger.info(f"Total Clicks: {data['total_clicks']}")
        
        # Print details for each ad
        logger.info("\nActive Ads Details:")
        for ad in data['ads']:
            logger.info(f"\nAd: {ad['name']}")
            logger.info(f"Campaign: {ad['campaign']}")
            metrics = ad['metrics']
            if metrics:
                logger.info(f"Spend: ${float(metrics.get('spend', 0)) * 0.28:.2f}")
                logger.info(f"Impressions: {metrics.get('impressions', 0)}")
                logger.info(f"Clicks: {metrics.get('clicks', 0)}")
                logger.info(f"CTR: {metrics.get('ctr', 0)}%")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_facebook_collector() 