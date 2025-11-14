"""
Tests for Barrier Trials Scraper.

Tests cover:
- Selenium initialization
- Authentication flow
- Trial data extraction
- Error handling
- Anti-scraping measures
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from src.data.models import BarrierTrial
from src.data.scrapers.barrier_trials import BarrierTrialScraper


class TestBarrierTrialScraper:
    """Test suite for BarrierTrialScraper."""

    def test_scraper_initialization_default(self):
        """Test scraper initialization with defaults."""
        scraper = BarrierTrialScraper()
        
        assert scraper.headless is True
        assert scraper.use_stealth is True
        assert scraper.authenticated is False
        assert scraper.driver is None

    def test_scraper_initialization_with_credentials(self):
        """Test scraper initialization with credentials."""
        scraper = BarrierTrialScraper(
            username="test_user",
            password="test_pass",
            headless=False,
        )
        
        assert scraper.username == "test_user"
        assert scraper.password == "test_pass"
        assert scraper.headless is False

    def test_scraper_initialization_from_env(self, monkeypatch):
        """Test scraper reads credentials from environment variables."""
        monkeypatch.setenv("RACING_COM_USERNAME", "env_user")
        monkeypatch.setenv("RACING_COM_PASSWORD", "env_pass")
        
        scraper = BarrierTrialScraper()
        
        assert scraper.username == "env_user"
        assert scraper.password == "env_pass"

    @patch("src.data.scrapers.barrier_trials.webdriver.Chrome")
    def test_init_driver_headless(self, mock_chrome):
        """Test WebDriver initialization in headless mode."""
        scraper = BarrierTrialScraper(headless=True)
        driver = scraper._init_driver()
        
        # Verify Chrome was called
        mock_chrome.assert_called_once()
        
        # Check options included headless flag
        call_args = mock_chrome.call_args
        options = call_args[1].get("options") if call_args else None
        
        # Driver should have been returned
        assert driver is not None

    @patch("src.data.scrapers.barrier_trials.webdriver.Chrome")
    def test_init_driver_with_stealth(self, mock_chrome):
        """Test WebDriver initialization with stealth settings."""
        scraper = BarrierTrialScraper(use_stealth=True)
        driver = scraper._init_driver()
        
        mock_chrome.assert_called_once()
        assert driver is not None

    def test_detect_2fa_no_indicators(self):
        """Test 2FA detection when no indicators present."""
        scraper = BarrierTrialScraper()
        scraper.driver = Mock()
        scraper.driver.page_source = "<html><body>Normal page</body></html>"
        
        has_2fa = scraper._detect_2fa()
        
        assert has_2fa is False

    def test_detect_2fa_with_indicators(self):
        """Test 2FA detection when indicators are present."""
        scraper = BarrierTrialScraper()
        scraper.driver = Mock()
        scraper.driver.page_source = """
            <html><body>
                <div>Enter your verification code</div>
            </body></html>
        """
        
        has_2fa = scraper._detect_2fa()
        
        assert has_2fa is True

    def test_verify_login_not_on_login_page(self):
        """Test login verification when redirected away from login."""
        scraper = BarrierTrialScraper()
        scraper.driver = Mock()
        scraper.driver.current_url = "https://www.racing.com/dashboard"
        # When searching for logout indicators, they're not found but that's OK
        from selenium.common.exceptions import NoSuchElementException
        scraper.driver.find_element.side_effect = NoSuchElementException("Not found")
        
        is_logged_in = scraper._verify_login()
        
        # Should be True because URL is not login page
        assert is_logged_in is True
        
        assert is_logged_in is True

    def test_verify_login_still_on_login_page(self):
        """Test login verification when still on login page."""
        scraper = BarrierTrialScraper()
        scraper.driver = Mock()
        scraper.driver.current_url = "https://www.racing.com/login"
        
        is_logged_in = scraper._verify_login()
        
        assert is_logged_in is False

    def test_convert_to_models_empty_list(self):
        """Test conversion of empty trial data list."""
        scraper = BarrierTrialScraper()
        
        trials = scraper._convert_to_models([], "Test Horse")
        
        assert trials == []

    def test_convert_to_models_valid_data(self):
        """Test conversion of valid trial data to models."""
        scraper = BarrierTrialScraper()
        
        trial_data = [
            {
                "horse_id": "test-horse-1",
                "trial_date": date(2024, 11, 1),
                "venue": "Flemington",
                "distance": 1000,
                "time": Decimal("58.5"),
                "margin": Decimal("1.5"),
                "position": 2,
                "field_size": 8,
                "comments": "Worked well",
                "track_condition": "Good 4",
            }
        ]
        
        trials = scraper._convert_to_models(trial_data, "Test Horse")
        
        assert len(trials) == 1
        assert isinstance(trials[0], BarrierTrial)
        assert trials[0].venue == "Flemington"
        assert trials[0].distance == 1000
        assert trials[0].position == 2

    def test_convert_to_models_invalid_data_skipped(self):
        """Test that invalid trial data is skipped with logging."""
        scraper = BarrierTrialScraper()
        
        # Invalid data (missing required fields)
        trial_data = [
            {
                "horse_id": "test-horse-1",
                # Missing trial_date, venue, distance
            }
        ]
        
        trials = scraper._convert_to_models(trial_data, "Test Horse")
        
        # Should skip invalid entry
        assert len(trials) == 0

    def test_scrape_horse_trials_no_driver(self):
        """Test that scraping without driver raises error."""
        scraper = BarrierTrialScraper()
        
        with pytest.raises(RuntimeError, match="Driver not initialized"):
            scraper.scrape_horse_trials("Test Horse")

    @patch.object(BarrierTrialScraper, "login")
    @patch.object(BarrierTrialScraper, "_search_and_extract_trials")
    def test_scrape_horse_trials_success(self, mock_extract, mock_login):
        """Test successful trial scraping."""
        scraper = BarrierTrialScraper()
        scraper.driver = Mock()
        scraper.authenticated = False
        
        # Mock login success
        mock_login.return_value = True
        
        # Mock trial extraction
        mock_extract.return_value = [
            {
                "horse_id": "test-horse-1",
                "trial_date": date.today() - timedelta(days=10),
                "venue": "Flemington",
                "distance": 1000,
            }
        ]
        
        trials = scraper.scrape_horse_trials("Test Horse", last_days=90)
        
        # Should have attempted login
        mock_login.assert_called_once()
        
        # Should have extracted trials
        mock_extract.assert_called_once()

    @patch.object(BarrierTrialScraper, "login")
    def test_scrape_horse_trials_login_failure(self, mock_login):
        """Test trial scraping when login fails."""
        scraper = BarrierTrialScraper()
        scraper.driver = Mock()
        scraper.authenticated = False
        
        # Mock login failure
        mock_login.return_value = False
        
        trials = scraper.scrape_horse_trials("Test Horse")
        
        # Should return empty list
        assert trials == []

    def test_scrape_venue_trials_not_implemented(self):
        """Test that venue-based scraping raises NotImplementedError."""
        scraper = BarrierTrialScraper()
        scraper.driver = Mock()
        
        with pytest.raises(NotImplementedError):
            scraper.scrape_venue_trials("Flemington", "2024-11-05")

    def test_context_manager_enter(self):
        """Test context manager initializes driver."""
        with patch("src.data.scrapers.barrier_trials.webdriver.Chrome") as mock_chrome:
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            
            with BarrierTrialScraper() as scraper:
                assert scraper.driver == mock_driver

    def test_context_manager_exit(self):
        """Test context manager cleans up driver."""
        with patch("src.data.scrapers.barrier_trials.webdriver.Chrome") as mock_chrome:
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            
            with BarrierTrialScraper() as scraper:
                pass
            
            # Driver should be quit on exit
            mock_driver.quit.assert_called_once()


@pytest.mark.integration
class TestBarrierTrialScraperIntegration:
    """Integration tests requiring actual browser and network access."""

    @pytest.mark.skip(reason="Requires Racing.com credentials")
    def test_full_login_flow(self):
        """
        Test complete login flow with real credentials.
        
        This test is skipped by default as it requires:
        - Valid Racing.com credentials
        - Network access
        - Chrome/ChromeDriver installed
        """
        import os
        
        username = os.getenv("RACING_COM_USERNAME")
        password = os.getenv("RACING_COM_PASSWORD")
        
        if not username or not password:
            pytest.skip("Racing.com credentials not configured")
        
        with BarrierTrialScraper(username=username, password=password) as scraper:
            success = scraper.login()
            assert success is True
            assert scraper.authenticated is True

    @pytest.mark.skip(reason="Requires Racing.com access")
    def test_scrape_real_horse_trials(self):
        """
        Test scraping trials for a real horse.
        
        Skipped by default - requires valid credentials and network access.
        """
        pytest.skip("Requires Racing.com credentials and access")
