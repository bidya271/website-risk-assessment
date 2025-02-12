import requests
from bs4 import BeautifulSoup
import re
import urllib3
import ssl
import socket
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def check_ssl(domain):
    """
    Check if the SSL certificate is valid.
    """
    try:
        context = ssl.create_default_context()
        conn = context.wrap_socket(socket.create_connection((domain, 443), timeout=5), server_hostname=domain)
        conn.getpeercert()  # Retrieve the SSL certificate
        return True  # SSL is valid
    except ssl.SSLError:
        return False  # SSL error
    except Exception:
        return False  # Other connection errors


def fetch_page_content(domain):
    """
    Try fetching the page content using multiple fallbacks.
    Returns page content (HTML) or None if the website is not accessible.
    """
    url = f"https://{domain}"
    try:
        # Try with requests (default)
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text

    except requests.exceptions.SSLError:
        # Fallback: Try requests without SSL verification
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(url, timeout=15, verify=False)
            response.raise_for_status()
            return response.text
        except Exception:
            pass

    except requests.exceptions.RequestException:
        pass  # If any request fails, move to the next fallback

    # Fallback: Use Selenium WebDriver to bypass SSL and JavaScript issues
    try:
        options = Options()
        options.add_argument('--ignore-certificate-errors')  # Ignore SSL issues
        options.add_argument('--headless')  # Run without GUI

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        page_content = driver.page_source
        driver.quit()
        return page_content
    except Exception:
        return None  # All attempts failed


def extract_legal_name(text):
    """
    Extracts potential legal company names based on common patterns in Terms, Privacy Policy, and About Us pages.
    """
    patterns = [
        r"company name[:\s]+([A-Za-z0-9\s,.-]+)",  
        r"registered as[:\s]+([A-Za-z0-9\s,.-]+)",  
        r"is operated by[:\s]+([A-Za-z0-9\s,.-]+)",  
        r"\b([A-Za-z0-9\s]+ (Ltd|LLC|Inc|Pvt|Corporation|Limited|Pvt Ltd|SpA|BV|AG|KG|AB|Oy|NV|Sdn Bhd))\b"  
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None  # No legal name found


def check_privacy_term(domain):
    """
    Check if a website is accessible and whether it contains Terms of Service or Privacy Policy.
    """
    page_content = fetch_page_content(domain)
    is_accessible = page_content is not None  # Boolean indicating site accessibility

    if not is_accessible:
        return {
            "is_accessible": False,
            "ssl_valid": check_ssl(domain),
            "terms_of_service_present": False,
            "privacy_policy_present": False,
            "legal_name": None
        }

    soup = BeautifulSoup(page_content, "html.parser")
    page_text = soup.get_text().lower()  # Convert to lowercase for case-insensitive search

    # Common permutations for Terms and Privacy Policy
    terms_variants = [
        "terms of service", "terms of use", "terms & conditions", "terms and conditions",
        "terms", "user agreement", "website terms", "site terms"
    ]

    privacy_variants = [
        "privacy policy", "data protection", "gdpr", "privacy statement",
        "privacy notice", "data privacy", "confidentiality", "privacy"
    ]

    # Check for presence of Terms & Privacy Policy
    terms_present = any(term in page_text for term in terms_variants)
    privacy_present = any(policy in page_text for policy in privacy_variants)

    # Extract potential legal entity name
    company_name = extract_legal_name(page_text)

    return {
        "is_accessible": True,
        "ssl_valid": check_ssl(domain),
        "terms_of_service_present": terms_present,
        "privacy_policy_present": privacy_present,
        "legal_name": company_name
    }


# Example Usage
if __name__ == "__main__":
    domain = "launchprotection.com"  # Example domain
    result = check_privacy_term(domain)
    print(result)
