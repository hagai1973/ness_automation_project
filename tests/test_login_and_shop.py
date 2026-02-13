"""
E2E Test: Login and Shopping Flow
Tests complete flow with authentication
"""

import pytest
import allure
from playwright.sync_api import Page
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.cart_page import CartPage
import logging


logger = logging.getLogger(__name__)


@allure.epic('E2E Complete Flow')
@allure.feature('Authenticated Shopping')
@allure.story('Login and Purchase Flow')
class TestLoginAndShop:
    """Test class for authenticated shopping flow"""
    
    @allure.title("Complete E2E: Login → Search → Add to Cart → Verify Total")
    @allure.description("""
    This is the most comprehensive test covering the complete user journey:
    1. User logs in with valid credentials
    2. Searches for products within budget
    3. Adds multiple items to cart using hover mechanism
    4. Verifies cart total doesn't exceed budget
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("E2E", "Regression", "Authenticated", "Critical Path")
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_login_search_add_verify(self, page, test_data, ensure_empty_cart):
        """
        Complete E2E Test with Login
        
        Steps:
        1. Login with valid credentials
        2. Search for products
        3. Add items to cart
        4. Verify cart total
        """
        logger.info(f"\n{'#'*60}")
        logger.info(f"🚀 TEST: Login + Search + Add + Verify")
        logger.info(f"{'#'*60}")
        
        # Get test data
        email = test_data['user_credentials']['email']
        password = test_data['user_credentials']['password']
        scenario = test_data['test_scenarios'][0]
        
        # Attach test data to report
        allure.attach(
            f"Email: {email}\nSearch: {scenario['search_query']}\nMax Price: Rs. {scenario['max_price']}\nLimit: {scenario['items_limit']}",
            name="Test Data",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # ========================================
        # STEP 1: Login (skip if already logged in from fixture)
        # ========================================
        with allure.step("STEP 1: Login with valid credentials"):
            logger.info(f"\n{'='*60}")
            logger.info(f"🔐 STEP 1: Login")
            logger.info(f"{'='*60}")
            
            with allure.step("Navigate to home page"):
                home_page = HomePage(page)
                home_page.navigate()
            
            # Check if already logged in (e.g. from ensure_empty_cart fixture)
            if home_page.is_user_logged_in():
                logger.info("✅ Already logged in — skipping login step")
                allure.attach(
                    "Login Status: ALREADY LOGGED IN (from fixture)",
                    name="Login Result",
                    attachment_type=allure.attachment_type.TEXT
                )
            else:
                with allure.step("Click Login link"):
                    home_page.go_to_login()
                
                with allure.step(f"Enter credentials and login as {email}"):
                    login_page = LoginPage(page)
                    login_success = login_page.login(email, password)
                
                with allure.step("Verify login successful"):
                    assert login_success, "Login failed"
                    allure.attach(
                        "Login Status: SUCCESS",
                        name="Login Result",
                        attachment_type=allure.attachment_type.TEXT
                    )
            
            logger.info("✅ Step 1 Complete: Logged in successfully")
        
        # ========================================
        # STEP 2: Search and Add to Cart
        # ========================================
        with allure.step(f"STEP 2: Search for '{scenario['search_query']}' and add to cart"):
            logger.info(f"\n{'='*60}")
            logger.info(f"🛍️ STEP 2: Search and Add to Cart")
            logger.info(f"{'='*60}")
            
            with allure.step("Navigate to Products page"):
                home_page.go_to_products()
            
            with allure.step(f"Search for products: '{scenario['search_query']}'"):
                products_page = ProductsPage(page)
                products_page.search_product(scenario['search_query'])
            
            with allure.step(f"Add items under Rs. {scenario['max_price']} to cart (limit: {scenario['items_limit']})"):
                items_added = products_page.get_products_under_price_and_add_to_cart(
                    scenario['max_price'],
                    scenario['items_limit']
                )
                
                # Attach shopping details
                allure.attach(
                    f"Search Query: {scenario['search_query']}\nMax Price: Rs. {scenario['max_price']}\nItems Added: {items_added}",
                    name="Shopping Details",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            with allure.step(f"Verify items were added ({items_added} items)"):
                assert items_added > 0, "No items added to cart"
            
            logger.info(f"✅ Step 2 Complete: Added {items_added} items")
        
        # ========================================
        # STEP 3: Verify Cart Total
        # ========================================
        with allure.step("STEP 3: Verify cart total within budget"):
            logger.info(f"\n{'='*60}")
            logger.info(f"💰 STEP 3: Verify Cart Total")
            logger.info(f"{'='*60}")
            
            with allure.step("Navigate to cart page"):
                home_page.go_to_cart()
            
            with allure.step(f"Verify total doesn't exceed Rs. {scenario['max_price'] * items_added}"):
                cart_page = CartPage(page)
                result = cart_page.verify_cart_total_not_exceeds(
                    scenario['max_price'],
                    items_added
                )
                
                # Get and attach cart summary
                summary = cart_page.get_cart_summary()
                allure.attach(
                    f"Items: {summary['items_count']}\nTotal: Rs. {summary['total']}\nBudget: Rs. {scenario['max_price'] * items_added}\nStatus: WITHIN BUDGET ✓",
                    name="Cart Verification Summary",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            with allure.step("Assert cart total is within budget"):
                assert result, "Cart total exceeds budget"
            
            logger.info("✅ Step 3 Complete: Cart verified")
        
        # Final success message
        logger.info(f"\n{'#'*60}")
        logger.info(f"🎉 TEST PASSED: Complete authenticated flow!")
        logger.info(f"{'#'*60}\n")