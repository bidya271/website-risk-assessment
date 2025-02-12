from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def check_https(domain):
    """
    Check if a website supports HTTPS or falls back to HTTP using Selenium.
    """
    https_url = f"https://{domain}"
    http_url = f"http://{domain}"

    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--ignore-certificate-errors")  # Bypass SSL certificate errors
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Helps with resource allocation

    # Initialize WebDriver without ChromeDriverManager
    service = Service()  # Use the default installed ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(https_url)
        time.sleep(2)  # Wait for the page to load
        page_title = driver.title
        return {
            "has_https": True,
            "protocol": "HTTPS",
            "status": "Accessible",
            "page_title": page_title
        }
    except Exception:
        try:
            driver.get(http_url)
            time.sleep(2)  # Wait for the page to load
            page_title = driver.title
            return {
                "has_https": False,
                "protocol": "HTTP",
                "status": "Accessible",
                "page_title": page_title,
                "error": "HTTPS failed, but HTTP is accessible"
            }
        except Exception:
            return {
                "has_https": False,
                "protocol": "None",
                "status": "Inaccessible",
                "error": "Both HTTPS and HTTP failed"
            }
    finally:
        driver.quit()  # Ensure the driver closes

if __name__ == "__main__":
    domain = "launchprotection.com"  # Replace with any domain
    result = check_https(domain)
    print(result)
