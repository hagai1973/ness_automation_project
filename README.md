# Ness Automation Project

Automated test framework for **automationexercise.com** built with **Playwright + Pytest**, following the **Page Object Model** design pattern with a custom **Smart Locator Fallback** mechanism for resilient element detection.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Running Tests](#running-tests)
- [Smart Locator Fallback Mechanism](#smart-locator-fallback-mechanism)
- [Page Object Model Design](#page-object-model-design)
- [Test Suites](#test-suites)
- [Test Data](#test-data)
- [Allure Reporting](#allure-reporting)
- [Fixtures](#fixtures)
- [Configuration](#configuration)

---

## Project Structure

```
ness_automation_project/
├── conftest.py                  # Pytest fixtures, hooks, browser setup
├── run_tests.py                 # Python test runner with Allure integration
├── pytest.ini                   # Pytest configuration and markers
├── requirements.txt             # Python dependencies
├── README.md
│
├── pages/                       # Page Object classes
│   ├── base_page.py             # Base class with Smart Locator fallback
│   ├── home_page.py             # Home page navigation
│   ├── login_page.py            # Login/authentication page
│   ├── products_page.py         # Product search, filter, add to cart
│   ├── cart_page.py             # Cart verification and management
│   └── product_detail_page.py   # Individual product details
│
├── tests/                       # Test suites
│   ├── test_login.py            # Login/logout tests (3 tests)
│   ├── test_shopping.py         # Guest shopping flow (1 test)
│   └── test_login_and_shop.py   # Authenticated E2E flow (1 test)
│
├── data/                        # Test data
│   └── search_data.json         # Search scenarios, credentials, budgets
│
├── utils/                       # Utility package (reserved for future use)
│
├── logs/                        # Test execution logs (git-ignored)
├── screenshots/                 # Failure screenshots (git-ignored)
├── allure-results/              # Raw Allure data (git-ignored)
└── allure-report/               # Generated HTML report (git-ignored)
```

---

## Tech Stack

| Component        | Technology                     |
|------------------|--------------------------------|
| Language         | Python 3.14                    |
| Test Framework   | Pytest 9.0.2                   |
| Browser Engine   | Playwright 1.58.0 (Chromium)   |
| Parallel         | pytest-xdist 3.8.0             |
| Reporting        | Allure 2.36.0 + allure-pytest  |
| Design Pattern   | Page Object Model (POM)        |
| CI/CD Ready      | Git + GitHub                   |

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- Git
- Java JDK (required by Allure CLI)
- Allure CLI (via [scoop](https://scoop.sh/) on Windows)

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/hagai1973/ness_automation_project.git
cd ness_automation_project

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
playwright install chromium

# 5. Install Allure CLI (Windows via scoop)
scoop install allure
```

---

## Running Tests

### Using `run_tests.py` (Recommended)

The Python test runner handles everything: environment setup, test execution, Allure report generation, and opening the report in the browser.

```bash
# Run ALL tests with Allure report
python run_tests.py

# Run specific test module
python run_tests.py --test login           # Login tests only
python run_tests.py --test shopping        # Shopping flow tests
python run_tests.py --test login_and_shop  # Authenticated E2E test

# Run by pytest marker
python run_tests.py --marker smoke         # Smoke tests
python run_tests.py --marker regression    # Regression suite
python run_tests.py --marker e2e           # End-to-end tests

# Run without Allure report
python run_tests.py --no-report

# Short flags
python run_tests.py -t login              # Same as --test login
python run_tests.py -m smoke              # Same as --marker smoke
```

### Parallel Execution

Use `--workers` / `-w` to run tests in parallel. Each worker gets its own browser instance:

```bash
# Run with 2 parallel browsers
python run_tests.py -w 2

# Run with 3 workers on login tests
python run_tests.py -t login -w 3

# Auto-detect workers (1 per CPU core)
python run_tests.py -w auto

# Combine with other flags
python run_tests.py -t login -w 2 --no-report
```

> **Note:** Each worker launches a separate Chromium browser. More workers = faster execution, but more memory. Start with 2-3 and increase based on your machine's resources.

**What `run_tests.py` does automatically:**

1. Sets up PATH for Allure CLI and Java
2. Cleans previous results (`logs/`, `screenshots/`, `allure-results/`, `allure-report/`)
3. Runs pytest with the venv interpreter
4. Generates the Allure HTML report
5. Opens the report in your default browser

### Using pytest directly

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_login.py -v

# Run a specific test
pytest tests/test_login.py::TestLogin::test_successful_login -v

# Run by marker
pytest tests/ -m smoke -v
```

---

## Smart Locator Fallback Mechanism

The framework implements a custom **Smart Locator** strategy that provides resilient element detection by trying multiple locator strategies in sequence. If the primary locator fails, it automatically falls back to alternative locators.

### How It Works

Each page element is defined with **2-3 locator strategies** (CSS, XPath, text). When interacting with an element, the framework tries each locator in order until one succeeds:

```
Attempt 1 (CSS)  →  ✅ Success  →  Interact with element
                 →  ❌ Fail     →  Attempt 2 (XPath)  →  ✅ Success  →  Interact
                                                      →  ❌ Fail     →  Attempt 3 (Text)  →  ✅/❌
```

### Implementation (base_page.py)

```python
def find_element_with_fallback(self, locators: List[Tuple[str, str]], timeout: int = 5000):
    """Try multiple locators with fallback"""
    for index, (strategy, value) in enumerate(locators, start=1):
        try:
            if strategy == 'css':
                element = self.page.locator(value)
            elif strategy == 'xpath':
                element = self.page.locator(f"xpath={value}")
            elif strategy == 'text':
                element = self.page.get_by_text(value)

            element.wait_for(state='visible', timeout=timeout)
            return element  # ✅ Success

        except Exception:
            if index == len(locators):
                raise  # 🚫 All locators failed
            continue     # ➡️ Try next locator
```

### Locator Definition Example

Each page object defines its elements as a list of `(strategy, value)` tuples:

```python
class LoginPage(BasePage):
    EMAIL_INPUT: List[Tuple[str, str]] = [
        ('css', 'input[data-qa="login-email"]'),          # Primary: CSS selector
        ('xpath', '//input[@data-qa="login-email"]'),      # Fallback 1: XPath
        ('xpath', '//form[@action="/login"]//input[@name="email"]')  # Fallback 2
    ]
```

### Supported Strategies

| Strategy | Method Used                        | Best For                  |
|----------|------------------------------------|---------------------------|
| `css`    | `page.locator(value)`              | IDs, classes, attributes  |
| `xpath`  | `page.locator(f"xpath={value}")`   | Complex DOM traversal     |
| `text`   | `page.get_by_text(value)`          | Visible text content      |
| `role`   | `page.get_by_role(value)`          | ARIA roles                |

### Helper Methods

The base page provides wrapper methods that use the fallback mechanism:

| Method                         | Description                               |
|--------------------------------|-------------------------------------------|
| `find_element_with_fallback()` | Find element, return Locator object        |
| `click_with_fallback()`        | Click using smart locator                  |
| `type_with_fallback()`         | Type text using smart locator              |
| `get_text_with_fallback()`     | Get element text using smart locator       |
| `navigate_to()`               | Navigate to URL, wait for network idle      |

---

## Page Object Model Design

The framework follows the **Page Object Model (POM)** pattern where each web page is represented by a class that encapsulates its elements and actions.

### Class Hierarchy

```
BasePage (base_page.py)
  ├── Smart Locator fallback mechanism
  ├── click_with_fallback(), type_with_fallback(), etc.
  └── navigate_to(), screenshot helpers
       │
       ├── HomePage (home_page.py)
       │     └── navigate(), go_to_products(), go_to_login(), go_to_cart()
       │
       ├── LoginPage (login_page.py)
       │     └── login(), logout(), is_logged_in()
       │
       ├── ProductsPage (products_page.py)
       │     └── search_product(), get_products_under_price_and_add_to_cart()
       │
       ├── CartPage (cart_page.py)
       │     └── get_cart_items_details(), calculate_cart_total(), clear_cart()
       │
       └── ProductDetailPage (product_detail_page.py)
             └── get_product_info(), add_to_cart()
```

### Key Design Principles

- **Each page = one class** with its own locators and methods
- **All locators use the fallback mechanism** (2-3 strategies per element)
- **BasePage handles all low-level interactions** (find, click, type, navigate)
- **Page classes expose business-level actions** (login, search, add to cart)
- **Tests never interact with locators directly** — only through page methods

---

## Test Suites

### test_login.py — Authentication Tests

| Test | Markers | Description |
|------|---------|-------------|
| `test_successful_login` | smoke, regression | Login with valid credentials, verify logged-in state |
| `test_login_with_invalid_credentials` | smoke | Login with bad credentials, verify error message |
| `test_logout` | regression | Login then logout, verify logged-out state |

### test_shopping.py — Guest Shopping Flow

| Test | Markers | Description |
|------|---------|-------------|
| `test_search_and_add_items_under_budget` | e2e, regression | Search products, filter by price, add to cart, verify total within budget |

### test_login_and_shop.py — Authenticated E2E Flow

| Test | Markers | Description |
|------|---------|-------------|
| `test_login_search_add_verify` | e2e, regression | Login → Search → Add items under budget → Navigate to cart → Verify total ≤ Rs. 4,500 |

Uses the `ensure_empty_cart` fixture to clean the cart before running.

---

## Test Data

Test data is stored in `data/search_data.json` and loaded once per session:

```json
{
  "base_url": "https://automationexercise.com",
  "test_scenarios": [
    { "test_name": "search_tshirt_under_budget", "search_query": "tshirt", "max_price": 1500, "items_limit": 3 },
    { "test_name": "search_dress_under_budget", "search_query": "dress", "max_price": 2000, "items_limit": 3 },
    { "test_name": "search_top_under_budget", "search_query": "top", "max_price": 1000, "items_limit": 2 }
  ],
  "user_credentials": { "email": "...", "password": "..." }
}
```

---

## Allure Reporting

Tests are decorated with Allure annotations for rich reporting:

```python
@allure.feature('Authentication')
@allure.story('User Login')
@allure.title("Successful login with valid credentials")
@allure.severity(allure.severity_level.BLOCKER)
```

### Report Features

- **Test steps** with descriptions and timing
- **Failure screenshots** automatically attached on test failure
- **Tags and categories** for filtering (smoke, regression, e2e)
- **Severity levels** (blocker, critical, normal)

### Viewing Reports

Reports are automatically generated and opened when running via `run_tests.py`. To manually open the last generated report:

```bash
allure open allure-report
```

---

## Fixtures

Defined in `conftest.py`:

| Fixture | Scope | Description |
|---------|-------|-------------|
| `test_data` | session | Loads test data from `search_data.json` (once per session) |
| `browser_context` | function | Creates a new browser context per test (maximized window) |
| `page` | function | Creates a new page per test |
| `screenshot_on_failure` | function (autouse) | Captures screenshot + attaches to Allure on failure |
| `ensure_empty_cart` | function | Logs in, navigates to cart, removes all items, returns to home |

---

## Configuration

### pytest.ini

- **Markers:** `smoke`, `regression`, `e2e`, `search`, `cart`, `slow`
- **Browser:** Chromium (headed mode, maximized)
- **Timeout:** 300 seconds per test
- **Logging:** Console (INFO) + file (DEBUG)
- **Allure:** Results auto-collected to `allure-results/`

### .gitignore

The following are excluded from the repository:
- `venv/` — Virtual environment
- `logs/` — Test execution logs
- `screenshots/` — Failure screenshots
- `allure-results/` — Raw Allure data
- `allure-report/` — Generated HTML report