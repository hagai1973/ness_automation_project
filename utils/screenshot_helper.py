"""
Screenshot utility for capturing test evidence
"""

import os
from datetime import datetime
from playwright.sync_api import Page


class ScreenshotHelper:
    """Helper class for taking screenshots"""
    
    def __init__(self, screenshots_dir: str = "screenshots"):
        self.screenshots_dir = screenshots_dir
        
        # Create screenshots directory if not exists
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
    
    
    def take_screenshot(self, page: Page, name: str) -> str:
        """
        Take a screenshot with timestamp
        
        Args:
            page: Playwright page object
            name: Screenshot name (e.g., 'login', 'cart')
            
        Returns:
            Path to saved screenshot
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        page.screenshot(path=filepath, full_page=True)
        return filepath
    
    
    def take_element_screenshot(self, page: Page, selector: str, name: str) -> str:
        """
        Take screenshot of specific element
        
        Args:
            page: Playwright page object
            selector: CSS selector or XPath
            name: Screenshot name
            
        Returns:
            Path to saved screenshot
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_element_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        element = page.locator(selector).first
        element.screenshot(path=filepath)
        return filepath