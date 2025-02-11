import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_mxtoolbox(domain_name):
    """
    Scrapes MXToolbox for email health information of a given domain.

    Args:
        domain_name (str): The domain name to check (e.g., "bizzycar.com").

    Returns:
        dict: A dictionary containing blacklist, problems, and issue details.
    """
    # Configure Selenium WebDriver options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(), options=chrome_options)
    result_data = {}

    try:
        # Navigate to the MXToolbox email health page
        url = f"https://mxtoolbox.com/emailhealth/{domain_name}/"
        driver.get(url)
        print("🔍 Fetching email health information...")

        # Wait for the page to show "Complete"
        WebDriverWait(driver, 900).until(
            EC.text_to_be_present_in_element((By.ID, "spanTestsRemaining"), "Complete")
        )
        print("✅ Test results are complete.")

        # Extract Blacklist Results
        blacklist_data = {
            "Errors": driver.find_element(By.ID, "blacklistNumFailed").text,
            "Warnings": driver.find_element(By.ID, "blacklistNumWarning").text,
            "Passed": driver.find_element(By.ID, "blacklistNumPassed").text
        }
        result_data["Blacklist"] = blacklist_data

        # Extract Problems Results
        problems_data = {
            "Errors": driver.find_element(By.ID, "spanNumErrors").text,
            "Warnings": driver.find_element(By.ID, "spanNumWarnings").text,
            "Passed": driver.find_element(By.ID, "spanNumPassed").text
        }
        result_data["Problems"] = problems_data
        print("✅ Extracted blacklist and problems data.")

        # Extract Problem Table Details
        table_rows = driver.find_elements(By.XPATH, "//table[@class='table']/tbody/tr")
        table_data = []

        for row in table_rows:
            try:
                # Extract the issue category, host, result, and status image alt text
                status_img = row.find_element(By.XPATH, "./td[1]/img").get_attribute("alt").strip()
                category = row.find_element(By.XPATH, "./td[2]").text.strip()
                host = row.find_element(By.XPATH, "./td[3]").text.strip()
                result = row.find_element(By.XPATH, "./td[4]").text.strip()

                table_data.append({
                    "Status": status_img,
                    "Category": category,
                    "Host": host,
                    "Result": result
                })
            except Exception as e:
                print(f"❌ Error extracting row data: {e}")

        result_data["Problem Table"] = table_data
        print("✅ Extracted problem table details.")

        # Validate JSON format and return result
        json.dumps(result_data, indent=4)
        return result_data

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": f"Error scraping MXToolbox for {domain_name}: {e}"}

    finally:
        driver.quit()


# Example usage
if __name__ == "__main__":
    domain_name = "bizzycar.com"
    scraped_data = scrape_mxtoolbox(domain_name)
    print(json.dumps(scraped_data, indent=4))
