import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv('API_KEY')
VERCEL_API_URL = os.getenv('VERCEL_API_URL')

def generate_test_data():
    # Generate last 30 days of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    daily_metrics = []
    
    accumulated_guests = 0
    for i in range(31):
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        daily_guests = 20 + (i % 10)  # Random-ish daily guests
        accumulated_guests += daily_guests
        gross_revenue = daily_guests * 100  # $100 per guest
        net_revenue = gross_revenue * 0.8  # 20% costs
        
        daily_metrics.append({
            "date": date,
            "grossRevenue": gross_revenue,
            "netRevenue": net_revenue,
            "dailyGuests": daily_guests,
            "accumulatedGuests": accumulated_guests
        })
    
    # Calculate overall metrics
    total_spend = 5000  # Example marketing spend
    total_revenue = sum(d["grossRevenue"] for d in daily_metrics)
    total_guests = accumulated_guests
    operational_expenses = 2166.91  # Match the value from Divvy
    
    return {
        "metrics": {
            "totalMarketingSpend": {"value": total_spend, "label": "Total Marketing Spend", "prefix": "$"},
            "influencerSpend": {"value": total_spend * 0.6, "label": "Influencer Spend", "prefix": "$"},
            "paidAdsSpend": {"value": total_spend * 0.4, "label": "Paid Ads Spend", "prefix": "$"},
            "netRevenue": {"value": total_revenue * 0.8, "label": "Net Revenue", "prefix": "$"},
            "revenueSpentOnAds": {"value": (total_spend / total_revenue) * 100, "label": "Revenue Spent on Ads", "suffix": "%"},
            "customerLifetimeValue": {"value": total_revenue / total_guests, "label": "Customer Lifetime Value", "prefix": "$"},
            "customerAcquisitionCost": {"value": total_spend / total_guests, "label": "Customer Acquisition Cost", "prefix": "$"},
            "tickets": {"value": total_guests, "label": "Tickets"},
            "revenue": {"value": total_revenue, "label": "Revenue", "prefix": "$"},
            "operationalExpenses": {"value": operational_expenses, "label": "Operational Expenses", "prefix": "$"}
        },
        "dailyMetrics": daily_metrics
    }

def send_test_data():
    if not API_KEY or not VERCEL_API_URL:
        print("Error: API_KEY or VERCEL_API_URL not found in environment variables")
        return
    
    data = generate_test_data()
    
    try:
        response = requests.post(
            f"{VERCEL_API_URL}/api/metrics/update",
            json=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print("Response:", response.json())
        
    except Exception as e:
        print(f"Error sending data: {str(e)}")

if __name__ == "__main__":
    send_test_data() 