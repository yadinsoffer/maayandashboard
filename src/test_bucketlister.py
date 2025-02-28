"""
Test script for Bucketlister data
"""

from src.collectors.bucketlister import get_bucketlister_data
from src.utils.logger import setup_logger

logger = setup_logger('test_bucketlister')

def test_bucketlister():
    """Test Bucketlister data collection"""
    try:
        data = get_bucketlister_data()
        logger.info("Successfully got Bucketlister data")
        
        # Print available dates
        logger.info("\nAvailable dates in Bucketlister data:")
        for summary in data['salesByExperience']['intervalSummaries']:
            date = summary['intervalStart'].split('T')[0]
            tickets = summary['ticketsSold']
            logger.info(f"Date: {date}, Tickets: {tickets}")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_bucketlister() 