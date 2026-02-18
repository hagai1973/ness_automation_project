"""
Shopping Service
----------------
Business logic layer for all shopping-related flows.

Sits between tests and page objects:
  tests/ --> services/ --> pages/

Responsibilities:
  - Orchestrate multi-step search / add-to-cart / cart verification flows
  - Accept business-level parameters (query, budget, limit)
  - Return results so tests can run assertions
  - Never assert here — assertions belong in tests only
"""

from playwright.sync_api import Page
from pages.home_page import HomePage
from pages.products_page import ProductsPage
from pages.cart_page import CartPage
import logging
import allure

logger = logging.getLogger(__name__)


class ShoppingService:
    """
    Encapsulates all shopping business logic.

    Usage:
        shop = ShoppingService(page)
        items = shop.search_and_add_to_cart("tshirt", 1500, 3)
        result, summary = shop.verify_cart_total(1500, items)
    """

    def __init__(self, page: Page):
        self.page          = page
        self.home_page     = HomePage(page)
        self.products_page = ProductsPage(page)
        self.cart_page     = CartPage(page)

    # ──────────────────────────────────────────────────────────────────────
    # PUBLIC ACTIONS
    # ──────────────────────────────────────────────────────────────────────

    @allure.step("SHOPPING SERVICE: Search '{query}' and add to cart (max Rs.{max_price}, limit {limit})")
    def search_and_add_to_cart(self, query: str, max_price: float, limit: int = 5) -> int:
        """
        Search for products and add matching ones to cart.

        Args:
            query:     Search term (e.g., 'tshirt')
            max_price: Maximum price threshold
            limit:     Maximum number of items to add

        Returns:
            int: Number of items added to cart
        """
        logger.info(f"🔍 ShoppingService.search_and_add_to_cart() → '{query}' | Rs.{max_price} | limit={limit}")

        self.home_page.go_to_products()
        self.products_page.search_product(query)
        items_added = self.products_page.get_products_under_price_and_add_to_cart(max_price, limit)

        logger.info(f"✅ ShoppingService: Added {items_added} items to cart")
        return items_added

    @allure.step("SHOPPING SERVICE: Verify cart total within budget")
    def verify_cart_total(self, budget_per_item: float, items_count: int) -> tuple:
        """
        Navigate to cart and check total against budget.

        Args:
            budget_per_item: Maximum price per item
            items_count:     Number of items in cart

        Returns:
            tuple: (is_within_budget: bool, summary: dict)
        """
        logger.info(f"💰 ShoppingService.verify_cart_total() → Rs.{budget_per_item} × {items_count}")

        self.home_page.go_to_cart()
        result  = self.cart_page.verify_cart_total_not_exceeds(budget_per_item, items_count)
        summary = self.cart_page.get_cart_summary()

        logger.info(f"📊 Cart: {summary['items_count']} items, Rs.{summary['total']} "
                     f"(budget Rs.{budget_per_item * items_count})")
        return result, summary


# ──────────────────────────────────────────────────────────────────────────
# STANDALONE HELPERS (used by test_shopping.py which doesn't need a class)
# ──────────────────────────────────────────────────────────────────────────

def search_and_add_items_to_cart(page: Page, query: str, max_price: float, limit: int = 5) -> int:
    """Convenience wrapper: creates a ShoppingService and searches."""
    shop = ShoppingService(page)
    shop.home_page.navigate()
    return shop.search_and_add_to_cart(query, max_price, limit)


def assert_cart_total_not_exceeds(page: Page, budget_per_item: float, items_count: int) -> None:
    """Convenience wrapper: verifies cart total and asserts."""
    shop = ShoppingService(page)
    result, summary = shop.verify_cart_total(budget_per_item, items_count)
    assert result, f"Cart total Rs. {summary['total']} exceeds budget Rs. {budget_per_item * items_count}"