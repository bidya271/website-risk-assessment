from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def check_popups_ads(domain):
    """
    Check if a website has pop-ups or advertisements.
    Returns strictly boolean values.
    """
    url = f"https://{domain}"

    # **Configure Selenium Options**
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-popup-blocking")  # Allow pop-ups to be detected

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Allow time for pop-ups and ads to load

        has_popups = False
        has_ads = False

        # **Step 1: Detect Pop-ups (New Windows)**
        main_window = driver.current_window_handle
        all_windows = driver.window_handles

        if len(all_windows) > 1:
            has_popups = True  # New window detected = Pop-up detected

        # **Step 2: Detect JavaScript Alerts (Pop-ups)**
        try:
            WebDriverWait(driver, 2).until(EC.alert_is_present())  # Wait for alert
            alert = driver.switch_to.alert
            alert.dismiss()
            has_popups = True  # JavaScript alert detected
        except:
            pass  # No JS alerts detected

        # **Step 3: Detect Advertisements**
        ad_selectors = [
            "iframe[src*='ads']", "div[class*='ad']", "div[id*='ad']",
            "ins.adsbygoogle", "iframe[title*='advertisement']", "iframe[src*='doubleclick']"
        ]

        for selector in ad_selectors:
            try:
                if driver.find_elements(By.CSS_SELECTOR, selector):
                    has_ads = True
                    break  # No need to check further if ads are detected
            except:
                continue  # Ignore errors on non-loading elements

        # **Step 4: Detect Dynamically Loaded Ads**
        try:
            ad_count = driver.execute_script("""
                return document.querySelectorAll("iframe, div[id*='ad'], div[class*='ad']").length;
            """)
            if ad_count > 0:
                has_ads = True
        except:
            pass  # If JavaScript fails, ignore it

    except Exception as e:
        print(f"❌ Error processing {domain}: {e}")
    finally:
        driver.quit()

    return {
        "has_popups": has_popups,
        "has_ads": has_ads
    }

if __name__ == "__main__":
    domain = "msn.com"  # Replace with any domain
    result = check_popups_ads(domain)
    print(result)
