"""
Test script for Luma collector
"""

from src.collectors.luma_collector import LumaCollector
from src.utils.logger import setup_logger

logger = setup_logger('test_luma')

def test_luma_collector():
    """Test Luma data collection"""
    try:
        collector = LumaCollector()
        logger.info("Initialized Luma collector")
        
        data = collector.collect()
        logger.info("Successfully collected Luma data")
        
        # Print summary
        logger.info("\nLuma Events Summary:")
        logger.info(f"Total Revenue: ${data['total_revenue']/100:.2f}")  # Convert cents to dollars
        logger.info(f"Total Guests: {data['total_guests']}")
        logger.info(f"Total Events: {data['event_count']}")
        
        # Print LTV metrics
        logger.info("\nCustomer Lifetime Value Metrics:")
        logger.info(f"Average LTV: ${data['average_ltv']/100:.2f}")  # Convert cents to dollars
        logger.info(f"Total Unique Guests: {data['total_unique_guests']}")
        logger.info(f"Repeat Guests: {data['repeat_guest_count']} ({data['repeat_guest_percentage']:.1f}%)")
        
        # Print daily breakdown with fees calculation
        logger.info("\nDaily Breakdown:")
        for day in data['daily_data']:
            logger.info(f"\nDate: {day['date']}")
            daily_revenue = day['daily_revenue']/100  # Convert to dollars
            daily_guests = day['daily_guests']
            
            # Calculate fees
            stripe_percentage_fee = daily_revenue * 0.029  # 2.9%
            stripe_guest_fee = daily_guests * 0.30  # $0.30 per guest
            total_fees = stripe_percentage_fee + stripe_guest_fee
            revenue_after_fees = daily_revenue - total_fees
            
            logger.info(f"Daily Revenue (Gross): ${daily_revenue:.2f}")
            logger.info(f"Stripe Fees: ${total_fees:.2f}")
            logger.info(f"Daily Revenue (After Fees): ${revenue_after_fees:.2f}")
            logger.info(f"Daily Guests: {daily_guests}")
            logger.info(f"Accumulated Revenue (Gross): ${day['accumulated_revenue']/100:.2f}")
            logger.info(f"Accumulated Guests: {day['accumulated_guests']}")
            logger.info(f"Events Count: {day['event_count']}")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_luma_collector() 