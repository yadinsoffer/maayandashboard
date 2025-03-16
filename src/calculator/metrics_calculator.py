"""
Metrics calculator for combining and processing data from all sources
"""

from typing import Dict, Any, List
from datetime import datetime
from zoneinfo import ZoneInfo
from src.utils.logger import setup_logger
from src.utils.marketing import get_influencer_spend, get_historical_spend
import json

logger = setup_logger('metrics_calculator')

class MetricsCalculator:
    """Calculates combined metrics from all data sources"""
    
    def __init__(self):
        self.logger = logger
        self.timezone = ZoneInfo("America/New_York")  # ET timezone
        
        # Fee constants
        self.stripe_percentage = 0.029  # 2.9%
        self.stripe_per_guest = 0.30    # $0.30 per guest
        
        # Get marketing spend components
        self.influencer_spend = get_influencer_spend()
        self.historical_spend = get_historical_spend()
        
    def calculate_metrics(self, fb_data: Dict[str, Any], luma_data: Dict[str, Any], bucketlister_tickets: Dict[str, int], divvy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate combined metrics from all data sources
        
        Args:
            fb_data: Data from Facebook Ads collector
            luma_data: Data from Luma collector
            bucketlister_tickets: Dictionary of daily tickets sold from Bucketlister
            divvy_data: Data from Divvy collector
            
        Returns:
            Dict containing calculated metrics
        """
        try:
            # Calculate Bucketlister metrics first (needed for spend calculations)
            total_bucketlister_tickets = sum(bucketlister_tickets.values())
            bucketlister_revenue = total_bucketlister_tickets * 65  # Already in USD
            bucketlister_influencer_fee = bucketlister_revenue * 0.23  # 23% of revenue goes to influencer spend
            
            # Extract base metrics
            fb_spend = fb_data['total_spend']  # Already in USD
            paid_ads_spend = fb_spend + self.historical_spend  # Add historical spend to paid ads
            total_influencer_spend = self.influencer_spend + bucketlister_influencer_fee  # Add Bucketlister influencer fees
            total_spend = paid_ads_spend + total_influencer_spend  # Total is now paid_ads + all influencer spend
            
            # Calculate daily metrics first to get proper revenue after fees
            daily_metrics = self._prepare_daily_metrics(luma_data['daily_data'])
            
            # Calculate totals from daily data
            total_gross_revenue = sum(day['gross_revenue'] for day in daily_metrics) / 100  # Convert to USD
            total_revenue_after_fees = (sum(day['revenue_after_fees'] for day in daily_metrics) / 100) + bucketlister_revenue  # Add Bucketlister revenue
            total_guests = luma_data['total_guests'] + total_bucketlister_tickets  # Add Bucketlister tickets to total
            
            # Calculate key metrics using combined revenue
            spend_to_revenue_ratio = total_spend / total_revenue_after_fees if total_revenue_after_fees > 0 else 0
            revenue_spent_on_ads = spend_to_revenue_ratio * 100 / 100  # Convert ratio to percentage and divide by 100 to fix scaling
            customer_acquisition_cost = total_spend / total_guests if total_guests > 0 else 0
            
            # Calculate final net revenue (after both Stripe fees and marketing spend)
            net_revenue = total_revenue_after_fees - total_spend
            
            # Get average LTV from Luma data
            average_ltv = luma_data.get('average_ltv', 0)  # Already in cents
            
            # Get operational expenses from Divvy data
            operational_expenses = divvy_data.get('total_spend', 0)
            self.logger.info(f"Total operational expenses from Divvy: ${operational_expenses:.2f}")
            
            # Add debug logging for Divvy data
            self.logger.info("Divvy data received:")
            self.logger.info(f"Raw Divvy data: {json.dumps(divvy_data, indent=2)}")
            self.logger.info(f"Operational expenses type: {type(operational_expenses)}")
            
            # Log spend breakdown
            self.logger.info(f"Facebook Ads spend: ${fb_spend:.2f}")
            self.logger.info(f"Historical spend (added to paid ads): ${self.historical_spend:.2f}")
            self.logger.info(f"Total paid ads spend: ${paid_ads_spend:.2f}")
            self.logger.info(f"Influencer spend: ${total_influencer_spend:.2f}")
            self.logger.info(f"Total marketing spend: ${total_spend:.2f}")
            
            # Log Facebook Ads status breakdown
            self.logger.info("\nFacebook Ads Status:")
            self.logger.info(f"Total Ads: {fb_data['total_ads_count']}")
            self.logger.info(f"Active Ads: {fb_data['active_ads_count']}")
            
            # Prepare final data structure with ET timestamp
            metrics = {
                'timestamp': datetime.now(self.timezone).isoformat(),
                'metrics': {
                    'totalSpend': total_spend,  # Already in dollars
                    'totalRevenue': total_revenue_after_fees,  # Using revenue after Stripe fees
                    'totalGuests': total_guests,
                    'spendToRevenueRatio': spend_to_revenue_ratio,
                    'revenueSpentOnAds': revenue_spent_on_ads,
                    'customerAcquisitionCost': customer_acquisition_cost,
                    'accumulatedNetRevenue': net_revenue,
                    'influencerSpend': total_influencer_spend,
                    'facebookSpend': fb_spend,
                    'paidAdsSpend': paid_ads_spend,
                    'historicalSpend': 0,  # Set to 0 since it's now part of paid_ads_spend
                    'averageLtv': average_ltv / 100,  # Convert to dollars
                    'operationalExpenses': operational_expenses  # Add operational expenses from Divvy
                },
                'facebook_metrics': {
                    'total_ads_count': fb_data['total_ads_count'],
                    'active_ads_count': fb_data['active_ads_count'],
                    'total_impressions': fb_data['total_impressions'],
                    'total_clicks': fb_data['total_clicks'],
                    'ads': fb_data['ads']
                },
                'dailyMetrics': self._prepare_daily_breakdown(daily_metrics, bucketlister_tickets)
            }
            
            if self._validate_metrics(metrics):
                self.logger.info("Successfully calculated combined metrics")
                return metrics
            else:
                raise ValueError("Calculated metrics failed validation")
                
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {str(e)}")
            raise
    
    def _prepare_daily_metrics(self, daily_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare daily metrics with fee calculations"""
        daily_metrics = []
        accumulated_revenue_after_fees = 0
        accumulated_guests = 0
        
        for day in daily_data:
            daily_gross = day['daily_revenue'] / 100  # Convert to USD
            daily_guests = day['daily_guests']
            
            # Calculate Stripe fees for this day
            stripe_percentage_fee = daily_gross * self.stripe_percentage
            stripe_guest_fee = daily_guests * self.stripe_per_guest
            total_daily_fees = stripe_percentage_fee + stripe_guest_fee
            
            # Calculate revenue after Stripe fees
            daily_revenue_after_fees = daily_gross - total_daily_fees
            
            # Update accumulated totals
            accumulated_revenue_after_fees += daily_revenue_after_fees
            accumulated_guests += daily_guests
            
            daily_metrics.append({
                'date': day['date'],
                'gross_revenue': day['daily_revenue'],  # Keep in cents
                'revenue_after_fees': int(daily_revenue_after_fees * 100),  # Convert back to cents
                'stripe_fees': int(total_daily_fees * 100),  # Convert to cents
                'accumulated_revenue_after_fees': int(accumulated_revenue_after_fees * 100),  # Convert to cents
                'daily_guests': daily_guests,
                'accumulated_guests': accumulated_guests
            })
        
        return daily_metrics
    
    def _prepare_daily_breakdown(self, daily_metrics: List[Dict[str, Any]], bucketlister_data: Dict[str, int]) -> List[Dict[str, Any]]:
        """Prepare final daily breakdown for Dashboard"""
        # Create a dictionary of all dates from Luma data
        daily_by_date = {day['date']: day for day in daily_metrics}
        
        # Get all unique dates from both sources
        all_dates = sorted(set(list(daily_by_date.keys()) + list(bucketlister_data.keys())))
        
        # Get latest date from each source
        latest_luma_date = max(daily_by_date.keys()) if daily_by_date else None
        latest_bucketlister_date = max(bucketlister_data.keys()) if bucketlister_data else None
        
        breakdown = []
        accumulated_revenue_after_fees = 0
        accumulated_gross_revenue = 0
        accumulated_guests = 0
        
        for date in all_dates:
            # Only include Luma data if the date is not after the latest Luma date
            luma_day = daily_by_date.get(date, {
                'gross_revenue': 0,
                'revenue_after_fees': 0,
                'accumulated_revenue_after_fees': 0,
                'daily_guests': 0,
                'accumulated_guests': 0
            }) if not latest_luma_date or date <= latest_luma_date else {
                'gross_revenue': 0,
                'revenue_after_fees': 0,
                'accumulated_revenue_after_fees': 0,
                'daily_guests': 0,
                'accumulated_guests': 0
            }
            
            # Only include Bucketlister data if the date is not after the latest Bucketlister date
            bucketlister_daily_guests = bucketlister_data.get(date, 0) if not latest_bucketlister_date or date <= latest_bucketlister_date else 0
            bucketlister_daily_revenue = bucketlister_daily_guests * 65  # Already in dollars
            
            # Update accumulated totals
            daily_gross = (luma_day['gross_revenue'] / 100) + bucketlister_daily_revenue  # Convert to dollars
            daily_net = (luma_day['revenue_after_fees'] / 100) + bucketlister_daily_revenue  # Convert to dollars
            
            accumulated_gross_revenue += daily_gross
            accumulated_revenue_after_fees += daily_net
            accumulated_guests += luma_day['daily_guests'] + bucketlister_daily_guests
            
            # Log the data sources being used for this date
            self.logger.info(f"Date {date} - Using Luma data: {date <= latest_luma_date if latest_luma_date else False}, "
                           f"Using Bucketlister data: {date <= latest_bucketlister_date if latest_bucketlister_date else False}")
            
            breakdown.append({
                'date': date,
                'grossRevenue': accumulated_gross_revenue,  # Now showing accumulated gross revenue
                'netRevenue': accumulated_revenue_after_fees,  # Now showing accumulated net revenue
                'accumulatedNet': accumulated_revenue_after_fees,  # This field is now redundant but keeping for backward compatibility
                'dailyGuests': luma_day['daily_guests'] + bucketlister_daily_guests,
                'accumulatedGuests': accumulated_guests
            })
        
        return breakdown
    
    def _validate_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Validate calculated metrics"""
        try:
            # Check required sections exist
            required_sections = ['metrics', 'facebook_metrics', 'dailyMetrics']
            if not all(section in metrics for section in required_sections):
                self.logger.error("Missing required sections in metrics")
                return False
            
            # Validate marketing metrics
            marketing = metrics['metrics']
            if marketing['totalSpend'] < 0:
                self.logger.error("Negative total spend")
                return False
            if marketing['totalRevenue'] < 0:
                self.logger.error("Negative total revenue")
                return False
            if marketing['totalGuests'] < 0:
                self.logger.error("Negative total guests")
                return False
            if not 0 <= marketing['revenueSpentOnAds'] <= 100:
                self.logger.error("Invalid revenue spent on ads percentage")
                return False
            
            # Validate daily metrics
            for day in metrics['dailyMetrics']:
                if day['grossRevenue'] < 0 or day['netRevenue'] < 0:
                    self.logger.error("Negative revenue in daily metrics")
                    return False
                if day['dailyGuests'] < 0:
                    self.logger.error("Negative guests in daily metrics")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating metrics: {str(e)}")
            return False 