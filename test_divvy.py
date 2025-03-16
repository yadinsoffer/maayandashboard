import os
from dotenv import load_dotenv
from src.collectors.divvy_collector import DivvyCollector
from datetime import datetime, timezone
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_divvy():
    try:
        # Load environment variables
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        print(f"Looking for .env file at: {env_path}")
        load_dotenv(env_path)
        
        # Print token (first few characters)
        token = os.getenv('DIVVY_API_TOKEN')
        if token:
            print(f"Found token (first 10 chars): {token[:10]}...")
        else:
            print("No token found!")
            
        # Initialize collector
        collector = DivvyCollector()
        
        # Set date range
        start_date = datetime(2025, 2, 1, tzinfo=timezone.utc)
        end_date = datetime.now(timezone.utc)
        
        print(f"\nFetching transactions from {start_date} to {end_date}")
        
        # Get transactions
        transactions = collector.get_transactions(start_date, end_date)
        
        # Calculate total spend (excluding declined)
        total_spend = sum(
            float(t.get('amount', 0))
            for t in transactions
            if t.get('transactionType') != 'DECLINE'
        )
        
        # Print results
        print(f"\nTotal transactions found: {len(transactions)}")
        print(f"Total spend (excluding declined): ${total_spend:.2f}")
        print("\nFirst few transactions:")
        for t in transactions[:3]:
            print(f"- {t.get('merchantName')}: ${float(t.get('amount', 0)):.2f} ({t.get('transactionType')})")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_divvy() 