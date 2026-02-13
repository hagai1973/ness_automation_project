"""
Smart locator helper with fallback mechanism
"""

from typing import List, Tuple
from playwright.sync_api import Page, Locator
import logging


class LocatorHelper:
    """Helper for managing smart locators with fallback"""
    
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(__name__)
    
    
    def find_with_fallback(
        self, 
        locators: List[Tuple[str, str]], 
        timeout: int = 5000
    ) -> Locator:
        """
        Find element using multiple locators with fallback
        
        Args:
            locators: List of (strategy, value) tuples
            timeout: Timeout per locator attempt (ms)
            
        Returns:
            Locator object
            
        Raises:
            Exception if all locators fail
        """
        for index, (strategy, value) in enumerate(locators, start=1):
            try:
                self.logger.info(f"Trying locator {index}/{len(locators)}: {strategy}={value}")
                
                if strategy == 'css':
                    locator = self.page.locator(value)
                elif strategy == 'xpath':
                    locator = self.page.locator(f"xpath={value}")
                elif strategy == 'text':
                    locator = self.page.get_by_text(value)
                elif strategy == 'role':
                    locator = self.page.get_by_role(value)
                else:
                    self.logger.warning(f"Unknown strategy: {strategy}")
                    continue
                
                # Check if element exists
                locator.wait_for(state='visible', timeout=timeout)
                self.logger.info(f"✅ Success with locator {index}")
                return locator
                
            except Exception as e:
                self.logger.warning(f"❌ Locator {index} failed: {str(e)}")
                if index == len(locators):
                    raise Exception(f"All {len(locators)} locators failed")
                continue
        
        raise Exception("No valid locator found")
    
    
    @staticmethod
    def create_locator_set(css: str, xpath: str, text: str = None) -> List[Tuple[str, str]]:
        """
        Create a set of fallback locators
        
        Args:
            css: CSS selector
            xpath: XPath selector
            text: Optional text content
            
        Returns:
            List of locator tuples
        """
        locators = [
            ('css', css),
            ('xpath', xpath)
        ]
        
        if text:
            locators.append(('text', text))
        
        return locators