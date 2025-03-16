import os
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import json

from src.collectors import DataCollector
from src.utils.logger import setup_logger

logger = setup_logger('divvy_collector')

class DivvyCollector(DataCollector):
    """Collector for Divvy credit card expenses."""
    
    def __init__(self):
        self.api_token = os.getenv('DIVVY_API_TOKEN')
        if not self.api_token:
            raise ValueError("DIVVY_API_TOKEN environment variable is not set")
        
        self.base_url = "https://gateway.prod.bill.com/connect/v3"
        self.headers = {
            "apiToken": self.api_token,
            "Accept": "application/json"
        }
        
        # Default to last 90 days of data
        self.default_days = 90

    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[Any, Any]]:
        """
        Fetch transactions from Divvy API.
        
        Args:
            start_date: Optional start date for filtering transactions (timezone-aware)
            end_date: Optional end date for filtering transactions (timezone-aware)
            
        Returns:
            List of transaction dictionaries
        """
        url = f"{self.base_url}/spend/transactions"
        
        try:
            response = requests.get(url, headers=self.headers)
            logger.debug(f"API Response Status Code: {response.status_code}")
            
            response.raise_for_status()
            
            try:
                data = response.json()
                transactions = data.get('results', [])
                logger.debug(f"Found {len(transactions)} transactions")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Response content: {response.text}")
                raise
            
            # Filter transactions by date if dates are provided
            if start_date or end_date:
                filtered_transactions = []
                for transaction in transactions:
                    try:
                        occurred_time = transaction.get('occurredTime', '')
                        if not occurred_time:
                            logger.warning(f"Transaction missing occurredTime: {transaction.get('id')}")
                            continue
                            
                        # Parse the ISO format datetime and ensure it's timezone-aware
                        transaction_date = datetime.fromisoformat(occurred_time.replace('Z', '+00:00'))
                        if transaction_date.tzinfo is None:
                            transaction_date = transaction_date.replace(tzinfo=timezone.utc)
                        
                        # Ensure comparison dates are timezone-aware
                        if start_date and start_date.tzinfo is None:
                            start_date = start_date.replace(tzinfo=timezone.utc)
                        if end_date and end_date.tzinfo is None:
                            end_date = end_date.replace(tzinfo=timezone.utc)
                        
                        if start_date and transaction_date < start_date:
                            continue
                        if end_date and transaction_date > end_date:
                            continue
                            
                        filtered_transactions.append(transaction)
                    except (ValueError, AttributeError) as e:
                        logger.warning(f"Could not parse transaction date: {occurred_time}")
                        continue
                
                logger.debug(f"Filtered to {len(filtered_transactions)} transactions within date range")
                return filtered_transactions
                
            return transactions
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Divvy transactions: {str(e)}")
            raise

    def _create_empty_data(self) -> Dict[str, Any]:
        """Create empty data structure when no transactions are found"""
        current_time = datetime.now(timezone.utc)
        return {
            'timestamp': current_time.isoformat(),
            'total_spend': 0,
            'transaction_count': 0,
            'transactions': [],
            'spend_by_category': {},
            'start_date': (current_time - timedelta(days=self.default_days)).isoformat(),
            'end_date': current_time.isoformat(),
            'daily_spend': []
        }

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate the collected data"""
        try:
            required_fields = ['total_spend', 'transaction_count', 'transactions', 'spend_by_category', 'start_date', 'end_date']
            if not all(field in data for field in required_fields):
                logger.error("Missing required fields in data")
                return False
            
            if data['total_spend'] < 0:
                logger.error("Negative total spend")
                return False
                
            if data['transaction_count'] < 0:
                logger.error("Negative transaction count")
                return False
                
            if not isinstance(data['transactions'], list):
                logger.error("Transactions is not a list")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            return False

    def collect(self) -> Dict[str, Any]:
        """
        Collect all relevant Divvy data.
        
        Returns:
            Dictionary containing collected data
        """
        # Get transactions for the configured time period
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=self.default_days)
        
        try:
            transactions = self.get_transactions(start_date, end_date)
            
            if not transactions:
                logger.warning("No transactions found")
                return self._create_empty_data()
            
            # Calculate total spend and categorize
            total_spend = 0
            categories = {}
            daily_spend = {}
            
            for transaction in transactions:
                try:
                    # Skip declined transactions
                    if transaction.get('transactionType') == 'DECLINE':
                        continue
                        
                    amount = float(transaction.get('amount', 0))
                    merchant = transaction.get('merchantName', 'Unknown')
                    category = transaction.get('merchantCategoryCode', 'Uncategorized')
                    occurred_time = transaction.get('occurredTime', '')
                    
                    # Parse transaction date for daily breakdown
                    transaction_date = datetime.fromisoformat(occurred_time.replace('Z', '+00:00')).date()
                    date_str = str(transaction_date)
                    
                    # Update daily spend
                    if date_str not in daily_spend:
                        daily_spend[date_str] = 0
                    daily_spend[date_str] += amount
                    
                    # Update total spend and categories
                    total_spend += amount
                    if category not in categories:
                        categories[category] = {
                            'total': 0,
                            'merchants': set()
                        }
                    categories[category]['total'] += amount
                    categories[category]['merchants'].add(merchant)
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error processing transaction amount: {str(e)}")
                    continue
            
            # Convert merchant sets to lists for JSON serialization
            for category in categories.values():
                category['merchants'] = list(category['merchants'])
            
            # Prepare daily spend data
            daily_spend_list = [
                {'date': date, 'spend': amount}
                for date, amount in sorted(daily_spend.items())
            ]
            
            data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_spend': total_spend,
                'transaction_count': len([t for t in transactions if t.get('transactionType') != 'DECLINE']),
                'transactions': transactions,
                'spend_by_category': categories,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'daily_spend': daily_spend_list
            }
            
            if self.validate_data(data):
                logger.info("Successfully collected Divvy data")
                return data
            else:
                raise ValueError("Collected data failed validation")
            
        except Exception as e:
            logger.error(f"Error collecting Divvy data: {str(e)}")
            raise