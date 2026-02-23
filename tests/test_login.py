"""
Login functionality tests
─────────────────────────
Architecture:
  test_login.py  ← assertions + test intent only  (this file)
  auth_service   ← business logic / multi-step flows
  pages/         ← element locators + low-level actions

Each test should answer ONE question:
  "Given this state, does the system behave correctly?"

Xray Integration:
  Each test is linked to a Jira Test issue via @pytest.mark.xray("SP2-XXX")
  Run with:  pytest --jira-xray --cloud
"""

import pytest
import allure
import logging
from services.auth_service import AuthService

logger = logging.getLogger(__name__)


@allure.feature('Authentication')
@allure.story('User Login')
class TestLogin:
    """Test class for login functionality"""

    # ──────────────────────────────────────────────────────────────────────
    # FIXTURES
    # ──────────────────────────────────────────────────────────────────────

    @pytest.fixture(autouse=True)
    def setup(self, page):
        """Initialise AuthService once per test — injected via 'page' fixture."""
        self.auth = AuthService(page)

    # ──────────────────────────────────────────────────────────────────────
    # TESTS
    # ──────────────────────────────────────────────────────────────────────

    @allure.title("Successful login with valid credentials")
    @allure.description("Verify a user can log in with correct email and password")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.xray("SP2-248")        # ← 🔗 Linked to Jira Test issue SP2-248
    def test_successful_login(self, user_credentials):
        """A valid user should be logged in after submitting correct credentials."""
        logger.info("🔐 TEST: Successful Login")

        # ── Act ────────────────────────────────────────────────────────────
        login_page = self.auth.login(
            email    = user_credentials['email'],
            password = user_credentials['password']
        )

        # ── Assert ─────────────────────────────────────────────────────────
        with allure.step("Verify user is logged in"):
            assert login_page.is_logged_in(), \
                "Expected user to be logged in after valid credentials — but they were not"

        logger.info("✅ TEST PASSED: Successful login confirmed")


    @allure.title("Login fails with invalid credentials")
    @allure.description("Verify login is rejected when wrong credentials are submitted")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.xray("SP2-249")        # ← 🔗 Replace SP2-249 with your actual Jira Test key
    def test_login_with_invalid_credentials(self):
        """An invalid user should NOT be logged in after submitting wrong credentials."""
        logger.info("🔐 TEST: Login with Invalid Credentials")

        # ── Act ────────────────────────────────────────────────────────────
        login_page = self.auth.login(
            email    = "invalid@test.com",
            password = "wrongpassword"
        )

        # ── Assert ─────────────────────────────────────────────────────────
        with allure.step("Verify user is NOT logged in"):
            assert login_page.is_logged_out(), \
                "Expected login to fail with invalid credentials — but user was logged in"

        logger.info("✅ TEST PASSED: Login correctly rejected invalid credentials")


    @allure.title("Logout functionality")
    @allure.description("Verify a logged-in user can successfully log out")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.xray("SP2-250")        # ← 🔗 Replace SP2-250 with your actual Jira Test key
    def test_logout(self, user_credentials):
        """A logged-in user should be logged out after triggering logout."""
        logger.info("🚪 TEST: Logout Functionality")

        # ── Arrange ────────────────────────────────────────────────────────
        login_page = self.auth.login(
            email    = user_credentials['email'],
            password = user_credentials['password']
        )

        with allure.step("Verify user is logged in before logout"):
            assert login_page.is_logged_in(), \
                "Precondition failed: user should be logged in before testing logout"

        # ── Act ────────────────────────────────────────────────────────────
        login_page = self.auth.logout()

        # ── Assert ─────────────────────────────────────────────────────────
        with allure.step("Verify user is logged out"):
            assert login_page.is_logged_out(), \
                "Expected user to be logged out — but they are still logged in"

        logger.info("✅ TEST PASSED: Logout confirmed")