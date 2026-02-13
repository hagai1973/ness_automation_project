"""
Login functionality tests
"""

import pytest
from playwright.sync_api import Page
from pages.home_page import HomePage
from pages.login_page import LoginPage
import logging


logger = logging.getLogger(__name__)


class TestLogin:
    """Test class for login functionality"""
    
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_successful_login(self, page, test_data):
        """
        Test: Successful login with valid credentials
        
        Steps:
        1. Navigate to login page
        2. Enter valid credentials
        3. Verify login success
        """
        logger.info(f"\n{'#'*60}")
        logger.info(f"🔐 TEST: Successful Login")
        logger.info(f"{'#'*60}")
        
        # Get credentials from test data
        email = test_data['user_credentials']['email']
        password = test_data['user_credentials']['password']
        
        # Navigate to home page first
        home_page = HomePage(page)
        home_page.navigate()
        
        # Go to login page
        home_page.go_to_login()
        
        # Login
        login_page = LoginPage(page)
        login_success = login_page.login(email, password)
        
        # Verify login
        assert login_success, "Login failed with valid credentials"
        assert login_page.is_logged_in(), "User is not logged in after successful login"
        
        logger.info(f"✅ TEST PASSED: User logged in successfully")
        logger.info(f"{'#'*60}\n")
    
    
    @pytest.mark.smoke
    def test_login_with_invalid_credentials(self, page):
        """
        Test: Login fails with invalid credentials
        
        Steps:
        1. Navigate to login page
        2. Enter invalid credentials
        3. Verify login fails with error message
        """
        logger.info(f"\n{'#'*60}")
        logger.info(f"🔐 TEST: Login with Invalid Credentials")
        logger.info(f"{'#'*60}")
        
        # Navigate to login page
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        
        # Try to login with invalid credentials
        login_success = login_page.login("invalid@test.com", "wrongpassword")
        
        # Verify login failed
        assert not login_success, "Login should fail with invalid credentials"
        assert not login_page.is_logged_in(), "User should not be logged in"
        
        logger.info(f"✅ TEST PASSED: Login correctly failed with invalid credentials")
        logger.info(f"{'#'*60}\n")
    
    
    @pytest.mark.regression
    def test_logout(self, page, test_data):
        """
        Test: Logout functionality
        
        Steps:
        1. Login with valid credentials
        2. Logout
        3. Verify logout success
        """
        logger.info(f"\n{'#'*60}")
        logger.info(f"🚪 TEST: Logout Functionality")
        logger.info(f"{'#'*60}")
        
        # Get credentials
        email = test_data['user_credentials']['email']
        password = test_data['user_credentials']['password']
        
        # Login first
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login(email, password)
        
        # Verify logged in
        assert login_page.is_logged_in(), "User should be logged in before logout"
        
        # Logout
        login_page.logout()
        
        # Verify logged out
        assert not login_page.is_logged_in(), "User should be logged out"
        
        logger.info(f"✅ TEST PASSED: Logout successful")
        logger.info(f"{'#'*60}\n")