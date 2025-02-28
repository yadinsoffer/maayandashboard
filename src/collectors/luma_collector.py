"""
Luma events data collector
"""

import requests
from typing import Dict, Any, List
from datetime import datetime, timezone
from tenacity import retry, stop_after_attempt, wait_exponential
from collections import defaultdict

from src.collectors import DataCollector
from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger('luma_collector')

class LumaCollector(DataCollector):
    """Collects data from Luma API"""
    
    def __init__(self):
        config = Config.get_luma_config()
        self.api_key = config['api_key']
        self.base_url = config['base_url']
        self.headers = {"x-luma-api-key": self.api_key}
        
        # List of event IDs to track
        self.track_events = ["evt-D6W6FYFZRzIvtGL", "evt-rsCQjpjQszHb0tP"]
        
        # List of event IDs to ignore
        self.ignore_events = [
            "evt-VYK92bG9jIB0bMi",
            "evt-xRbyhlNfUhs029h",
            "evt-Gh1SAlQc7dRfyv1",
            "evt-Ife7INJhPKOiqVn"
        ]
        
        # Track guest data for LTV calculation
        self.guest_history = {}  # guest_email -> List[Dict] of event participation
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to Luma API with retry logic"""
        url = f"{self.base_url}/{endpoint}"
        
        logger.info(f"Making request to: {endpoint}")
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code != 200:
            logger.error(f"Luma API Error: {response.text}")
            response.raise_for_status()
        
        return response.json()
    
    def _get_event_guests_and_revenue(self, event_id):
        guests_by_date = defaultdict(lambda: {'amount': 0, 'tickets': 0})
        
        endpoint = "event/get-guests"
        params = {"event_api_id": event_id}
        
        guests_data = self._make_request(endpoint, params)
        entries = guests_data.get("entries", [])
        
        for entry in entries:
            guest = entry.get("guest", {})
            email = guest.get("email")
            tickets = guest.get("event_tickets", [])
            
            if tickets and email:
                total_amount = sum(ticket.get("amount", 0) for ticket in tickets)
                
                # Skip free tickets
                if total_amount == 0:
                    logger.info(f"Skipping free registration for {email}")
                    continue
                
                ticket_count = len(tickets)
                single_ticket_amount = total_amount // ticket_count if ticket_count > 0 else 0
                
                purchase_date = datetime.fromisoformat(guest.get("registered_at", "").replace('Z', '+00:00')).date()
                
                # Update daily revenue with total amount
                guests_by_date[purchase_date]['amount'] += total_amount
                guests_by_date[purchase_date]['tickets'] += ticket_count
                
                logger.info(f"Guest data: Email={email}, Tickets={ticket_count}")
                logger.info(f"Guest details: {guest}")
                
                # Track this event participation for the guest's LTV
                if email not in self.guest_history:
                    self.guest_history[email] = {'events': {}, 'total_spend': 0}
                
                # Only add if this is a new event for this guest
                if event_id not in self.guest_history[email]['events']:
                    self.guest_history[email]['events'][event_id] = {
                        'amount': single_ticket_amount,  # Store single ticket amount for LTV
                        'tickets': ticket_count,
                        'date': purchase_date
                    }
                    # Update total spend with single ticket amount
                    self.guest_history[email]['total_spend'] = sum(
                        e['amount'] for e in self.guest_history[email]['events'].values()
                    )
                    logger.info(f"Added event {event_id} to guest {email}'s history. Single ticket amount: ${single_ticket_amount/100:.2f}")
        
        # Convert to list of daily sales
        daily_sales = []
        for date, data in guests_by_date.items():
            daily_sales.append({
                "date": str(date),
                "revenue": data["amount"],
                "tickets": data["tickets"]
            })
        
        return daily_sales
    
    def _calculate_ltv_metrics(self) -> Dict[str, Any]:
        """Calculate LTV metrics from guest history"""
        if not self.guest_history:
            return {
                "average_ltv": 0,
                "total_unique_guests": 0,
                "repeat_guest_count": 0,
                "repeat_guest_percentage": 0
            }
        
        total_unique_guests = len(self.guest_history)
        repeat_guests = sum(1 for guest_data in self.guest_history.values() if len(guest_data['events']) > 1)
        
        # Calculate individual LTV (sum of single ticket amounts across all events) for each guest
        guest_ltvs = []
        for guest_email, guest_data in self.guest_history.items():
            guest_ltv = guest_data['total_spend']  # Already stored as sum of single ticket amounts
            guest_ltvs.append(guest_ltv)
            logger.info(f"Guest {guest_email} LTV: ${guest_ltv/100:.2f} from {len(guest_data['events'])} events")
        
        # Calculate average LTV across all guests
        average_ltv = sum(guest_ltvs) / len(guest_ltvs) if guest_ltvs else 0
        
        return {
            "average_ltv": average_ltv,
            "total_unique_guests": total_unique_guests,
            "repeat_guest_count": repeat_guests,
            "repeat_guest_percentage": (repeat_guests / total_unique_guests * 100) if total_unique_guests > 0 else 0
        }
    
    def collect(self) -> Dict[str, Any]:
        """Collect Luma events data"""
        try:
            # Get list of all events
            events_data = self._make_request("calendar/list-events")
            entries = events_data.get("entries", [])
            
            if not entries:
                logger.warning("No events found")
                return self._create_empty_data()
            
            # Process each relevant event
            sales_by_date = {}
            current_time = datetime.utcnow().isoformat() + "Z"
            
            for entry in entries:
                event = entry.get("event", {})
                event_id = event.get("api_id")
                
                if not event_id:
                    continue
                
                # Skip if event is in ignore list
                if event_id in self.ignore_events:
                    logger.info(f"Skipping ignored event: {event.get('name', 'Unnamed Event')} ({event_id})")
                    continue
                
                # Process if event is in track list or is a new event
                if event_id in self.track_events or (event_id not in self.track_events and event_id not in self.ignore_events):
                    logger.info(f"Processing event: {event.get('name', 'Unnamed Event')} ({event_id})")
                    daily_sales = self._get_event_guests_and_revenue(event_id)
                    
                    for sale in daily_sales:
                        date = sale["date"]
                        if date in sales_by_date:
                            sales_by_date[date]["daily_revenue"] += sale["revenue"]
                            sales_by_date[date]["daily_guests"] += sale["tickets"]
                            sales_by_date[date]["event_count"] += 1
                        else:
                            sales_by_date[date] = {
                                "daily_revenue": sale["revenue"],
                                "daily_guests": sale["tickets"],
                                "event_count": 1
                            }
            
            # Calculate LTV metrics
            ltv_metrics = self._calculate_ltv_metrics()
            
            # Calculate accumulated metrics and prepare final data
            data = self._prepare_final_data(sales_by_date, current_time)
            
            # Add LTV metrics to the data
            data.update({
                "average_ltv": ltv_metrics["average_ltv"],
                "total_unique_guests": ltv_metrics["total_unique_guests"],
                "repeat_guest_count": ltv_metrics["repeat_guest_count"],
                "repeat_guest_percentage": ltv_metrics["repeat_guest_percentage"]
            })
            
            if self.validate_data(data):
                logger.info("Successfully collected Luma data")
                return data
            else:
                raise ValueError("Collected data failed validation")
                
        except Exception as e:
            logger.error(f"Error collecting Luma data: {str(e)}")
            raise
    
    def _create_empty_data(self) -> Dict[str, Any]:
        """Create empty data structure when no events are found"""
        current_time = datetime.utcnow().isoformat() + "Z"
        return {
            "timestamp": current_time,
            "total_revenue": 0,
            "total_guests": 0,
            "event_count": 0,
            "daily_data": [],
            "average_ltv": 0,
            "total_unique_guests": 0,
            "repeat_guest_count": 0,
            "repeat_guest_percentage": 0
        }
    
    def _prepare_final_data(self, sales_by_date: Dict[str, Dict[str, Any]], timestamp: str) -> Dict[str, Any]:
        """Prepare final data structure with accumulated metrics"""
        accumulated_revenue = 0
        accumulated_guests = 0
        daily_data = []
        
        for date in sorted(sales_by_date.keys()):
            daily_data_point = sales_by_date[date]
            daily_revenue = daily_data_point["daily_revenue"]
            daily_guests = daily_data_point["daily_guests"]
            
            accumulated_revenue += daily_revenue
            accumulated_guests += daily_guests
            
            daily_data.append({
                "date": date,
                "daily_revenue": daily_revenue,
                "daily_guests": daily_guests,
                "accumulated_revenue": accumulated_revenue,
                "accumulated_guests": accumulated_guests,
                "event_count": daily_data_point["event_count"]
            })
        
        return {
            "timestamp": timestamp,
            "total_revenue": accumulated_revenue,
            "total_guests": accumulated_guests,
            "event_count": sum(d["event_count"] for d in daily_data),
            "daily_data": daily_data
        }
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected data"""
        required_fields = [
            'timestamp', 'total_revenue', 'total_guests', 'event_count', 'daily_data',
            'average_ltv', 'total_unique_guests', 'repeat_guest_count', 'repeat_guest_percentage'
        ]
        
        # Check required fields exist
        if not all(field in data for field in required_fields):
            logger.error("Missing required fields in data")
            return False
        
        # Validate total revenue is non-negative
        if data['total_revenue'] < 0:
            logger.error("Total revenue is negative")
            return False
        
        # Validate total guests is non-negative
        if data['total_guests'] < 0:
            logger.error("Total guests is negative")
            return False
        
        # Validate LTV metrics
        if data['average_ltv'] < 0:
            logger.error("Negative average LTV")
            return False
        if not 0 <= data['repeat_guest_percentage'] <= 100:
            logger.error("Invalid repeat guest percentage")
            return False
        
        # Validate daily data if exists
        if data['daily_data']:
            daily_fields = ['date', 'daily_revenue', 'daily_guests', 'accumulated_revenue', 'accumulated_guests']
            for day in data['daily_data']:
                if not all(field in day for field in daily_fields):
                    logger.error("Missing required fields in daily data")
                    return False
                
                if day['daily_revenue'] < 0 or day['daily_guests'] < 0:
                    logger.error("Negative values in daily data")
                    return False
        
        return True 