"""
Data collectors for different sources
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class DataCollector(ABC):
    """Base interface for all data collectors"""
    
    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """
        Collect data from the source
        
        Returns:
            Dict[str, Any]: Collected data in a standardized format
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate collected data
        
        Args:
            data (Dict[str, Any]): Data to validate
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        pass
