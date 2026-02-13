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