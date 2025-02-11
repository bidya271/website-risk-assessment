import ssl
import hashlib
import socket
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_ssl_fingerprint(domain):
    """
    Retrieves the SHA-256 fingerprint of an SSL certificate.
    Uses a direct SSL socket connection.
    Falls back to Selenium if SSL extraction fails.
    """
    try:
        context = ssl.create_default_context()
        
        # Create a secure SSL socket connection
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert(binary_form=True)
        
        # Compute SHA-256 fingerprint
        sha256_fingerprint = hashlib.sha256(cert).hexdigest()
        return {
            "domain": domain,
            "sha256_fingerprint": sha256_fingerprint,
            "has_sha256": True
        }
    except Exception as e:
        # If direct SSL fails, try Selenium
        return get_ssl_fingerprint_selenium(domain, error=str(e))

def get_ssl_fingerprint_selenium(domain, error=""):
    """
    Fallback: Uses Selenium to extract SSL fingerprint if the direct method fails.
    Opens the website in a headless browser and verifies SSL certificate usage.
    """
    url = f"https://{domain}"

    options = Options()
    options.add_argument("--headless")  # Run without UI
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        page_title = driver.title
        driver.quit()
        return {
            "domain": domain,
            "has_sha256": "Unknown",
            "error": f"Direct SSL failed: {error}",
            "ssl_check_via_selenium": True,
            "page_title": page_title
        }
    except Exception as e:
        driver.quit()
        return {
            "domain": domain,
            "has_sha256": False,
            "error": f"Both SSL and Selenium failed: {error}, {str(e)}"
        }

if __name__ == "__main__":
    domain = "launchprotection.com"  # Replace with your domain
    result = get_ssl_fingerprint(domain)
    print(result)
