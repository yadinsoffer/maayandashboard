"""
Test script for Luma data
"""

from src.collectors.luma_collector import LumaCollector
from src.utils.logger import setup_logger

logger = setup_logger('test_luma')

def test_luma():
    """Test Luma data collection"""
    try:
        collector = LumaCollector()
        logger.info("Initialized Luma collector")
        
        data = collector.collect()
        logger.info("Successfully collected Luma data")
        
        # Print daily data
        logger.info("\nAvailable dates in Luma data:")
        for day in data['daily_data']:
            logger.info(f"Date: {day['date']}, Revenue: ${day['daily_revenue']/100:.2f}, Guests: {day['daily_guests']}")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_luma() 