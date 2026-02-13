"""
Products Page - Search, filter by price, collect product URLs
"""

from pages.base_page import BasePage
from typing import List, Tuple
import re


class ProductsPage(BasePage):
    """Products page with search and filtering capabilities"""
    
    # Smart Locators with fallback
    SEARCH_INPUT: List[Tuple[str, str]] = [
        ('css', '#search_product'),
        ('xpath', '//input[@id="search_product"]'),
        ('xpath', '//input[@placeholder="Search Product"]')
    ]
    
    SEARCH_BUTTON: List[Tuple[str, str]] = [
        ('css', '#submit_search'),
        ('xpath', '//button[@id="submit_search"]'),
        ('xpath', '//button[contains(@class, "btn-default")]')
    ]
    
    PRODUCT_ITEMS: List[Tuple[str, str]] = [
        ('css', '.productinfo'),
        ('xpath', '//div[contains(@class, "productinfo")]'),
        ('xpath', '//div[@class="col-sm-4"]//div[@class="productinfo text-center"]')
    ]
    
    PRODUCT_LINKS: List[Tuple[str, str]] = [
        ('css', '.productinfo a[href*="product_details"]'),
        ('xpath', '//div[@class="productinfo"]//a[contains(@href, "product_details")]'),
        ('xpath', '//a[contains(text(), "View Product")]')
    ]
    
    PRODUCT_PRICES: List[Tuple[str, str]] = [
        ('css', '.productinfo h2'),
        ('xpath', '//div[@class="productinfo"]//h2'),
        ('xpath', '//h2[contains(text(), "Rs.")]')
    ]
    
    CONTINUE_SHOPPING_BTN: List[Tuple[str, str]] = [
        ('css', 'button[data-dismiss="modal"]'),
        ('xpath', '//button[contains(text(), "Continue Shopping")]'),
        ('xpath', '//button[@data-dismiss="modal"]')
    ]
    
    
    def __init__(self, page):
        super().__init__(page)
    
    
    def search_product(self, query: str):
        """
        Search for products by query
        
        Args:
            query: Search term (e.g., 'tshirt', 'dress')
        """
        self.logger.info(f"🔍 Searching for: '{query}'")
        self.type_with_fallback(self.SEARCH_INPUT, query)
        self.click_with_fallback(self.SEARCH_BUTTON)
        self.page.wait_for_load_state('networkidle')
        self.logger.info(f"✅ Search completed for '{query}'")
    
    
    def extract_price(self, price_text: str) -> float:
        """
        Extract numeric price from text like 'Rs. 500' or 'Rs.1000'
        
        Args:
            price_text: Text containing price (e.g., 'Rs. 500')
            
        Returns:
            float: Numeric price value
        """
        # Remove 'Rs.' and any whitespace, extract numbers
        match = re.search(r'[\d,]+', price_text)
        if match:
            price = float(match.group().replace(',', ''))
            return price
        return 0.0
    
    
    def get_products_under_price_and_add_to_cart(self, max_price: float, limit: int = 5) -> int:
        """
            Get products under price and add them to cart directly
            Uses hover + click approach for the product listing page
            
            Args:
                max_price: Maximum price threshold
                limit: Maximum number of products to add
                
            Returns:
                Number of products added to cart
        """
        self.logger.info(f"💰 Filtering and adding products under Rs. {max_price}, limit: {limit}")
        
        added_count = 0
        
        try:
            # Get all product containers
            products = self.page.locator('.single-products').all()
            self.logger.info(f"📦 Found {len(products)} total products")
            
            for index, product in enumerate(products):
                if added_count >= limit:
                    break
                
                try:
                    # Get price
                    price_element = product.locator('.productinfo h2').first
                    price_text = price_element.inner_text()
                    price = self.extract_price(price_text)
                    
                    self.logger.info(f"   Product {index+1}: Price = Rs. {price}")
                    
                    # Check if price is under threshold
                    if price <= max_price and price > 0:
                        # Get product name
                        try:
                            name_element = product.locator('.productinfo p').first
                            product_name = name_element.inner_text()
                        except:
                            product_name = f"Product {index+1}"
                        
                        self.logger.info(f"   ✅ Adding: {product_name} - Rs. {price}")
                        
                        # STEP 1: Hover over the product to reveal "Add to cart" button
                        self.logger.info(f"   🖱️ Hovering over product...")
                        product.hover()
                        
                        # Wait a bit for the overlay to appear
                        import time
                        time.sleep(0.5)
                        
                        # STEP 2: Click "Add to cart" button
                        add_to_cart_btn = product.locator('a.add-to-cart').first
                        add_to_cart_btn.wait_for(state='visible', timeout=3000)
                        
                        self.logger.info(f"   🛒 Clicking 'Add to cart'...")
                        add_to_cart_btn.click()
                        
                        # Wait for modal to appear
                        time.sleep(1)
                        
                        # Take screenshot
                        timestamp = int(time.time())
                        self.page.screenshot(path=f"screenshots/added_to_cart_{added_count+1}_{timestamp}.png")
                        
                        # Close modal - click "Continue Shopping"
                        self.close_modal_if_present()
                        
                        added_count += 1
                        self.logger.info(f"   ✅ Added to cart ({added_count}/{limit})")
                        
                    else:
                        self.logger.info(f"   ❌ Skipped: Price Rs. {price} exceeds limit Rs. {max_price}")
                
                except Exception as e:
                    self.logger.warning(f"   ⚠️ Error processing product {index+1}: {str(e)}")
                    continue
            
            self.logger.info(f"✅ Successfully added {added_count} products to cart")
            
        except Exception as e:
            self.logger.error(f"❌ Error adding products to cart: {str(e)}")
            self.page.screenshot(path=f"screenshots/add_to_cart_error.png")
        
        return added_count
    
    
    def close_modal_if_present(self):
        """Close 'Continue Shopping' modal if it appears after adding to cart"""
        try:
            self.logger.info("🔍 Checking for modal...")
            modal = self.page.locator('button[data-dismiss="modal"]').first
            if modal.is_visible(timeout=2000):
                modal.click()
                self.logger.info("✅ Modal closed")
        except:
            self.logger.info("ℹ️ No modal found")