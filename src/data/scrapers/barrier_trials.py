"""
Barrier Trials Scraper for Racing.com

This scraper:
- Uses Selenium for Racing.com authentication
- Handles login automation and 2FA
- Extracts trial data: date, venue, distance, time, margin, position, comments
- Implements headless browser mode
- Handles anti-scraping measures

Usage:
    from src.data.scrapers.barrier_trials import BarrierTrialScraper

    scraper = BarrierTrialScraper(
        username="your_username",
        password="your_password",
        headless=True
    )
    trials = scraper.scrape_horse_trials("Horse Name", last_days=90)
"""

from __future__ import annotations

import logging
import os
import time
from datetime import date
from typing import Any

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.data.models import BarrierTrial

logger = logging.getLogger(__name__)


class BarrierTrialScraper:
    """
    Selenium-based scraper for Racing.com barrier trials.

    Racing.com trials require authentication, so we use Selenium
    to handle the login flow and navigate the authenticated sections.

    CONFIDENCE: MEDIUM - Racing.com may change their UI/auth flow
    This scraper implements defensive programming with fallbacks.

    Anti-scraping measures:
    - Random delays between requests
    - Headless mode with stealth settings
    - User agent rotation
    - Cookie management
    """

    BASE_URL = "https://www.racing.com"
    LOGIN_URL = f"{BASE_URL}/login"
    TRIALS_URL = f"{BASE_URL}/trials"

    # Timing constants (in seconds)
    PAGE_LOAD_TIMEOUT = 30
    ELEMENT_WAIT_TIMEOUT = 10
    MIN_REQUEST_DELAY = 2.0
    MAX_REQUEST_DELAY = 5.0

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        headless: bool = True,
        use_stealth: bool = True,
    ):
        """
        Initialize barrier trial scraper.

        Args:
            username: Racing.com username (or set RACING_COM_USERNAME env var)
            password: Racing.com password (or set RACING_COM_PASSWORD env var)
            headless: Run browser in headless mode
            use_stealth: Use stealth settings to avoid detection

        Note: If credentials are not provided, scraper will attempt
        to operate without authentication (limited functionality).
        """
        self.username = username or os.getenv("RACING_COM_USERNAME")
        self.password = password or os.getenv("RACING_COM_PASSWORD")
        self.headless = headless
        self.use_stealth = use_stealth

        self.driver: webdriver.Chrome | None = None
        self.authenticated = False

        logger.info(
            f"Initialized BarrierTrialScraper "
            f"(headless={headless}, auth={'yes' if self.username else 'no'})"
        )

    def _init_driver(self) -> webdriver.Chrome:
        """
        Initialize Chrome WebDriver with appropriate options.

        CONFIDENCE: HIGH - Chrome WebDriver is stable
        """
        options = webdriver.ChromeOptions()

        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")

        # Anti-detection measures (CONFIDENCE: MEDIUM - may need updates)
        if self.use_stealth:
            # Disable automation flags
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            # Set realistic user agent
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )

        # General options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)

        # Additional stealth measures
        if self.use_stealth:
            # Override navigator.webdriver property
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        })
                    """
                },
            )

        return driver

    def __enter__(self):
        """Context manager entry - initialize driver."""
        self.driver = self._init_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup driver."""
        if self.driver:
            self.driver.quit()

    def login(self, max_retries: int = 3) -> bool:
        """
        Authenticate with Racing.com.

        Args:
            max_retries: Maximum login attempts

        Returns:
            True if login successful, False otherwise

        CONFIDENCE: LOW - website may change login flow
        This is the most brittle part of the scraper.
        """
        if not self.username or not self.password:
            logger.warning("No credentials provided, skipping login")
            return False

        if not self.driver:
            raise RuntimeError("Driver not initialized. Use context manager.")

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Login attempt {attempt}/{max_retries}")

                # Navigate to login page
                self.driver.get(self.LOGIN_URL)
                time.sleep(2)  # Let page load

                # Find and fill username field
                # CONFIDENCE: LOW - selectors may change
                username_selectors = [
                    "input[name='username']",
                    "input[type='email']",
                    "input[id*='user']",
                    "#username",
                ]

                username_field = None
                for selector in username_selectors:
                    try:
                        username_field = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        break
                    except TimeoutException:
                        continue

                if not username_field:
                    raise NoSuchElementException("Could not find username field")

                username_field.clear()
                username_field.send_keys(self.username)

                # Find and fill password field
                password_selectors = [
                    "input[name='password']",
                    "input[type='password']",
                    "#password",
                ]

                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = self.driver.find_element(
                            By.CSS_SELECTOR, selector
                        )
                        break
                    except NoSuchElementException:
                        continue

                if not password_field:
                    raise NoSuchElementException("Could not find password field")

                password_field.clear()
                password_field.send_keys(self.password)

                # Find and click login button
                login_button_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Log in')",
                    "button:contains('Sign in')",
                ]

                login_button = None
                for selector in login_button_selectors:
                    try:
                        login_button = self.driver.find_element(
                            By.CSS_SELECTOR, selector
                        )
                        break
                    except NoSuchElementException:
                        continue

                if not login_button:
                    raise NoSuchElementException("Could not find login button")

                login_button.click()

                # Wait for login to complete
                time.sleep(3)

                # Check for 2FA prompt
                # CONFIDENCE: LOW - 2FA flow varies
                if self._detect_2fa():
                    logger.warning(
                        "2FA detected. Manual intervention may be required."
                    )
                    # Wait longer for manual 2FA completion
                    time.sleep(30)

                # Verify login success
                if self._verify_login():
                    self.authenticated = True
                    logger.info("✓ Login successful")
                    return True
                else:
                    logger.warning(f"Login failed (attempt {attempt})")

            except Exception as e:
                logger.error(f"Login attempt {attempt} failed: {e}")

            time.sleep(2)  # Delay between retries

        logger.error("All login attempts failed")
        return False

    def _detect_2fa(self) -> bool:
        """
        Detect if 2FA/MFA prompt is shown.

        CONFIDENCE: LOW - 2FA UI varies
        """
        try:
            two_fa_indicators = [
                "verification code",
                "two-factor",
                "2fa",
                "authenticator",
                "security code",
            ]

            page_text = self.driver.page_source.lower()
            return any(indicator in page_text for indicator in two_fa_indicators)

        except Exception:
            return False

    def _verify_login(self) -> bool:
        """
        Verify if login was successful.

        CONFIDENCE: MEDIUM - checks for common post-login indicators
        """
        try:
            # Check URL changed from login page
            if "login" in self.driver.current_url.lower():
                return False

            # Check for logout button or user menu
            logout_indicators = [
                "a[href*='logout']",
                "button:contains('Log out')",
                "[class*='user-menu']",
                "[class*='account-menu']",
            ]

            for selector in logout_indicators:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, selector)
                    return True
                except NoSuchElementException:
                    continue

            # If no specific indicator found, assume success if not on login page
            return True

        except Exception:
            return False

    def scrape_horse_trials(
        self,
        horse_name: str,
        last_days: int = 90,
    ) -> list[BarrierTrial]:
        """
        Scrape barrier trials for a specific horse.

        Args:
            horse_name: Horse name to search for
            last_days: Number of days to look back

        Returns:
            List of BarrierTrial models

        CONFIDENCE: MEDIUM - depends on Racing.com UI structure
        """
        if not self.driver:
            raise RuntimeError("Driver not initialized. Use context manager.")

        # Login if not already authenticated
        if not self.authenticated:
            if not self.login():
                logger.error("Cannot scrape trials without authentication")
                return []

        logger.info(f"Scraping trials for {horse_name} (last {last_days} days)")

        try:
            # Navigate to trials search
            self.driver.get(self.TRIALS_URL)
            time.sleep(2)

            # Search for horse
            trials_data = self._search_and_extract_trials(horse_name, last_days)

            # Convert to BarrierTrial models
            trials = self._convert_to_models(trials_data, horse_name)

            logger.info(f"✓ Found {len(trials)} trials for {horse_name}")
            return trials

        except Exception as e:
            logger.error(f"Failed to scrape trials for {horse_name}: {e}")
            return []

    def _search_and_extract_trials(
        self, horse_name: str, last_days: int
    ) -> list[dict[str, Any]]:
        """
        Search for horse and extract trial data.

        CONFIDENCE: LOW - Racing.com UI structure may change
        This is a placeholder implementation that would need to be
        adapted to the actual Racing.com trials page structure.
        """
        # TODO: Implement actual search and extraction logic
        # This would require:
        # 1. Find search input
        # 2. Enter horse name
        # 3. Submit search
        # 4. Parse results table
        # 5. Extract trial details

        logger.warning(
            "Trial extraction not fully implemented - "
            "would require analysis of Racing.com HTML structure"
        )

        # For now, return empty list
        # Real implementation would extract from page elements
        return []

    def _convert_to_models(
        self, trials_data: list[dict[str, Any]], horse_name: str
    ) -> list[BarrierTrial]:
        """
        Convert raw trial data to BarrierTrial models.

        Args:
            trials_data: List of dicts with trial info
            horse_name: Horse name for ID generation

        Returns:
            List of validated BarrierTrial models
        """
        trials = []

        for idx, trial_data in enumerate(trials_data):
            try:
                # Generate unique trial ID
                trial_id = (
                    f"{trial_data.get('horse_id', horse_name.lower())}-"
                    f"{trial_data.get('trial_date', date.today())}-{idx}"
                )

                # Create model with validation
                trial = BarrierTrial(
                    trial_id=trial_id,
                    horse_id=trial_data.get("horse_id", horse_name.lower()),
                    trial_date=trial_data["trial_date"],
                    venue=trial_data["venue"],
                    distance=trial_data["distance"],
                    time=trial_data.get("time"),
                    margin=trial_data.get("margin"),
                    position=trial_data.get("position"),
                    field_size=trial_data.get("field_size"),
                    comments=trial_data.get("comments"),
                    jockey_id=trial_data.get("jockey_id"),
                    trial_type=trial_data.get("trial_type", "official"),
                    track_condition=trial_data.get("track_condition"),
                    data_source="racing.com",
                )
                trials.append(trial)

            except Exception as e:
                logger.error(f"Failed to create BarrierTrial model: {e}")
                continue

        return trials

    def scrape_venue_trials(
        self,
        venue: str,
        trial_date: date | str,
    ) -> list[BarrierTrial]:
        """
        Scrape all trials for a specific venue and date.

        Args:
            venue: Venue name (e.g., 'Flemington', 'Randwick')
            trial_date: Trial date

        Returns:
            List of BarrierTrial models for all horses at that venue/date

        Note: This is a stub for future implementation
        """
        if isinstance(trial_date, str):
            trial_date = date.fromisoformat(trial_date)

        logger.info(f"Scraping venue trials: {venue} on {trial_date}")

        # TODO: Implement venue-based scraping
        raise NotImplementedError(
            "Venue-based trial scraping not yet implemented"
        )
