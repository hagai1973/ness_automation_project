"""
Home Page - Landing page navigation
"""

from pages.base_page import BasePage
from typing import List, Tuple


class HomePage(BasePage):
    """Home page object for automationexercise.com"""
    
    # Smart Locators with fallback (2+ locators per element)
    PRODUCTS_LINK: List[Tuple[str, str]] = [
        ('css', 'a[href="/products"]'),
        ('xpath', '//a[contains(@href, "products")]'),
        ('text', 'Products')
    ]
    
    LOGIN_LINK: List[Tuple[str, str]] = [
        ('css', 'a[href="/login"]'),
        ('xpath', '//a[contains(text(), "Signup") or contains(text(), "Login")]'),
        ('text', 'Signup / Login')
    ]
    
    CART_LINK: List[Tuple[str, str]] = [
        ('css', 'a[href="/view_cart"]'),
        ('xpath', '//a[contains(@href, "cart")]'),
        ('text', 'Cart')
    ]
    
    
    def __init__(self, page):
        super().__init__(page)
        self.url = "https://automationexercise.com"
    
    
    def navigate(self):
        """Navigate to home page"""
        self.navigate_to(self.url)
        self.logger.info("🏠 Navigated to Home Page")
    
    
    def go_to_products(self):
        """Click Products link to go to products page"""
        self.logger.info("🛍️ Clicking Products link")
        self.click_with_fallback(self.PRODUCTS_LINK)
        self.page.wait_for_url("**/products")
        self.logger.info("✅ On Products page")
    
    
    def go_to_login(self):
        """Click Login/Signup link"""
        self.logger.info("🔐 Clicking Login link")
        self.click_with_fallback(self.LOGIN_LINK)
    
    
    def go_to_cart(self):
        """Click Cart link to view shopping cart"""
        self.logger.info("🛒 Clicking Cart link")
        self.click_with_fallback(self.CART_LINK)
        self.page.wait_for_url("**/view_cart")
        self.logger.info("✅ On Cart page")
    
    
    def is_user_logged_in(self) -> bool:
        """Check if user is logged in by looking for logout link"""
        try:
            logout_locators = [
                ('css', 'a[href="/logout"]'),
                ('xpath', '//a[contains(text(), "Logout")]')
            ]
            self.find_element_with_fallback(logout_locators, timeout=2000)
            self.logger.info("✅ User is logged in")
            return True
        except:
            self.logger.info("❌ User not logged in")
            return False