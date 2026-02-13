"""
E2E Test: Login and Shopping Flow
Tests complete flow with authentication
"""

import pytest
from playwright.sync_api import Page
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.cart_page import CartPage
import logging


logger = logging.getLogger(__name__)


class TestLoginAndShop:
    """Test class for authenticated shopping flow"""
    
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_login_search_add_verify(self, page, test_data):
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
        
        # STEP 1: Login
        logger.info(f"\n{'='*60}")
        logger.info(f"🔐 STEP 1: Login")
        logger.info(f"{'='*60}")
        
        home_page = HomePage(page)
        home_page.navigate()
        home_page.go_to_login()
        
        login_page = LoginPage(page)
        login_success = login_page.login(email, password)
        
        assert login_success, "Login failed"
        logger.info("✅ Step 1 Complete: Logged in successfully")
        
        # STEP 2: Search and add to cart
        logger.info(f"\n{'='*60}")
        logger.info(f"🛍️ STEP 2: Search and Add to Cart")
        logger.info(f"{'='*60}")
        
        home_page.go_to_products()
        
        products_page = ProductsPage(page)
        products_page.search_product(scenario['search_query'])
        
        items_added = products_page.get_products_under_price_and_add_to_cart(
            scenario['max_price'],
            scenario['items_limit']
        )
        
        assert items_added > 0, "No items added to cart"
        logger.info(f"✅ Step 2 Complete: Added {items_added} items")
        
        # STEP 3: Verify cart
        logger.info(f"\n{'='*60}")
        logger.info(f"💰 STEP 3: Verify Cart Total")
        logger.info(f"{'='*60}")
        
        home_page.go_to_cart()
        
        cart_page = CartPage(page)
        result = cart_page.verify_cart_total_not_exceeds(
            scenario['max_price'],
            items_added
        )
        
        assert result, "Cart total exceeds budget"
        logger.info("✅ Step 3 Complete: Cart verified")
        
        logger.info(f"\n{'#'*60}")
        logger.info(f"🎉 TEST PASSED: Complete authenticated flow!")
        logger.info(f"{'#'*60}\n")