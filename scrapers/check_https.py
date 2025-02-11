from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

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

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Attempt to open HTTPS first
    try:
        driver.get(https_url)
        page_title = driver.title
        driver.quit()
        return {
            "has_https": True,
            "protocol": "HTTPS",
            "status": "Accessible",
            "page_title": page_title
        }
    except Exception as e:
        # HTTPS Failed, Try HTTP Instead
        try:
            driver.get(http_url)
            page_title = driver.title
            driver.quit()
            return {
                "has_https": False,
                "protocol": "HTTP",
                "status": "Accessible",
                "page_title": page_title,
                "error": "HTTPS failed, but HTTP is accessible"
            }
        except Exception as e:
            driver.quit()
            return {
                "has_https": False,
                "protocol": "None",
                "status": "Inaccessible",
                "error": "Both HTTPS and HTTP failed"
            }

if __name__ == "__main__":
    domain = "launchprotection.com"  # Replace with any domain
    result = check_https(domain)
    print(result)
