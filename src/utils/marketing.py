"""
Marketing utilities
"""

from pathlib import Path
import os

from src.utils.logger import setup_logger

logger = setup_logger('marketing_utils')

def get_project_root() -> Path:
    """Get absolute path to project root directory"""
    return Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def get_influencer_spend() -> float:
    """
    Read the influencer spend from the text file
    
    Returns:
        float: Influencer spend in USD, 0 if file not found or invalid
    """
    try:
        spend_file = get_project_root() / 'influencerspend.txt'
        if not spend_file.exists():
            logger.warning("influencerspend.txt not found, using 0")
            return 0.0
            
        with open(spend_file, 'r') as f:
            spend = float(f.read().strip())
            logger.info(f"Read influencer spend: ${spend:.2f}")
            return spend
            
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error reading influencer spend: {str(e)}")
        return 0.0

def get_historical_spend() -> float:
    """
    Read the historical spend from the text file
    
    Returns:
        float: Historical spend in USD, 0 if file not found or invalid
    """
    try:
        spend_file = get_project_root() / 'historicalspend.txt'
        if not spend_file.exists():
            logger.warning("historicalspend.txt not found, using 0")
            return 0.0
            
        with open(spend_file, 'r') as f:
            spend = float(f.read().strip())
            logger.info(f"Read historical spend: ${spend:.2f}")
            return spend
            
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error reading historical spend: {str(e)}")
        return 0.0 