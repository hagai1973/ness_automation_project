"""
Product Detail Page - View product details and add to cart
"""

from pages.base_page import BasePage
from typing import List, Tuple
import time


class ProductDetailPage(BasePage):
    """Product detail page for adding items to cart"""
    
    # Smart Locators with fallback
    ADD_TO_CART_BTN: List[Tuple[str, str]] = [
        ('css', 'button.cart'),
        ('xpath', '//button[contains(@class, "cart")]'),
        ('xpath', '//button[contains(text(), "Add to cart")]')
    ]
    
    QUANTITY_INPUT: List[Tuple[str, str]] = [
        ('css', '#quantity'),
        ('xpath', '//input[@id="quantity"]'),
        ('xpath', '//input[@name="quantity"]')
    ]
    
    PRODUCT_NAME: List[Tuple[str, str]] = [
        ('css', '.product-information h2'),
        ('xpath', '//div[@class="product-information"]//h2'),
        ('xpath', '//h2[contains(@class, "product")]')
    ]
    
    PRODUCT_PRICE: List[Tuple[str, str]] = [
        ('css', '.product-information span span'),
        ('xpath', '//div[@class="product-information"]//span/span'),
        ('xpath', '//span[contains(text(), "Rs.")]')
    ]
    
    CONTINUE_SHOPPING_BTN: List[Tuple[str, str]] = [
        ('css', 'button[data-dismiss="modal"]'),
        ('xpath', '//button[contains(text(), "Continue Shopping")]'),
        ('xpath', '//button[@data-dismiss="modal"]')
    ]
    
    VIEW_CART_BTN: List[Tuple[str, str]] = [
        ('css', 'a[href="/view_cart"] u'),
        ('xpath', '//a[contains(@href, "view_cart")]//u'),
        ('xpath', '//u[contains(text(), "View Cart")]')
    ]
    
    
    def __init__(self, page):
        super().__init__(page)
    
    
    def navigate_to_product(self, product_url: str):
        """
        Navigate to specific product detail page
        
        Args:
            product_url: Full URL of product
        """
        self.logger.info(f"🌐 Navigating to product: {product_url}")
        self.navigate_to(product_url)
    
    
    def get_product_name(self) -> str:
        """Get product name from detail page"""
        try:
            name = self.get_text_with_fallback(self.PRODUCT_NAME)
            return name
        except:
            return "Unknown Product"
    
    
    def get_product_price(self) -> str:
        """Get product price from detail page"""
        try:
            price = self.get_text_with_fallback(self.PRODUCT_PRICE)
            return price
        except:
            return "Rs. 0"
    
    
    def set_quantity(self, quantity: int = 1):
        """
        Set product quantity
        
        Args:
            quantity: Number of items to add (default: 1)
        """
        try:
            self.logger.info(f"🔢 Setting quantity to: {quantity}")
            element = self.find_element_with_fallback(self.QUANTITY_INPUT)
            element.clear()
            element.fill(str(quantity))
            self.logger.info(f"✅ Quantity set to {quantity}")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not set quantity: {str(e)}")
    
    
    def add_to_cart(self):
        """
        Click 'Add to Cart' button
        Handles modal that appears after adding
        """
        try:
            product_name = self.get_product_name()
            product_price = self.get_product_price()
            
            self.logger.info(f"🛒 Adding to cart: {product_name} - {product_price}")
            
            # Click Add to Cart
            self.click_with_fallback(self.ADD_TO_CART_BTN)
            
            # Wait for modal to appear
            time.sleep(1)
            
            # Take screenshot
            timestamp = int(time.time())
            self.page.screenshot(path=f"screenshots/added_to_cart_{timestamp}.png")
            self.logger.info(f"📸 Screenshot saved: added_to_cart_{timestamp}.png")
            
            # Close modal by clicking "Continue Shopping"
            self.close_add_to_cart_modal()
            
            self.logger.info(f"✅ Successfully added to cart: {product_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add to cart: {str(e)}")
            self.page.screenshot(path=f"screenshots/add_to_cart_error_{int(time.time())}.png")
            raise
    
    
    def close_add_to_cart_modal(self):
        """Close the modal that appears after adding item to cart"""
        try:
            self.logger.info("🔍 Looking for 'Continue Shopping' button...")
            
            # Wait for modal to be visible
            modal_btn = self.page.locator('button[data-dismiss="modal"]').first
            modal_btn.wait_for(state='visible', timeout=5000)
            
            # Click Continue Shopping
            modal_btn.click()
            self.logger.info("✅ Clicked 'Continue Shopping'")
            
            # Wait for modal to close
            time.sleep(0.5)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not close modal: {str(e)}")
            # Try alternative: press Escape
            try:
                self.page.keyboard.press('Escape')
                self.logger.info("✅ Closed modal with Escape key")
            except:
                self.logger.warning("⚠️ Modal handling failed, continuing anyway")
    
    
    def go_to_cart_from_modal(self):
        """Click 'View Cart' from the modal after adding to cart"""
        try:
            self.logger.info("🛒 Clicking 'View Cart' from modal")
            self.click_with_fallback(self.VIEW_CART_BTN)
            self.page.wait_for_url("**/view_cart")
            self.logger.info("✅ Navigated to cart")
        except Exception as e:
            self.logger.error(f"❌ Failed to navigate to cart: {str(e)}")