from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_ssltrust_blacklist(domain_name):
    """
    Scrapes SSL Trust Website Security Check data for a given domain using Selenium.
    
    Args:
        domain_name (str): The domain name to check (e.g., "bizzycar.com").
    
    Returns:
        dict: A dictionary containing the scraped data or an error message.
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
        # Open the SSL Trust security check page
        url = "https://www.ssltrust.com/ssl-tools/website-security-check"
        driver.get(url)

        # Wait for the input field and enter the domain
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.el-input__inner"))
        )
        input_field.clear()
        input_field.send_keys(domain_name)

        # Click the Submit button
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.el-button.el-button--primary"))
        )
        submit_button.click()

        # Wait for results to load (Adjust delay if necessary)
        time.sleep(15)  # Allow time for the scan to complete

        # Extract status and results
        results = {
            "Status": "Unknown",
            "results": "Unknown"
        }

        try:
            status_text = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//p/strong[contains(text(),'Status:')]/.."))
            ).text
            results["Status"] = status_text.replace("Status:", "").strip()

            results_text = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//p/strong[contains(text(),'Results:')]/.."))
            ).text
            results["Results"] = results_text.replace("Results:", "").strip()

        except Exception as e:
            results["error"] = f"Failed to extract results: {e}"

        return results

    except Exception as e:
        return {"error": f"Error scraping {domain_name}: {e}"}
    
    finally:
        driver.quit()
