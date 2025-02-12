from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def check_popups_ads(domain):
    """
    Check if a website has pop-ups or advertisements.
    Returns strictly boolean values.
    """
    url = f"https://{domain}"

    # Configure Selenium Options
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-popup-blocking")  # Allow pop-ups to be detected

    # **Fixed WebDriver Initialization**
    service = Service()  # Use installed ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Allow time for pop-ups and ads to load

        has_popups = False
        has_ads = False

        # Detect Pop-ups (New Windows)
        main_window = driver.current_window_handle
        all_windows = driver.window_handles

        if len(all_windows) > 1:
            has_popups = True  # New window detected = Pop-up detected

        # Detect JavaScript Alerts (Pop-ups)
        try:
            WebDriverWait(driver, 2).until(EC.alert_is_present())  # Wait for alert
            alert = driver.switch_to.alert
            alert.dismiss()
            has_popups = True  # JavaScript alert detected
        except:
            pass  # No JS alerts detected

        # Detect Advertisements
        ad_selectors = [
            "iframe[src*='ads']", "div[class*='ad']", "div[id*='ad']",
            "ins.adsbygoogle", "iframe[title*='advertisement']", "iframe[src*='doubleclick']"
        ]

        for selector in ad_selectors:
            if driver.find_elements(By.CSS_SELECTOR, selector):
                has_ads = True
                break  # No need to check further if ads are detected

    except Exception as e:
        print(f"❌ Error processing {domain}: {e}")
    finally:
        driver.quit()

    return {
        "has_popups": has_popups,
        "has_ads": has_ads
    }

if __name__ == "__main__":
    domain = "aiworldjournal.com"
    result = check_popups_ads(domain)
    print(result)
