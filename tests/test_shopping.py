"""
E2E Shopping Flow Tests for automationexercise.com
"""

import pytest
import allure
from services.shopping_service import search_and_add_items_to_cart, assert_cart_total_not_exceeds
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
    @pytest.mark.parametrize("scenario_index", [0, 1, 2], ids=[
        "tshirt_under_budget",
        "dress_under_budget",
        "top_under_budget"
    ])
    def test_search_and_add_items_under_budget(self, page, test_data, scenario_index):
        """Main E2E Test: Search -> Hover -> Add to Cart -> Verify Total"""
        scenario = test_data['test_scenarios'][scenario_index]
        
        search_query = scenario['search_query']
        max_price = scenario['max_price']
        items_limit = scenario['items_limit']
        
        logger.info(f"\n{'#'*60}")
        logger.info(f"🚀 TEST: {scenario['test_name']}")
        logger.info(f"{'#'*60}")

        # ── Act ────────────────────────────────────────────────────────────
        with allure.step(f"Search and add items: '{search_query}' under Rs. {max_price}"):
            items_added = search_and_add_items_to_cart(page, search_query, max_price, items_limit)
            
            allure.attach(
                f"Search Query: {search_query}\nMax Price: Rs. {max_price}\nItems Added: {items_added}",
                name="Search Details",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # ── Assert ─────────────────────────────────────────────────────────
        assert items_added > 0, f"No items added for '{search_query}' under Rs. {max_price}"
        
        with allure.step(f"Verify cart total doesn't exceed budget (Rs. {max_price * items_added})"):
            assert_cart_total_not_exceeds(page, max_price, items_added)
        
        logger.info(f"🎉 TEST PASSED: {scenario['test_name']}")