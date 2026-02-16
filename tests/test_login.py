"""
Login functionality tests
"""

import pytest
import allure
from pages.home_page import HomePage
from pages.login_page import LoginPage
import logging


logger = logging.getLogger(__name__)


@allure.feature('Authentication')
@allure.story('User Login')
class TestLogin:
    """Test class for login functionality"""
    
    @allure.title("Successful login with valid credentials")
    @allure.description("Test that user can login successfully with valid email and password")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_successful_login(self, page, user_credentials):
        """Test: Successful login with valid credentials"""
        logger.info(f"\n{'#'*60}")
        logger.info(f"🔐 TEST: Successful Login")
        logger.info(f"{'#'*60}")
        
        # Get credentials from .env
        email = user_credentials['email']
        password = user_credentials['password']
        
        with allure.step("Navigate to login page"):
            home_page = HomePage(page)
            home_page.navigate()
            home_page.go_to_login()
        
        with allure.step(f"Login with email: {email}"):
            login_page = LoginPage(page)
            login_success = login_page.login(email, password)
        
        with allure.step("Verify login successful"):
            assert login_success, "Login failed with valid credentials"
            assert login_page.is_logged_in(), "User is not logged in after successful login"
        
        logger.info(f"✅ TEST PASSED: User logged in successfully")
        logger.info(f"{'#'*60}\n")
    
    
    @allure.title("Login fails with invalid credentials")
    @allure.description("Test that login properly fails when using invalid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_login_with_invalid_credentials(self, page):
        """Test: Login fails with invalid credentials"""
        logger.info(f"\n{'#'*60}")
        logger.info(f"🔐 TEST: Login with Invalid Credentials")
        logger.info(f"{'#'*60}")
        
        with allure.step("Navigate to login page"):
            login_page = LoginPage(page)
            login_page.navigate_to_login()
        
        with allure.step("Attempt login with invalid credentials"):
            login_success = login_page.login("invalid@test.com", "wrongpassword")
        
        with allure.step("Verify login failed"):
            assert not login_success, "Login should fail with invalid credentials"
            assert not login_page.is_logged_in(), "User should not be logged in"
        
        logger.info(f"✅ TEST PASSED: Login correctly failed with invalid credentials")
        logger.info(f"{'#'*60}\n")
    
    
    @allure.title("Logout functionality")
    @allure.description("Test that user can successfully logout after logging in")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_logout(self, page, user_credentials):
        """Test: Logout functionality"""
        logger.info(f"\n{'#'*60}")
        logger.info(f"🚪 TEST: Logout Functionality")
        logger.info(f"{'#'*60}")
        
        email = user_credentials['email']
        password = user_credentials['password']
        
        with allure.step("Login first"):
            login_page = LoginPage(page)
            login_page.navigate_to_login()
            login_page.login(email, password)
            assert login_page.is_logged_in(), "User should be logged in before logout"
        
        with allure.step("Logout"):
            login_page.logout()
        
        with allure.step("Verify logged out"):
            assert not login_page.is_logged_in(), "User should be logged out"
        
        logger.info(f"✅ TEST PASSED: Logout successful")
        logger.info(f"{'#'*60}\n")