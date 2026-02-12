"""
E2E Shopping Flow Tests for automationexercise.com
Tests: Search -> Add to Cart -> Verify Total
"""

import pytest
import json
from pathlib import Path


class TestShoppingFlow:
    """Test class for complete shopping flow"""
    
    @pytest.fixture(scope="class")
    def test_data(self):
        """Load test data from JSON file"""
        data_file = Path(__file__).parent.parent / "data" / "search_data.json"
        with open(data_file, 'r') as f:
            return json.load(f)
    
    
    def test_search_and_add_items_under_budget(self, test_data):
        """
        Test: Search items, add to cart, verify total within budget
        
        Steps:
        1. Search for items under max price
        2. Add items to cart
        3. Verify cart total doesn't exceed budget
        """
        # Get first test scenario
        scenario = test_data['test_scenarios'][0]
        
        search_query = scenario['search_query']
        max_price = scenario['max_price']
        items_limit = scenario['items_limit']
        
        print(f"\n🔍 Test Scenario: {scenario['test_name']}")
        print(f"   Search: '{search_query}' | Max Price: {max_price} | Limit: {items_limit}")
        
        # TODO: Step 1 - Search for items
        # item_urls = search_items_by_name_under_price(search_query, max_price, items_limit)
        
        # TODO: Step 2 - Add items to cart
        # add_items_to_cart(item_urls)
        
        # TODO: Step 3 - Verify cart total
        # assert_cart_total_not_exceeds(max_price, len(item_urls))
        
        # Placeholder assertion for now
        assert True, "Test structure created successfully!"