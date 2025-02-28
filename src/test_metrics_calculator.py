"""
Test script for metrics calculator
"""

from src.collectors.facebook_collector import FacebookAdsCollector
from src.collectors.luma_collector import LumaCollector
from src.calculator.metrics_calculator import MetricsCalculator
from src.utils.logger import setup_logger

logger = setup_logger('test_metrics')

def test_metrics_calculator():
    """Test metrics calculation with real data from collectors"""
    try:
        # Collect data from both sources
        logger.info("Collecting data from Facebook Ads...")
        fb_collector = FacebookAdsCollector()
        fb_data = fb_collector.collect()
        
        logger.info("Collecting data from Luma...")
        luma_collector = LumaCollector()
        luma_data = luma_collector.collect()
        
        # Calculate combined metrics
        logger.info("Calculating combined metrics...")
        calculator = MetricsCalculator()
        metrics = calculator.calculate_metrics(fb_data, luma_data)
        
        # Print summary
        logger.info("\nCombined Metrics Summary:")
        marketing = metrics['marketing_metrics']
        logger.info(f"Total Marketing Spend: ${marketing['total_spend']/100:.2f}")
        logger.info(f"Total Revenue: ${marketing['total_revenue']/100:.2f}")
        logger.info(f"Total Guests: {marketing['total_guests']}")
        logger.info(f"Spend to Revenue Ratio: {marketing['spend_to_revenue_ratio']:.3f}")
        logger.info(f"Revenue Spent on Ads: {marketing['revenue_spent_on_ads']*100:.1f}%")
        logger.info(f"Customer Acquisition Cost: ${marketing['customer_acquisition_cost']/100:.2f}")
        logger.info(f"Net Revenue: ${marketing['accumulated_net_revenue']/100:.2f}")
        
        # Print Facebook metrics
        facebook = metrics['facebook_metrics']
        logger.info("\nFacebook Ads Metrics:")
        logger.info(f"Active Ads: {facebook['active_ads_count']}")
        logger.info(f"Total Impressions: {facebook['total_impressions']}")
        logger.info(f"Total Clicks: {facebook['total_clicks']}")
        
        # Print daily metrics
        logger.info("\nDaily Metrics:")
        for day in metrics['daily_metrics']:
            logger.info(f"\nDate: {day['date']}")
            logger.info(f"Gross Revenue: ${day['gross_revenue']/100:.2f}")
            logger.info(f"Net Revenue: ${day['net_revenue']/100:.2f}")
            logger.info(f"Daily Guests: {day['daily_guests']}")
            logger.info(f"Accumulated Net Revenue: ${day['accumulated_net']/100:.2f}")
            logger.info(f"Accumulated Guests: {day['accumulated_guests']}")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_metrics_calculator() 