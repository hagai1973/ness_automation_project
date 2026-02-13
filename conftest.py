"""
Pytest configuration and shared fixtures
"""

import pytest
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
import logging
import os
from datetime import datetime


# Configure logging
def setup_logging():
    """Setup logging configuration"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    log_filename = f"logs/test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


# Setup logging at module level
logger = setup_logging()


# ============================================================================
# SESSION SCOPE FIXTURES - Run once per test session
# ============================================================================

@pytest.fixture(scope="session")
def test_data():
    """
    Load test data from JSON file
    Scope: session (loaded once for all tests)
    """
    data_file = Path(__file__).parent / "data" / "search_data.json"
    logger.info(f"📂 Loading test data from: {data_file}")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"✅ Test data loaded: {len(data.get('test_scenarios', []))} scenarios")
    return data


@pytest.fixture(scope="session")
def base_url(test_data):
    """
    Get base URL from test data
    Scope: session
    """
    url = test_data.get('base_url', 'https://automationexercise.com')
    logger.info(f"🌐 Base URL: {url}")
    return url


# ============================================================================
# FUNCTION SCOPE FIXTURES - Run for each test
# ============================================================================

@pytest.fixture(scope="function")
def browser_context():
    """
    Setup Playwright browser context for each test
    Scope: function (new browser for each test)
    
    Returns:
        tuple: (page, context, browser, playwright)
    """
    logger.info("\n" + "="*80)
    logger.info("🚀 Starting Browser Session")
    logger.info("="*80)
    
    # Start Playwright
    playwright = sync_playwright().start()
    
    # Launch browser MAXIMIZED
    browser = playwright.chromium.launch(
        headless=False,
        slow_mo=300,  # Reduced for faster execution
        args=[
            '--start-maximized',
            '--disable-blink-features=AutomationControlled'  # Hide automation flags
        ]
    )
    
    # Create context without viewport constraints
    context = browser.new_context(
        no_viewport=True,  # KEY: Allows window to be maximized
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    
    # Create page
    page = context.new_page()
    
    logger.info("✅ Browser launched successfully (MAXIMIZED)")
    
    yield page, context, browser, playwright
    
    # Teardown
    logger.info("\n" + "="*80)
    logger.info("🛑 Closing Browser Session")
    logger.info("="*80)
    
    page.close()
    context.close()
    browser.close()
    playwright.stop()
    
    logger.info("✅ Browser closed successfully")

@pytest.fixture(scope="function")
def page(browser_context):
    """
    Get page object from browser context
    Scope: function
    
    Returns:
        Page: Playwright page object
    """
    page, context, browser, playwright = browser_context
    return page


# ============================================================================
# SCREENSHOT FIXTURE
# ============================================================================

@pytest.fixture(scope="function", autouse=True)
def screenshot_on_failure(request, page):
    """
    Automatically take screenshot on test failure
    Scope: function, autouse=True (runs automatically)
    """
    yield
    
    # Check if test failed
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        test_name = request.node.name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create screenshots directory
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        screenshot_path = f"screenshots/FAILED_{test_name}_{timestamp}.png"
        
        try:
            page.screenshot(path=screenshot_path, full_page=True)
            logger.error(f"📸 Failure screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.error(f"❌ Could not take failure screenshot: {str(e)}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test result for screenshot_on_failure fixture
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ============================================================================
# CART CLEANUP FIXTURE
# ============================================================================

@pytest.fixture(scope="function")
def ensure_empty_cart(page, test_data):
    """
    Ensure the cart is empty before the test runs.
    Logs in first, then navigates to cart, removes all items if any exist,
    then returns to home page.
    Scope: function
    """
    from pages.cart_page import CartPage
    from pages.home_page import HomePage
    from pages.login_page import LoginPage

    # Step 1: Login first so we clear the authenticated user's cart
    logger.info("🔐 Logging in before cart cleanup...")
    home_page = HomePage(page)
    home_page.navigate()
    home_page.go_to_login()

    login_page = LoginPage(page)
    email = test_data['user_credentials']['email']
    password = test_data['user_credentials']['password']
    login_page.login(email, password)
    logger.info("✅ Logged in for cart cleanup")

    # Step 2: Navigate to cart and clean it
    logger.info("🛒 Checking if cart is empty...")
    cart_page = CartPage(page)
    cart_page.navigate_to_cart()

    # Check for items and remove them
    delete_buttons = page.locator('a.cart_quantity_delete')
    count = delete_buttons.count()

    if count > 0:
        logger.info(f"🧹 Cart has {count} item(s) — cleaning up...")
        for i in range(count):
            try:
                page.locator('a.cart_quantity_delete').first.click()
                # Wait for the item to be removed from DOM
                page.wait_for_timeout(1000)
                logger.info(f"   ❌ Removed item {i + 1}/{count}")
            except Exception:
                break

        # Verify cart is now empty
        remaining = page.locator('a.cart_quantity_delete').count()
        if remaining == 0:
            logger.info("✅ Cart is now empty")
        else:
            logger.warning(f"⚠️ {remaining} item(s) still remain in cart")
    else:
        logger.info("✅ Cart is already empty")

    # Step 3: Navigate back to home page so test starts from a clean state
    home_page.navigate()

    yield


# ============================================================================
# TEST MARKERS
# ============================================================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "smoke: Quick smoke tests")
    config.addinivalue_line("markers", "regression: Full regression tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "search: Search functionality tests")
    config.addinivalue_line("markers", "cart: Shopping cart tests")


# ============================================================================
# CLI OPTIONS
# ============================================================================

def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--env",
        action="store",
        default="prod",
        help="Environment to run tests: prod, staging, dev"
    )


@pytest.fixture(scope="session")
def test_environment(request):
    """Get test environment from command line"""
    return request.config.getoption("--env")