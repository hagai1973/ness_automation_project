"""
Authentication Service
----------------------
Business logic layer for all authentication-related flows.

Sits between tests and page objects:
  tests/ --> services/ --> pages/

Responsibilities:
  - Orchestrate multi-step login / logout / navigation flows
  - Accept business-level parameters (email, password)
  - Return page objects so tests can run assertions
  - Never assert here — assertions belong in tests only
"""

import allure
import logging
from pages.home_page import HomePage
from pages.login_page import LoginPage

logger = logging.getLogger(__name__)


class AuthService:
    """
    Encapsulates all authentication business logic.

    Usage:
        auth = AuthService(page)
        login_page = auth.login(email, password)
        assert login_page.is_logged_in()
    """

    def __init__(self, page):
        self.page       = page
        self.home_page  = HomePage(page)
        self.login_page = LoginPage(page)

    # ──────────────────────────────────────────────────────────────────────
    # PUBLIC ACTIONS
    # ──────────────────────────────────────────────────────────────────────

    @allure.step("AUTH SERVICE: Perform login with email={email}")
    def login(self, email: str, password: str) -> LoginPage:
        """
        Full login flow: navigate → open login page → submit credentials.

        Args:
            email:    User email address
            password: User password

        Returns:
            LoginPage: so the caller (test) can run assertions on it
        """
        logger.info(f"🔐 AuthService.login() → {email}")

        self._navigate_to_login()
        self._submit_credentials(email, password)

        logger.info("✅ AuthService.login() complete — awaiting assertion in test")
        return self.login_page

    @allure.step("AUTH SERVICE: Perform logout")
    def logout(self) -> LoginPage:
        """
        Logout the currently logged-in user.

        Returns:
            LoginPage: so the caller (test) can assert logged-out state
        """
        logger.info("🚪 AuthService.logout()")

        self.login_page.logout()

        logger.info("✅ AuthService.logout() complete — awaiting assertion in test")
        return self.login_page

    @allure.step("AUTH SERVICE: Login then logout in one flow")
    def login_and_logout(self, email: str, password: str) -> LoginPage:
        """
        Convenience method: full login followed immediately by logout.
        Useful for tests that verify the complete session lifecycle.

        Args:
            email:    User email address
            password: User password

        Returns:
            LoginPage: so the caller (test) can assert logged-out state
        """
        logger.info(f"🔄 AuthService.login_and_logout() → {email}")

        self.login(email, password)
        return self.logout()

    # ──────────────────────────────────────────────────────────────────────
    # PRIVATE HELPERS  (implementation details, not called by tests)
    # ──────────────────────────────────────────────────────────────────────

    @allure.step("Navigate to login page")
    def _navigate_to_login(self) -> None:
        """Navigate from home page to the login page."""
        logger.info("   → Navigating to home and opening login page")
        self.home_page.navigate()
        self.home_page.go_to_login()

    @allure.step("Submit login credentials")
    def _submit_credentials(self, email: str, password: str) -> None:
        """Fill in and submit the login form."""
        logger.info(f"   → Submitting credentials for {email}")
        self.login_page.login(email, password)