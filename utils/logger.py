"""
Centralized logging utility
"""

import logging
import os
from datetime import datetime


class Logger:
    """Custom logger for the automation framework"""
    
    @staticmethod
    def get_logger(name: str, log_level=logging.INFO):
        """
        Get or create a logger
        
        Args:
            name: Logger name (usually __name__)
            log_level: Logging level (default: INFO)
            
        Returns:
            Logger instance
        """
        # Create logs directory if not exists
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_filename = f"logs/test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger