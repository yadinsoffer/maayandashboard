"""
Main orchestrator for the Maayan Dashboard data pipeline
"""

import sys
from datetime import datetime
from typing import Dict, Any
import requests
import json

from src.collectors.facebook_collector import FacebookAdsCollector
from src.collectors.luma_collector import LumaCollector
from src.collectors.bucketlister import get_tickets_sold, bucketlister_daily
from src.collectors.divvy_collector import DivvyCollector
from src.calculator.metrics_calculator import MetricsCalculator
from src.integrations.geckoboard.client import DashboardClient
from src.integrations.geckoboard.datasets import transform_metrics_for_geckoboard, transform_daily_metrics_for_geckoboard
from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger('main')

def initialize_collectors():
    """Initialize all data collectors"""
    try:
        logger.info("Initializing collectors...")
        fb_collector = FacebookAdsCollector()
        luma_collector = LumaCollector()
        divvy_collector = DivvyCollector()
        calculator = MetricsCalculator()
        dashboard = DashboardClient()
        
        return fb_collector, luma_collector, divvy_collector, calculator, dashboard
    except Exception as e:
        logger.error(f"Failed to initialize collectors: {str(e)}")
        raise

def collect_and_process_data() -> Dict[str, Any]:
    """
    Main function to collect and process all data
    
    Returns:
        Dict[str, Any]: Processed metrics ready for dashboard
    """
    try:
        # Initialize collectors
        fb_collector, luma_collector, divvy_collector, calculator, _ = initialize_collectors()
        
        # Collect Facebook Ads data
        logger.info("Collecting Facebook Ads data...")
        fb_data = fb_collector.collect()
        logger.info("Successfully collected Facebook Ads data")
        
        # Collect Luma data
        logger.info("Collecting Luma data...")
        luma_data = luma_collector.collect()
        logger.info("Successfully collected Luma data")
        
        # Get Bucketlister tickets sold
        logger.info("Getting Bucketlister tickets data...")
        bucketlister_tickets = bucketlister_daily()
        logger.info(f"Successfully got Bucketlister tickets: {bucketlister_tickets}")
        
        # Collect Divvy data
        logger.info("Collecting Divvy data...")
        divvy_data = divvy_collector.collect()
        logger.info("Successfully collected Divvy data")
        
        # Calculate combined metrics
        logger.info("Calculating combined metrics...")
        metrics = calculator.calculate_metrics(fb_data, luma_data, bucketlister_tickets, divvy_data)
        logger.info("Successfully calculated combined metrics")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error in data collection pipeline: {str(e)}")
        raise

def push_to_dashboard(metrics: Dict[str, Any]) -> None:
    """Push metrics to Dashboard API"""
    try:
        logger.info("Pushing metrics to dashboard API...")
        
        # Debug logging for operational expenses
        logger.info("Debug: Metrics received in push_to_dashboard:")
        logger.info(f"Raw metrics object: {json.dumps(metrics, indent=2)}")
        logger.info(f"Operational expenses from metrics: ${metrics['metrics'].get('operationalExpenses', 0):.2f}")
        
        # Prepare the request data
        request_data = {
            "metrics": {
                "totalMarketingSpend": { 
                    "value": metrics['metrics']['totalSpend'], 
                    "label": "Total Marketing Spend", 
                    "prefix": "$" 
                },
                "influencerSpend": { 
                    "value": metrics['metrics']['influencerSpend'], 
                    "label": "Influencer Spend", 
                    "prefix": "$" 
                },
                "paidAdsSpend": { 
                    "value": metrics['metrics']['paidAdsSpend'], 
                    "label": "Paid Ads Spend", 
                    "prefix": "$" 
                },
                "netRevenue": { 
                    "value": metrics['metrics']['accumulatedNetRevenue'], 
                    "label": "Net Revenue", 
                    "prefix": "$" 
                },
                "revenueSpentOnAds": { 
                    "value": metrics['metrics']['revenueSpentOnAds'], 
                    "label": "Revenue Spent on Ads", 
                    "suffix": "%" 
                },
                "customerLifetimeValue": { 
                    "value": metrics['metrics']['averageLtv'], 
                    "label": "Customer Lifetime Value", 
                    "prefix": "$" 
                },
                "customerAcquisitionCost": { 
                    "value": metrics['metrics']['customerAcquisitionCost'], 
                    "label": "Customer Acquisition Cost", 
                    "prefix": "$" 
                },
                "tickets": { 
                    "value": metrics['metrics']['totalGuests'], 
                    "label": "Tickets" 
                },
                "revenue": { 
                    "value": metrics['metrics']['totalRevenue'], 
                    "label": "Revenue", 
                    "prefix": "$" 
                },
                "operationalExpenses": {
                    "value": metrics['metrics']['operationalExpenses'],
                    "label": "Lala Expenses",
                    "prefix": "$"
                }
            },
            "dailyMetrics": [
                {
                    "date": day['date'],
                    "grossRevenue": day['grossRevenue'],
                    "netRevenue": day['netRevenue'],
                    "dailyGuests": day['dailyGuests'],
                    "accumulatedGuests": day['accumulatedGuests']
                }
                for day in metrics['dailyMetrics']
            ]
        }
        
        # Log the metrics being sent for debugging
        logger.info("Sending metrics to dashboard:")
        for metric_name, metric_value in request_data["metrics"].items():
            logger.info(f"{metric_name}: {metric_value['value']}")
            
        # Additional debug logging for operational expenses in request
        logger.info(f"Debug: Operational expenses in request_data: ${request_data['metrics']['operationalExpenses']['value']:.2f}")
        
        # Log the complete request data being sent to Vercel
        logger.info("=== COMPLETE VERCEL API REQUEST DATA ===")
        logger.info(f"Endpoint: {Config.VERCEL_API_URL}/api/metrics/update")
        logger.info(f"Complete request JSON: {json.dumps(request_data, indent=2)}")
        logger.info("=== END OF VERCEL API REQUEST DATA ===")
        
        # Send data to Vercel API
        response = requests.post(
            f"{Config.VERCEL_API_URL}/api/metrics/update",
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {Config.API_KEY}"
            }
        )
        
        if not response.ok:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        else:
            # Log the response from Vercel
            logger.info(f"Vercel API response status: {response.status_code}")
            try:
                logger.info(f"Vercel API response: {json.dumps(response.json(), indent=2)}")
            except:
                logger.info(f"Vercel API response text: {response.text}")
            
        logger.info("Successfully pushed metrics to dashboard API")
        
    except Exception as e:
        logger.error(f"Error pushing metrics to dashboard: {str(e)}")
        raise

def log_metrics_summary(metrics: Dict[str, Any]):
    """Log a summary of the calculated metrics"""
    try:
        marketing = metrics['metrics']
        facebook = metrics['facebook_metrics']
        
        logger.info("\nMetrics Summary:")
        logger.info(f"Timestamp: {metrics['timestamp']}")
        
        logger.info("\nMarketing Metrics:")
        logger.info(f"Total Marketing Spend: ${marketing['totalSpend']:.2f}")
        logger.info(f"Total Revenue: ${marketing['totalRevenue']:.2f}")
        logger.info(f"Total Guests: {marketing['totalGuests']}")
        logger.info(f"Customer Acquisition Cost: ${marketing['customerAcquisitionCost']:.2f}")
        logger.info(f"Net Revenue: ${marketing['accumulatedNetRevenue']:.2f}")
        
        logger.info("\nFacebook Metrics:")
        logger.info(f"Active Ads: {facebook['active_ads_count']}")
        logger.info(f"Total Impressions: {facebook['total_impressions']}")
        logger.info(f"Total Clicks: {facebook['total_clicks']}")
        
        logger.info("\nDaily Breakdown:")
        for day in metrics['dailyMetrics']:
            logger.info(f"\nDate: {day['date']}")
            logger.info(f"Gross Revenue: ${day['grossRevenue']:.2f}")
            logger.info(f"Net Revenue: ${day['netRevenue']:.2f}")
            logger.info(f"Daily Guests: {day['dailyGuests']}")
            logger.info(f"Accumulated Guests: {day['accumulatedGuests']}")
            
    except Exception as e:
        logger.error(f"Error logging metrics summary: {str(e)}")

def main():
    """Main entry point"""
    try:
        logger.info("Starting Maayan Dashboard data pipeline")
        logger.info(f"Time: {datetime.utcnow().isoformat()}Z")
        
        # Validate environment
        Config.validate_env()
        
        # Collect and process data
        metrics = collect_and_process_data()
        
        # Log summary
        log_metrics_summary(metrics)
        
        # Log datasets
        logger.info("=== Dataset Transformation Debug ===")
        logger.info("Raw metrics before transformation:")
        logger.info(json.dumps(metrics, indent=2))
        
        # Transform and log Geckoboard datasets
        geckoboard_metrics = transform_metrics_for_geckoboard(metrics)
        logger.info("Transformed Geckoboard metrics dataset:")
        logger.info(json.dumps(geckoboard_metrics, indent=2))
        
        daily_metrics = transform_daily_metrics_for_geckoboard(metrics)
        logger.info("Transformed Geckoboard daily metrics dataset:")
        logger.info(json.dumps(daily_metrics, indent=2))
        
        # Log how the data would be transformed for charts
        logger.info("=== Chart Data Transformation Debug ===")
        
        # Example of how bar chart data would be structured (daily guests)
        bar_chart_data = [
            {
                "date": day['date'],
                "value": day['dailyGuests']
            }
            for day in metrics['dailyMetrics']
        ]
        logger.info("Bar Chart Data (Daily Guests):")
        logger.info(json.dumps(bar_chart_data, indent=2))
        
        # Example of how line chart data would be structured (gross revenue)
        line_chart_data = [
            {
                "date": day['date'],
                "value": str(day['grossRevenue'])
            }
            for day in metrics['dailyMetrics']
        ]
        logger.info("Line Chart Data (Gross Revenue):")
        logger.info(json.dumps(line_chart_data, indent=2))
        
        # Push to Dashboard
        push_to_dashboard(metrics)
        
        # TODO: Add health check
        # TODO: Add alerting
        
        logger.info("Pipeline completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 