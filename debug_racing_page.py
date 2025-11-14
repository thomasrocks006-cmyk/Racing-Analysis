#!/usr/bin/env python3
"""
Debug script to see what Racing.com page structure looks like.
"""

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Load Melbourne Cup page
    url = "https://www.racing.com/form/2024-11-05/flemington"
    print(f"Loading: {url}")
    driver.get(url)

    # Wait for page to load
    time.sleep(5)

    # Get page source and save it
    page_source = driver.page_source

    print(f"\nPage title: {driver.title}")
    print(f"Page source length: {len(page_source)} bytes")

    # Save to file for inspection
    with open("racing_com_page_source.html", "w", encoding="utf-8") as f:
        f.write(page_source)
    print("\n✅ Saved full page source to: racing_com_page_source.html")

    # Look for common patterns
    print("\n" + "=" * 60)
    print("LOOKING FOR PATTERNS:")
    print("=" * 60)

    patterns_to_check = [
        ("table", By.TAG_NAME),
        ("tbody", By.TAG_NAME),
        ("tr", By.TAG_NAME),
        ("[class*='runner']", By.CSS_SELECTOR),
        ("[class*='race']", By.CSS_SELECTOR),
        ("[class*='horse']", By.CSS_SELECTOR),
        ("[data-testid]", By.CSS_SELECTOR),
        ("button", By.TAG_NAME),
        ("a", By.TAG_NAME),
    ]

    for pattern, by_type in patterns_to_check:
        try:
            elements = driver.find_elements(by_type, pattern)
            print(f"\n{pattern}: Found {len(elements)} elements")

            if elements and len(elements) < 50:
                for i, elem in enumerate(elements[:10]):
                    text = elem.text.strip()[:50]
                    classes = elem.get_attribute("class") or ""
                    testid = elem.get_attribute("data-testid") or ""
                    if text or classes or testid:
                        print(
                            f"  [{i}] text='{text}' class='{classes[:30]}' testid='{testid[:30]}'"
                        )
        except Exception as e:
            print(f"{pattern}: Error - {e}")

    # Take a screenshot
    driver.save_screenshot("racing_com_screenshot.png")
    print("\n✅ Saved screenshot to: racing_com_screenshot.png")

finally:
    driver.quit()
    print("\n✅ Browser closed")
