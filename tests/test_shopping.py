"""
E2E Shopping Flow Tests for automationexercise.com
Tests: Search -> Add to Cart -> Verify Total
"""

import pytest
import allure
from playwright.sync_api import Page
from pages.home_page import HomePage
from pages.products_page import ProductsPage
from pages.cart_page import CartPage
import logging


logger = logging.getLogger(__name__)


@allure.feature('Shopping Cart')
@allure.story('E2E Shopping Flow')
class TestShoppingFlow:
    """Test class for complete shopping flow"""
    
    @allure.title("Search and add items under budget")
    @allure.description("Test complete shopping flow: search products, add to cart, verify total within budget")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_search_and_add_items_under_budget(self, page, test_data):
        """
        Main E2E Test: Search -> Hover -> Add to Cart -> Verify Total
        
        Steps:
        1. Search for items and add to cart (with hover)
        2. Verify cart total doesn't exceed budget
        """
        # Get first test scenario
        scenario = test_data['test_scenarios'][0]
        
        search_query = scenario['search_query']
        max_price = scenario['max_price']
        items_limit = scenario['items_limit']
        
        logger.info(f"\n{'#'*60}")
        logger.info(f"🚀 TEST: {scenario['test_name']}")
        logger.info(f"{'#'*60}")
        
        with allure.step(f"Search and add items: '{search_query}' under Rs. {max_price}"):
            # STEP 1: Search and add items to cart
            items_added = self.search_and_add_items_to_cart(
                page, 
                search_query, 
                max_price, 
                items_limit
            )
            
            # Attach info to report
            allure.attach(
                f"Search Query: {search_query}\nMax Price: Rs. {max_price}\nItems Added: {items_added}",
                name="Search Details",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # Verify we added items
        assert items_added > 0, f"No items added for '{search_query}' under Rs. {max_price}"
        logger.info(f"✅ Step 1 Complete: Added {items_added} items to cart")
        
        with allure.step(f"Verify cart total doesn't exceed budget (Rs. {max_price * items_added})"):
            # STEP 2: Verify cart total
            self.assert_cart_total_not_exceeds(page, max_price, items_added)
            logger.info(f"✅ Step 2 Complete: Cart total verified")
        
        logger.info(f"\n{'#'*60}")
        logger.info(f"🎉 TEST PASSED: {scenario['test_name']}")
        logger.info(f"{'#'*60}")
    
    
    def search_and_add_items_to_cart(
        self, 
        page: Page, 
        query: str, 
        max_price: float, 
        limit: int = 5
    ) -> int:
        """
        Combined Function: Search for items and add to cart with hover
        
        Args:
            page: Playwright page object
            query: Search term (e.g., 'tshirt')
            max_price: Maximum price threshold
            limit: Maximum number of items to add
            
        Returns:
            Number of items added to cart
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🔍 FUNCTION 1: Search and Add Items to Cart")
        logger.info(f"   Query: '{query}' | Max Price: Rs. {max_price} | Limit: {limit}")
        logger.info(f"{'='*60}")
        
        # Navigate to home page
        home_page = HomePage(page)
        home_page.navigate()
        
        # Go to products page
        home_page.go_to_products()
        
        # Search for products
        products_page = ProductsPage(page)
        products_page.search_product(query)
        
        # Add products to cart (with hover + click)
        items_added = products_page.get_products_under_price_and_add_to_cart(max_price, limit)
        
        logger.info(f"✅ Added {items_added} products to cart")
        return items_added
    
    
    def assert_cart_total_not_exceeds(
        self, 
        page: Page, 
        budget_per_item: float, 
        items_count: int
    ) -> None:
        """
        Core Function 2: Verify cart total doesn't exceed budget
        
        Args:
            page: Playwright page object
            budget_per_item: Maximum price per item
            items_count: Number of items in cart
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ FUNCTION 2: Assert Cart Total Not Exceeds")
        logger.info(f"   Budget per item: Rs. {budget_per_item}")
        logger.info(f"   Items count: {items_count}")
        logger.info(f"{'='*60}")
        
        # Navigate to cart
        home_page = HomePage(page)
        home_page.go_to_cart()
        
        # Verify total
        cart_page = CartPage(page)
        result = cart_page.verify_cart_total_not_exceeds(budget_per_item, items_count)
        
        # Get cart summary
        summary = cart_page.get_cart_summary()
        
        logger.info(f"\n📊 Cart Summary:")
        logger.info(f"   Items in cart: {summary['items_count']}")
        logger.info(f"   Total amount: Rs. {summary['total']}")
        logger.info(f"   Budget limit: Rs. {budget_per_item * items_count}")
        
        # Attach to Allure report
        allure.attach(
            f"Items: {summary['items_count']}\nTotal: Rs. {summary['total']}\nBudget: Rs. {budget_per_item * items_count}",
            name="Cart Summary",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Assert
        assert result, f"Cart total Rs. {summary['total']} exceeds budget Rs. {budget_per_item * items_count}"
        logger.info(f"✅ PASSED: Cart total is within budget!")