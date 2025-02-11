import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def scrape_similarweb_data(domain_name):
    """
    Scrapes SimilarWeb for firmographics, rankings, and top traffic countries of a given domain_name.
    
    Args:
        domain_name (str): The domain_name name to check (e.g., "example.com").
    
    Returns:
        dict: A dictionary containing extracted data from SimilarWeb.
    """
    # Configure Selenium WebDriver options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(), options=chrome_options)
    
    try:
        url = f"https://www.similarweb.com/website/{domain_name}/"
        driver.get(url)
        time.sleep(5)  # Allow extra time for the page to load

        # Initialize results dictionary
        data = {'domain_name': domain_name}

        # Extract Firmographics
        try:
            firmographics_section = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".app-firmographics__list"))
            )
            firmographics_items = firmographics_section.find_elements(By.CSS_SELECTOR, ".app-firmographics__item")
            for item in firmographics_items:
                title = item.find_element(By.CSS_SELECTOR, ".app-firmographics__item-title").text.strip()
                value = item.find_element(By.CSS_SELECTOR, ".app-firmographics__item-value").text.strip()
                data[title] = value
        except (TimeoutException, NoSuchElementException):
            data['Firmographics'] = "NA"
        
        # Extract Rankings
        try:
            rankings_section = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".app-summary-card.wa-summary__rankings"))
            )
            rankings_items = rankings_section.find_elements(By.CSS_SELECTOR, ".wa-summary__rankings-item")
            for item in rankings_items:
                title = item.find_element(By.CSS_SELECTOR, ".wa-summary__rankings-title").text.strip()
                value = item.find_element(By.CSS_SELECTOR, ".wa-summary__rankings-value").text.strip()
                data[title] = value.replace("#", "").replace(",", "").strip()
        except (NoSuchElementException, TimeoutException):
            data['Rankings'] = "NA"

        # Extract Top Countries by traffic share
        try:
            countries_section = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".wa-geography__legend"))
            )
            country_items = countries_section.find_elements(By.CSS_SELECTOR, ".wa-geography__legend-item")
            countries_data = {}
            for item in country_items:
                country_name = item.find_element(By.CSS_SELECTOR, ".wa-geography__country-name").text.strip()
                traffic_value = item.find_element(By.CSS_SELECTOR, ".wa-geography__country-traffic-value").text.strip()
                countries_data[country_name] = traffic_value.replace("%", "").strip()
            data['Top Countries traffic percentage'] = countries_data
        except (NoSuchElementException, TimeoutException):
            data['Top Countries traffic percentage'] = "NA"

        return data
    
    except Exception as e:
        return {"error": f"Error scraping SimilarWeb for {domain_name}: {e}"}
    
    finally:
        driver.quit()

# Example usage:
if __name__ == "__main__":
    domain_name = "amazon.com"
    scraped_data = scrape_similarweb_data(domain_name)
    print(json.dumps(scraped_data, indent=4))
