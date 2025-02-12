from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

def scrape_godaddy_whois(domain):
    """
    Scrapes WHOIS data for a given domain from GoDaddy's WHOIS lookup page.

    Args:
        domain (str): The domain name to scrape (e.g., "productindata.com").

    Returns:
        dict: A dictionary containing the scraped data in snake_case format.
    """
    # Configure Selenium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(), options=chrome_options)

    try:
        # Construct the GoDaddy WHOIS URL
        url = f"https://in.godaddy.com/whois/results.aspx?itc=dlp_domain_whois&domainName={domain}"

        # Open the URL
        driver.get(url)
        time.sleep(random.uniform(3, 5))  # Random delay to mimic human behavior

        # Mimic mouse movements
        actions = ActionChains(driver)
        actions.move_by_offset(random.randint(10, 50), random.randint(10, 50)).perform()
        time.sleep(random.uniform(1, 2))

        # Extract the required information
        results = {
            "name": "unknown",
            "registry_domain_id": "unknown",
            "registered_on": "unknown",
            "expires_on": "unknown",
            "updated_on": "unknown",
            "domain_status": "unknown",
            "name_servers": []
        }

        # Locate the container
        try:
            container = driver.find_element(By.CLASS_NAME, "contact-info-container")

            # Extract Name
            try:
                results["name"] = container.find_element(
                    By.CSS_SELECTOR, "span#title-domainName + span.contact-label"
                ).text.strip()
            except:
                pass

            # Extract Registry Domain ID
            try:
                results["registry_domain_id"] = container.find_element(
                    By.CSS_SELECTOR, "span#title-registryDomainId + span.contact-label"
                ).text.strip()
            except:
                pass

            # Extract Registered On
            try:
                results["registered_on"] = container.find_element(
                    By.CSS_SELECTOR, "span#title-creationDate + span.contact-label"
                ).text.strip()
            except:
                pass

            # Extract Expires On
            try:
                results["expires_on"] = container.find_element(
                    By.CSS_SELECTOR, "span#title-expiresOn + span.contact-label"
                ).text.strip()
            except:
                pass

            # Extract Updated On
            try:
                results["updated_on"] = container.find_element(
                    By.CSS_SELECTOR, "span#title-updatedOn + span.contact-label"
                ).text.strip()
            except:
                pass

            # Extract Domain Status
            try:
                results["domain_status"] = container.find_element(
                    By.CSS_SELECTOR, "div#contact-labels p.contact-label"
                ).text.strip()
            except:
                pass

            # Extract Name Servers
            try:
                name_servers = container.find_elements(
                    By.CSS_SELECTOR, "span#title-nameservers + div#contact-labels p.contact-label"
                )
                results["name_servers"] = [ns.text.strip() for ns in name_servers]
            except:
                pass

        except:
            pass

        return results
    except Exception as e:
        print(f"Error scraping {domain}: {e}")
        return None
    finally:
        # Close the WebDriver
        driver.quit()
