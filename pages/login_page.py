"""
Login Page - User authentication
"""

from pages.base_page import BasePage
from typing import List, Tuple
import time


class LoginPage(BasePage):
    """Login page for user authentication"""
    
    # Smart Locators with fallback
    EMAIL_INPUT: List[Tuple[str, str]] = [
        ('css', 'input[data-qa="login-email"]'),
        ('xpath', '//input[@data-qa="login-email"]'),
        ('xpath', '//form[@action="/login"]//input[@name="email"]')
    ]
    
    PASSWORD_INPUT: List[Tuple[str, str]] = [
        ('css', 'input[data-qa="login-password"]'),
        ('xpath', '//input[@data-qa="login-password"]'),
        ('xpath', '//form[@action="/login"]//input[@type="password"]')
    ]
    
    LOGIN_BUTTON: List[Tuple[str, str]] = [
        ('css', 'button[data-qa="login-button"]'),
        ('xpath', '//button[@data-qa="login-button"]'),
        ('xpath', '//button[contains(text(), "Login")]')
    ]
    
    LOGIN_ERROR: List[Tuple[str, str]] = [
        ('css', 'p[style*="color: red"]'),
        ('xpath', '//p[contains(@style, "color: red")]'),
        ('xpath', '//p[contains(text(), "incorrect")]')
    ]
    
    LOGGED_IN_USER: List[Tuple[str, str]] = [
        ('css', 'a[href="/logout"]'),
        ('xpath', '//a[contains(text(), "Logout")]'),
        ('xpath', '//li/a[@href="/logout"]')
    ]
    
    
    def __init__(self, page):
        super().__init__(page)
        self.url = "https://automationexercise.com/login"
    
    
    def navigate_to_login(self):
        """Navigate to login page"""
        self.logger.info("🔐 Navigating to Login page")
        self.navigate_to(self.url)
    
    
    def login(self, email: str, password: str) -> bool:
        """
        Login with email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            self.logger.info(f"🔐 Attempting login with email: {email}")
            
            # Enter email
            self.logger.info("📧 Entering email...")
            self.type_with_fallback(self.EMAIL_INPUT, email)
            
            # Enter password
            self.logger.info("🔒 Entering password...")
            self.type_with_fallback(self.PASSWORD_INPUT, password)
            
            # Take screenshot before login
            timestamp = int(time.time())
            self.page.screenshot(path=f"screenshots/before_login_{timestamp}.png")
            self.logger.info(f"📸 Screenshot saved: before_login_{timestamp}.png")
            
            # Click login button
            self.logger.info("🖱️ Clicking Login button...")
            self.click_with_fallback(self.LOGIN_BUTTON)
            
            # Wait for navigation
            time.sleep(2)
            
            # Check if login was successful
            if self.is_logged_in():
                self.logger.info("✅ Login successful!")
                
                # Take screenshot after successful login
                self.page.screenshot(path=f"screenshots/after_login_{timestamp}.png")
                self.logger.info(f"📸 Screenshot saved: after_login_{timestamp}.png")
                
                return True
            else:
                # Check for error message
                try:
                    error_msg = self.get_text_with_fallback(self.LOGIN_ERROR)
                    self.logger.error(f"❌ Login failed: {error_msg}")
                except:
                    self.logger.error("❌ Login failed: Unknown error")
                
                # Take screenshot of error
                self.page.screenshot(path=f"screenshots/login_error_{timestamp}.png")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Login failed with exception: {str(e)}")
            self.page.screenshot(path=f"screenshots/login_exception_{int(time.time())}.png")
            return False
    
    
    def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in
        
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            self.find_element_with_fallback(self.LOGGED_IN_USER, timeout=3000)
            self.logger.info("✅ User is logged in (Logout link visible)")
            return True
        except:
            self.logger.info("❌ User is not logged in (Logout link not found)")
            return False
    
    
    def logout(self):
        """Logout the current user"""
        try:
            self.logger.info("🚪 Logging out...")
            self.click_with_fallback(self.LOGGED_IN_USER)
            time.sleep(1)
            self.logger.info("✅ Logged out successfully")
        except Exception as e:
            self.logger.error(f"❌ Logout failed: {str(e)}")
    
    
    def get_logged_in_username(self) -> str:
        """
        Get the username of logged in user
        
        Returns:
            str: Username or empty string if not logged in
        """
        try:
            # Username is usually displayed near the logout link
            username_text = self.get_text_with_fallback(self.LOGGED_IN_USER)
            # Extract just the username (remove "Logout as " prefix if exists)
            return username_text.strip()
        except:
            return ""