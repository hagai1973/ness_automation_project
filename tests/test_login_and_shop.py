"""
E2E Test: Login and Shopping Flow
─────────────────────────────────
Architecture:
  test_login_and_shop.py  ← assertions + test intent only  (this file)
  auth_service            ← login / logout business logic
  shopping_service        ← search / cart business logic
  pages/                  ← element locators + low-level actions

Each test answers ONE question with ONE assert.
"""

import pytest
import allure
import random
import logging
from services.auth_service import AuthService
from services.shopping_service import ShoppingService

logger = logging.getLogger(__name__)


@allure.epic('E2E Complete Flow')
@allure.feature('Authenticated Shopping')
@allure.story('Login and Purchase Flow')
class TestLoginAndShop:
    """Test class for authenticated shopping flow"""

    # ──────────────────────────────────────────────────────────────────────
    # FIXTURES
    # ──────────────────────────────────────────────────────────────────────

    @pytest.fixture(autouse=True)
    def setup(self, page, test_data, user_credentials, ensure_empty_cart):
        """Initialise services and pick a random scenario."""
        self.auth = AuthService(page)
        self.shop = ShoppingService(page)
        self.scenario = test_data['test_scenarios'][random.randint(0, len(test_data['test_scenarios']) - 1)]
        self.email = user_credentials['email']
        self.password = user_credentials['password']

    # ──────────────────────────────────────────────────────────────────────
    # TESTS  (1 assert each)
    # ──────────────────────────────────────────────────────────────────────

    @allure.title("Login with valid credentials")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_login(self):
        """Authenticated user should be logged in."""
        logger.info("🔐 TEST: Login")

        # ── Act ────────────────────────────────────────────────────────────
        login_page = self.auth.login(self.email, self.password)

        # ── Assert ─────────────────────────────────────────────────────────
        assert login_page.is_logged_in(), "Expected user to be logged in"

    @allure.title("Search and add items to cart under budget")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_search_and_add_to_cart(self):
        """Items matching the search should be added to cart."""
        logger.info(f"🛍️ TEST: Search '{self.scenario['search_query']}' and add to cart")

        # ── Arrange ────────────────────────────────────────────────────────
        self.auth.login(self.email, self.password)

        # ── Act ────────────────────────────────────────────────────────────
        self.items_added = self.shop.search_and_add_to_cart(
            query     = self.scenario['search_query'],
            max_price = self.scenario['max_price'],
            limit     = self.scenario['items_limit']
        )

        # ── Assert ─────────────────────────────────────────────────────────
        assert self.items_added > 0, \
            f"No items added for '{self.scenario['search_query']}' under Rs. {self.scenario['max_price']}"

    @allure.title("Cart total does not exceed budget")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_cart_total_within_budget(self):
        """Cart total should stay within the calculated budget."""
        logger.info("💰 TEST: Verify cart total within budget")

        # ── Arrange ────────────────────────────────────────────────────────
        self.auth.login(self.email, self.password)
        items_added = self.shop.search_and_add_to_cart(
            query     = self.scenario['search_query'],
            max_price = self.scenario['max_price'],
            limit     = self.scenario['items_limit']
        )

        # ── Act ────────────────────────────────────────────────────────────
        result, summary = self.shop.verify_cart_total(
            budget_per_item = self.scenario['max_price'],
            items_count     = items_added
        )

        # ── Assert ─────────────────────────────────────────────────────────
        assert result, \
            f"Cart total Rs. {summary['total']} exceeds budget Rs. {self.scenario['max_price'] * items_added}"