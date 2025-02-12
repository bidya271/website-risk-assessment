import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_page_size(url_to_check):
    """
    Scrapes the page size from EntireTools' Page Size Checker.

    Args:
        url_to_check (str): The website URL to check.

    Returns:
        dict: A dictionary containing Page URL, Page Size (Bytes), and Page Size (KB).
    """
    # Configure Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(), options=chrome_options)
    result_data = {}

    try:
        # Open the page
        url = "https://entiretools.com/page-size-checker"
        driver.get(url)
        print("🔍 Opening Page Size Checker...")

        # Fill in the URL input
        url_input = driver.find_element(By.NAME, "url")
        url_input.send_keys(url_to_check)

        # Click the submit button
        submit_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Submit']")
        submit_button.click()
        print("🚀 Submitted URL, waiting for results...")

        # Wait until the results table appears (up to 30 seconds)
        try:
            results_table = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[3]/div/div[1]/table"))
            )
        except:
            print("❌ Table not found. Check if the website structure has changed.")
            return {"error": "Results table not found."}

        print("✅ Results table found, extracting data...")

        # Extract required values
        table_rows = results_table.find_elements(By.TAG_NAME, "tr")

        if len(table_rows) < 3:
            print("❌ Unexpected table structure.")
            return {"error": "Unexpected table structure."}

        page_url = table_rows[0].find_elements(By.TAG_NAME, "td")[1].text.strip()
        page_size_bytes = table_rows[1].find_elements(By.TAG_NAME, "td")[1].text.strip()
        page_size_kb = table_rows[2].find_elements(By.TAG_NAME, "td")[1].text.strip()

        result_data = {
            "Page URL": page_url,
            "Page Size (Bytes)": page_size_bytes,
            "Page Size (KB)": page_size_kb
        }

        # Validate JSON format
        json.dumps(result_data, indent=4)
        return result_data

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": f"Error scraping Page Size Checker: {e}"}

    finally:
        driver.quit()


# Example usage
if __name__ == "__main__":
    test_url = "http://productindata.com"
    scraped_data = scrape_page_size(test_url)
    print(json.dumps(scraped_data, indent=4))
