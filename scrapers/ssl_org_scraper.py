import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def scrape_ssl_org(domain_name):
    """
    Scrapes SSL.org's security report for a given domain using Selenium.

    Args:
        domain_name (str): The domain name to check (e.g., "olleyes.com").

    Returns:
        dict: A dictionary containing report summary and SSL certificate details, formatted in snake_case.
    """
    # Configure Selenium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(), options=chrome_options)

    try:
        # Construct the URL
        url = f"https://www.ssl.org/report/{domain_name}"
        driver.get(url)

        # Wait for the report summary section to load
        report_summary = {}
        ssl_details = {}

        try:
            # Extract Report Summary
            report_table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'table-bordered')][1]"))
            )
            rows = report_table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) == 2:
                    key = to_snake_case(cols[0].text.strip().replace(":", ""))
                    value = cols[1].text.strip() or "n/a"
                    report_summary[key] = value

            # Extract SSL Certificate Details
            ssl_table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'table-bordered')][2]"))
            )
            rows = ssl_table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) == 2:
                    key = to_snake_case(cols[0].text.strip().replace(":", ""))
                    value = cols[1].text.strip() or "n/a"
                    ssl_details[key] = value

        except Exception as e:
            return {"error": f"error_extracting_data: {str(e)}"}

        # Construct the final dictionary
        result_data = {
            "domain": domain_name,
            "report_summary": report_summary,
            "ssl_certificate_details": ssl_details
        }

        # Validate JSON format
        try:
            json.dumps(result_data, indent=4)  # Ensure it converts to valid JSON
            return result_data
        except Exception as e:
            return {"error": f"invalid_json_formatting: {str(e)}"}

    except Exception as e:
        return {"error": f"error_scraping_{domain_name}", "details": str(e)}
    
    finally:
        driver.quit()

def to_snake_case(text):
    """
    Converts a given string to snake_case.
    """
    text = re.sub(r"\s+", "_", text)  # Replace spaces with underscores
    text = re.sub(r"[^a-zA-Z0-9_]", "", text)  # Remove non-alphanumeric characters except underscores
    return text.lower()

# Example usage
if __name__ == "__main__":
    domain_name = "olleyes.com"
    scraped_data = scrape_ssl_org(domain_name)
    print(json.dumps(scraped_data, indent=4))
