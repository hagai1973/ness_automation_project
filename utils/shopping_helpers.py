"""
Shopping flow helper functions
"""

from playwright.sync_api import Page
from pages.home_page import HomePage
from pages.products_page import ProductsPage
from pages.cart_page import CartPage
import logging
import allure

logger = logging.getLogger(__name__)


def search_and_add_items_to_cart(
    page: Page, 
    query: str, 
    max_price: float, 
    limit: int = 5
) -> int:
    """
    Search for items and add to cart with hover
    
    Args:
        page: Playwright page object
        query: Search term (e.g., 'tshirt')
        max_price: Maximum price threshold
        limit: Maximum number of items to add
        
    Returns:
        Number of items added to cart
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🔍 Search and Add Items to Cart")
    logger.info(f"   Query: '{query}' | Max Price: Rs. {max_price} | Limit: {limit}")
    logger.info(f"{'='*60}")
    
    home_page = HomePage(page)
    home_page.navigate()
    home_page.go_to_products()
    
    products_page = ProductsPage(page)
    products_page.search_product(query)
    
    items_added = products_page.get_products_under_price_and_add_to_cart(max_price, limit)
    
    logger.info(f"✅ Added {items_added} products to cart")
    return items_added


def assert_cart_total_not_exceeds(
    page: Page, 
    budget_per_item: float, 
    items_count: int
) -> None:
    """
    Verify cart total doesn't exceed budget
    
    Args:
        page: Playwright page object
        budget_per_item: Maximum price per item
        items_count: Number of items in cart
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Assert Cart Total Not Exceeds")
    logger.info(f"   Budget per item: Rs. {budget_per_item}")
    logger.info(f"   Items count: {items_count}")
    logger.info(f"{'='*60}")
    
    home_page = HomePage(page)
    home_page.go_to_cart()
    
    cart_page = CartPage(page)
    result = cart_page.verify_cart_total_not_exceeds(budget_per_item, items_count)
    
    summary = cart_page.get_cart_summary()
    
    logger.info(f"\n📊 Cart Summary:")
    logger.info(f"   Items in cart: {summary['items_count']}")
    logger.info(f"   Total amount: Rs. {summary['total']}")
    logger.info(f"   Budget limit: Rs. {budget_per_item * items_count}")
    
    allure.attach(
        f"Items: {summary['items_count']}\nTotal: Rs. {summary['total']}\nBudget: Rs. {budget_per_item * items_count}",
        name="Cart Summary",
        attachment_type=allure.attachment_type.TEXT
    )
    
    assert result, f"Cart total Rs. {summary['total']} exceeds budget Rs. {budget_per_item * items_count}"
    logger.info(f"✅ PASSED: Cart total is within budget!")