"""
Base Page - Foundation for all page objects
Includes Smart Locators with fallback mechanism
"""

from playwright.sync_api import Page, expect
import logging
from typing import List, Tuple
import time


class BasePage:
    """Base page class with smart locator mechanism"""
    
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(__name__)
        
    
    def find_element_with_fallback(self, locators: List[Tuple[str, str]], timeout: int = 5000):
        """
        Smart Locator: Try multiple locators with fallback
        
        Args:
            locators: List of tuples [(strategy, value), (strategy, value)]
                     Example: [('css', '#search'), ('xpath', '//input[@name="search"]')]
            timeout: Wait time per locator attempt
            
        Returns:
            Locator object or None
        """
        for index, (strategy, value) in enumerate(locators, start=1):
            try:
                self.logger.info(f"🔍 Attempt {index}/{len(locators)} - Strategy: {strategy}, Value: {value}")
                
                if strategy == 'css':
                    element = self.page.locator(value)
                elif strategy == 'xpath':
                    element = self.page.locator(f"xpath={value}")
                elif strategy == 'text':
                    element = self.page.get_by_text(value)
                elif strategy == 'role':
                    element = self.page.get_by_role(value)
                else:
                    self.logger.warning(f"⚠️ Unknown strategy: {strategy}")
                    continue
                
                # Wait for element to be visible
                element.wait_for(state='visible', timeout=timeout)
                self.logger.info(f"✅ Success with locator {index}: {strategy}={value}")
                return element
                
            except Exception as e:
                self.logger.warning(f"❌ Locator {index} failed: {str(e)}")
                if index == len(locators):
                    self.logger.error(f"🚫 All {len(locators)} locators failed!")
                    self.page.screenshot(path=f"screenshots/fallback_failed_{int(time.time())}.png")
                    raise Exception(f"All locators failed for element. Tried {len(locators)} strategies.")
                continue
    
    
    def click_with_fallback(self, locators: List[Tuple[str, str]]):
        """Click element using smart locator fallback"""
        element = self.find_element_with_fallback(locators)
        element.click()
        self.logger.info(f"🖱️ Clicked element successfully")
    
    
    def type_with_fallback(self, locators: List[Tuple[str, str]], text: str):
        """Type text into element using smart locator fallback"""
        element = self.find_element_with_fallback(locators)
        element.fill(text)
        self.logger.info(f"⌨️ Typed text: '{text}'")
    
    
    def get_text_with_fallback(self, locators: List[Tuple[str, str]]) -> str:
        """Get text from element using smart locator fallback"""
        element = self.find_element_with_fallback(locators)
        text = element.inner_text()
        self.logger.info(f"📝 Retrieved text: '{text}'")
        return text
    
    
    def navigate_to(self, url: str):
        """Navigate to URL"""
        self.logger.info(f"🌐 Navigating to: {url}")
        self.page.goto(url, wait_until='domcontentloaded')
        try:
            self.page.wait_for_load_state('networkidle', timeout=10000)
        except Exception:
            self.logger.warning("⚠️ networkidle timeout — page has background requests (ads/tracking), continuing...")