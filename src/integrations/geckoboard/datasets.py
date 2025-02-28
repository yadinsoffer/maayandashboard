"""
Geckoboard dataset definitions and transformations
"""

from typing import Dict, Any, List
from datetime import datetime
from zoneinfo import ZoneInfo

# Dataset field definitions
MARKETING_METRICS_SCHEMA = {
    "timestamp": {
        "type": "datetime",
        "name": "Time"
    },
    "customer_acquisition_cost": {
        "type": "money",
        "name": "Customer Acquisition Cost",
        "currency_code": "USD"
    },
    "customer_lifetime_value": {
        "type": "money",
        "name": "Customer Lifetime Value",
        "currency_code": "USD"
    },
    "revenue_spent_on_ads": {
        "type": "percentage",
        "name": "Revenue Spent on Ads"
    },
    "revenue_after_stripe": {
        "type": "money",
        "name": "Revenue (net of stripe)",
        "currency_code": "USD"
    },
    "accumulated_tickets": {
        "type": "number",
        "name": "Tickets"
    },
    "total_marketing_spend": {
        "type": "money",
        "name": "Total Marketing Spend",
        "currency_code": "USD"
    },
    "influencer_spend": {
        "type": "money",
        "name": "Influencer Spend",
        "currency_code": "USD"
    },
    "paid_ads_spend": {
        "type": "money",
        "name": "Paid Ads Spend",
        "currency_code": "USD"
    },
    "historical_spend": {
        "type": "money",
        "name": "Historical Marketing Spend",
        "currency_code": "USD"
    },
    "net_revenue": {
        "type": "money",
        "name": "Net Revenue (net of marketing and stripe)",
        "currency_code": "USD"
    }
}

# New schema for daily revenue dataset
DAILY_REVENUE_SCHEMA = {
    "date": {
        "type": "date",
        "name": "Date"
    },
    "gross_revenue": {
        "type": "money",
        "name": "Gross Revenue",
        "currency_code": "USD"
    },
    "net_revenue": {
        "type": "money",
        "name": "Net Revenue",
        "currency_code": "USD"
    },
    "daily_guests": {
        "type": "number",
        "name": "Daily Guests"
    },
    "accumulated_guests": {
        "type": "number",
        "name": "Total Guests"
    },
    "accumulated_net": {
        "type": "money",
        "name": "Accumulated Net Revenue",
        "currency_code": "USD"
    }
}

def transform_metrics_for_geckoboard(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transform metrics into Geckoboard dataset format
    
    Args:
        metrics: Combined metrics from collectors
        
    Returns:
        List of records in Geckoboard format
    """
    marketing = metrics['metrics']
    
    # Ensure timestamp is in ET
    timestamp = metrics['timestamp']
    if not timestamp.endswith('-04:00') and not timestamp.endswith('-05:00'):
        # If timestamp is not already in ET, convert it
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        et_dt = dt.astimezone(ZoneInfo("America/New_York"))
        timestamp = et_dt.isoformat()
    
    # Create main metrics record
    record = {
        "timestamp": timestamp,
        "customer_acquisition_cost": marketing['customerAcquisitionCost'] * 100,  # Convert to cents
        "customer_lifetime_value": marketing['averageLtv'] * 100,  # Convert to cents
        "revenue_spent_on_ads": marketing['revenueSpentOnAds'],  # Already a percentage
        "revenue_after_stripe": marketing['totalRevenue'] * 100,  # Convert to cents
        "accumulated_tickets": marketing['totalGuests'],
        "total_marketing_spend": marketing['totalSpend'] * 100,  # Convert to cents
        "influencer_spend": marketing['influencerSpend'] * 100,  # Convert to cents
        "paid_ads_spend": marketing['paidAdsSpend'] * 100,  # Convert to cents
        "historical_spend": marketing['historicalSpend'] * 100,  # Convert to cents
        "net_revenue": marketing['accumulatedNetRevenue'] * 100  # Convert to cents
    }
    
    return [record]

def transform_daily_metrics_for_geckoboard(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transform daily metrics into Geckoboard dataset format
    
    Args:
        metrics: Combined metrics from collectors
        
    Returns:
        List of daily records in Geckoboard format
    """
    daily_records = []
    
    for day in metrics['dailyMetrics']:
        record = {
            "date": day['date'],
            "gross_revenue": day['grossRevenue'] * 100,  # Convert to cents
            "net_revenue": day['netRevenue'] * 100,  # Convert to cents
            "daily_guests": day['dailyGuests'],
            "accumulated_guests": day['accumulatedGuests'],
            "accumulated_net": day['accumulatedNet'] * 100  # Convert to cents
        }
        daily_records.append(record)
    
    return daily_records 


