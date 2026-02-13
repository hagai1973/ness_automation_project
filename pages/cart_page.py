"""
Cart Page - View cart items and verify total amount
"""

from pages.base_page import BasePage
from typing import List, Tuple
import re
import time


class CartPage(BasePage):
    """Cart page for viewing items and verifying totals"""
    
    # Smart Locators with fallback
    CART_ITEMS: List[Tuple[str, str]] = [
        ('css', '#cart_info tbody tr'),
        ('xpath', '//table[@id="cart_info"]//tbody//tr'),
        ('xpath', '//tr[contains(@id, "product")]')
    ]
    
    ITEM_PRICES: List[Tuple[str, str]] = [
        ('css', '.cart_price p'),
        ('xpath', '//td[@class="cart_price"]//p'),
        ('xpath', '//p[contains(text(), "Rs.")]')
    ]
    
    ITEM_QUANTITIES: List[Tuple[str, str]] = [
        ('css', '.cart_quantity button'),
        ('xpath', '//td[@class="cart_quantity"]//button'),
        ('xpath', '//button[@class="disabled"]')
    ]
    
    ITEM_TOTALS: List[Tuple[str, str]] = [
        ('css', '.cart_total_price'),
        ('xpath', '//p[@class="cart_total_price"]'),
        ('xpath', '//td[@class="cart_total"]//p')
    ]
    
    CART_TOTAL: List[Tuple[str, str]] = [
        ('css', '.cart_total_price'),
        ('xpath', '//p[@class="cart_total_price"]'),
        ('xpath', '//h4[contains(text(), "Total")]/../p')
    ]
    
    PRODUCT_NAMES: List[Tuple[str, str]] = [
        ('css', '.cart_description h4 a'),
        ('xpath', '//td[@class="cart_description"]//h4/a'),
        ('xpath', '//h4/a[contains(@href, "product")]')
    ]
    
    
    def __init__(self, page):
        super().__init__(page)
        self.url = "https://automationexercise.com/view_cart"
    
    
    def navigate_to_cart(self):
        """Navigate directly to cart page"""
        self.logger.info("🛒 Navigating to Cart page")
        self.navigate_to(self.url)
    
    
    def extract_price(self, price_text: str) -> float:
        """
        Extract numeric price from text like 'Rs. 500' or 'Rs.1000'
        
        Args:
            price_text: Text containing price
            
        Returns:
            float: Numeric price value
        """
        match = re.search(r'[\d,]+', price_text)
        if match:
            price = float(match.group().replace(',', ''))
            return price
        return 0.0
    
    
    def get_cart_items_count(self) -> int:
        """Get number of items in cart"""
        try:
            items = self.page.locator('#cart_info tbody tr').all()
            count = len(items)
            self.logger.info(f"📦 Cart contains {count} items")
            return count
        except Exception as e:
            self.logger.error(f"❌ Error counting cart items: {str(e)}")
            return 0
    
    
    def get_cart_items_details(self) -> List[dict]:
        """
        Get details of all items in cart
        
        Returns:
            List of dictionaries with item details
        """
        items_details = []
        
        try:
            cart_rows = self.page.locator('#cart_info tbody tr').all()
            self.logger.info(f"📋 Processing {len(cart_rows)} cart items")
            
            for index, row in enumerate(cart_rows, start=1):
                try:
                    # Get product name
                    name_element = row.locator('.cart_description h4 a').first
                    name = name_element.inner_text()
                    
                    # Get price
                    price_element = row.locator('.cart_price p').first
                    price_text = price_element.inner_text()
                    price = self.extract_price(price_text)
                    
                    # Get quantity
                    qty_element = row.locator('.cart_quantity button').first
                    quantity = int(qty_element.inner_text())
                    
                    # Get total for this item
                    total_element = row.locator('.cart_total_price').first
                    total_text = total_element.inner_text()
                    total = self.extract_price(total_text)
                    
                    item = {
                        'name': name,
                        'price': price,
                        'quantity': quantity,
                        'total': total
                    }
                    
                    items_details.append(item)
                    self.logger.info(f"   Item {index}: {name} | Rs. {price} x {quantity} = Rs. {total}")
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Error processing cart item {index}: {str(e)}")
                    continue
            
            return items_details
            
        except Exception as e:
            self.logger.error(f"❌ Error getting cart details: {str(e)}")
            return []
    
    
    def calculate_cart_total(self) -> float:
        """
        Calculate total of all items in cart
        
        Returns:
            float: Total cart amount
        """
        try:
            items = self.get_cart_items_details()
            total = sum(item['total'] for item in items)
            self.logger.info(f"💰 Calculated cart total: Rs. {total}")
            return total
        except Exception as e:
            self.logger.error(f"❌ Error calculating total: {str(e)}")
            return 0.0
    
    
    def verify_cart_total_not_exceeds(self, budget_per_item: float, items_count: int) -> bool:
        """
        Verify that cart total doesn't exceed budget
        
        Args:
            budget_per_item: Maximum price per item
            items_count: Number of items expected
            
        Returns:
            bool: True if within budget, False otherwise
        """
        self.logger.info(f"🔍 Verifying cart total...")
        self.logger.info(f"   Budget per item: Rs. {budget_per_item}")
        self.logger.info(f"   Items count: {items_count}")
        
        # Calculate threshold
        threshold = budget_per_item * items_count
        self.logger.info(f"   Threshold: Rs. {threshold}")
        
        # Get actual cart total
        actual_total = self.calculate_cart_total()
        self.logger.info(f"   Actual total: Rs. {actual_total}")
        
        # Take screenshot
        timestamp = int(time.time())
        screenshot_path = f"screenshots/cart_verification_{timestamp}.png"
        self.page.screenshot(path=screenshot_path)
        self.logger.info(f"📸 Screenshot saved: {screenshot_path}")
        
        # Verify
        if actual_total <= threshold:
            self.logger.info(f"✅ PASS: Cart total Rs. {actual_total} is within budget Rs. {threshold}")
            return True
        else:
            self.logger.error(f"❌ FAIL: Cart total Rs. {actual_total} exceeds budget Rs. {threshold}")
            return False
    
    
    def get_cart_summary(self) -> dict:
        """
        Get complete cart summary
        
        Returns:
            Dictionary with cart summary
        """
        items = self.get_cart_items_details()
        total = self.calculate_cart_total()
        
        summary = {
            'items_count': len(items),
            'items': items,
            'total': total
        }
        
        self.logger.info(f"📊 Cart Summary: {len(items)} items, Total: Rs. {total}")
        return summary
    
    def clear_cart(self):
        """Clear all items from cart"""
    
        try:
            self.logger.info("🧹 Clearing cart...")
            
            # Get all delete buttons
            delete_buttons = self.page.locator('a.cart_quantity_delete')
            count = delete_buttons.count()
            
            if count == 0:
                self.logger.info("   Cart is already empty")
                return True
            
            self.logger.info(f"   Found {count} items to remove")
            
            # Delete each item
            for i in range(count):
                # Always click the first button (items shift after deletion)
                try:
                    self.page.locator('a.cart_quantity_delete').first.click()
                    time.sleep(0.5)
                    self.logger.info(f"   Removed item {i+1}/{count}")
                except:
                    break
            
            self.logger.info("✅ Cart cleared successfully")
            return True
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not clear cart: {str(e)}")
            return False