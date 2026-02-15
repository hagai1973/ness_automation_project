"""
Pytest configuration and shared fixtures
"""

import pytest
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
import logging
import os
import allure
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Configure logging
def setup_logging():
    """Setup logging configuration (worker-safe for parallel execution)"""
    if not os.path.exists('logs'):
        os.makedirs('logs', exist_ok=True)
    
    # Include xdist worker ID in log filename to avoid file conflicts
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'master')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"logs/test_run_{timestamp}_{worker_id}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s - [{worker_id}] %(name)s - %(levelname)s - %(message)s',
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


@pytest.fixture(scope="session")
def user_credentials():
    """
    Load user credentials from .env file
    Scope: session
    """
    email = os.getenv('USER_EMAIL')
    password = os.getenv('USER_PASSWORD')
    
    if not email or not password:
        raise ValueError(
            "❌ USER_EMAIL and USER_PASSWORD must be set in .env file.\n"
            "   Copy .env.example to .env and fill in your credentials."
        )
    
    logger.info(f"🔐 Credentials loaded from .env for: {email}")
    return {'email': email, 'password': password}


# ============================================================================
# FUNCTION SCOPE FIXTURES - Run for each test
# ============================================================================

@pytest.fixture(scope="function")
def browser_context():
    """
    Setup Playwright browser context for each test
    Scope: function (new browser for each test)
    
    Auto-detects Docker environment and configures browser accordingly:
    - Docker: headless mode with explicit viewport
    - Local: headed mode with maximized window
    
    Returns:
        tuple: (page, context, browser, playwright)
    """
    logger.info("\n" + "="*80)
    logger.info("🚀 Starting Browser Session")
    logger.info("="*80)
    
    # Detect if running in Docker container
    is_docker = os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER') == 'true'
    
    # Start Playwright
    playwright = sync_playwright().start()
    
    # Configure browser based on environment
    if is_docker:
        logger.info("🐳 Docker environment detected - running in HEADLESS mode")
        headless = True
        slow_mo = 100  # Faster in Docker
    else:
        logger.info("💻 Local environment detected - running in HEADED mode")
        headless = False
        slow_mo = 300  # Slower for local debugging
    
    # Launch browser with appropriate settings
    browser = playwright.chromium.launch(
        headless=headless,
        slow_mo=slow_mo,
        args=[
            '--start-maximized',
            '--disable-blink-features=AutomationControlled',  # Hide automation flags
            '--no-sandbox',  # Required for Docker
            '--disable-dev-shm-usage'  # Prevents memory issues in Docker
        ]
    )
    
    # Create context with environment-appropriate viewport settings
    if headless:
        # Headless mode: needs explicit viewport size
        logger.info("   📐 Setting viewport: 1920x1080")
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
    else:
        # Headed mode: allows window to be maximized
        logger.info("   🖥️  Using no_viewport (maximized window)")
        context = browser.new_context(
            no_viewport=True,  # KEY: Allows window to be maximized
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
    
    # Create page
    page = context.new_page()
    
    logger.info(f"✅ Browser launched successfully ({'HEADLESS' if headless else 'HEADED, MAXIMIZED'})")
    
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
            
            # Attach screenshot to Allure report
            with open(screenshot_path, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"FAILED_{test_name}",
                    attachment_type=allure.attachment_type.PNG
                )
            logger.error(f"📎 Screenshot attached to Allure report")
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
def ensure_empty_cart(page, user_credentials):
    """
    Ensure the cart is empty before the test runs.
    Logs in first, then navigates to cart, removes all items using clear_cart(),
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
    email = user_credentials['email']
    password = user_credentials['password']
    login_page.login(email, password)
    logger.info("✅ Logged in for cart cleanup")

    # Step 2: Navigate to cart and clean it using clear_cart()
    logger.info("🛒 Checking if cart is empty...")
    cart_page = CartPage(page)
    cart_page.navigate_to_cart()
    
    # Use the clear_cart() method
    cart_page.clear_cart()
    logger.info("✅ Cart cleared using clear_cart() method")

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