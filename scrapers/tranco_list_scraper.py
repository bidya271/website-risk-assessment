import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_tranco_list(domain_name):
    """
    Scrapes Tranco List for traffic rank information of a given domain.

    Args:
        domain_name (str): The domain name to check (e.g., "bizzycar.com").

    Returns:
        dict: A dictionary containing the domain and its traffic rank.
    """
    # Configure Selenium WebDriver options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(), options=chrome_options)

    try:
        # Debug: Step 1 - Navigate to the Tranco List website
        url = "https://tranco-list.eu/query"
        driver.get(url)
       # print("🔍 Step 1: Opened Tranco List website.")

        # Debug: Step 2 - Wait for the input box to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "domainInput"))
        )
       # print("✅ Step 2: Domain input field found.")

        # Debug: Step 3 - Enter the domain in the input field
        domain_input = driver.find_element(By.ID, "domainInput")
        domain_input.clear()
        domain_input.send_keys(domain_name)
       # print(f"✅ Step 3: Entered domain '{domain_name}' in input field.")

        # Debug: Step 4 - Click the "Get Rank" button
        get_rank_button = driver.find_element(By.ID, "getRanks")
        get_rank_button.click()
       # print("✅ Step 4: Clicked the 'Get Rank' button.")

        # Debug: Step 5 - Wait until the domain value updates, indicating a response
        WebDriverWait(driver, 15).until(
            lambda driver: driver.find_element(By.ID, "domain").text.strip() == domain_name
        )
       # print("✅ Step 5: Domain name response confirmed.")

        # Debug: Step 6 - Extract the rank result if available
        rank = driver.find_element(By.ID, "rank").text
       # print(f"✅ Step 6: Extracted rank '{rank}'.")

        result_data = {
            "domain": domain_name,
            "Tranco Rank": rank
        }

        # Debug: Step 7 - Validate and return JSON format
        json.dumps(result_data, indent=4)  # Ensure it converts to valid JSON
       # print("✅ Step 7: Successfully validated JSON format.")
        return result_data

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": f"Error scraping Tranco List for {domain_name}: {e}"}

    finally:
        driver.quit()


# Example usage
if __name__ == "__main__":
    domain_name = "nacelle.com"
    scraped_data = scrape_tranco_list(domain_name)
    print(json.dumps(scraped_data, indent=4))
