"""
Configuration file reader utility
"""

import json
from pathlib import Path
from typing import Dict, Any


class ConfigReader:
    """Read configuration from JSON files"""
    
    @staticmethod
    def read_json(file_path: str) -> Dict[str, Any]:
        """
        Read JSON configuration file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary with configuration
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    
    @staticmethod
    def get_test_data(data_dir: str = "data", filename: str = "search_data.json") -> Dict[str, Any]:
        """
        Get test data from data directory
        
        Args:
            data_dir: Data directory name
            filename: Data file name
            
        Returns:
            Test data dictionary
        """
        file_path = Path(__file__).parent.parent / data_dir / filename
        return ConfigReader.read_json(str(file_path))