import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_google_safe_browsing(domain_name):
    """
    Scrapes Google Transparency Report - Safe Browsing data for a given domain using Selenium.
    
    Args:
        domain_name (str): The domain name to check (e.g., "bizzycar.com").
    
    Returns:
        dict: A dictionary containing the site status and site info.
    """
    # Configure Selenium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    chrome_options.add_argument("--log-level=3")  # Suppress unnecessary logs
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Initialize WebDriver
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        return {"error": f"Failed to start WebDriver: {e}"}

    try:
        # Construct the URL
        url = f"https://transparencyreport.google.com/safe-browsing/search?url={domain_name}&hl=en"
        driver.get(url)

        # Wait for the status and site info sections to load
        status = "Unknown"
        site_info = "Unknown"

        try:
            # Extract "Current Status"
            status_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//data-tile[@trtitle='Current status']//span"))
            )
            status = status_element.text.strip()

            # Extract "Site Info"
            site_info_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//column-layout//p"))
            )
            site_info = site_info_element.text.strip()

        except Exception as e:
            return {"error": f"Failed to extract data: {e}"}

        # Construct final result
        result_data = {
            "domain": domain_name,
            "Current Status": status,
            "Site Info": site_info
        }

        return result_data

    except Exception as e:
        return {"error": f"Error scraping {domain_name}: {e}"}

    finally:
        driver.quit()


# Example usage
if __name__ == "__main__":
    domain_name = "launchprotection.com"  # Replace with the domain to check
    scraped_data = scrape_google_safe_browsing(domain_name)
    print(json.dumps(scraped_data, indent=4))
