import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scrape_urlvoid(domain):
    """
    Uses Selenium to interact with URLVoid, enter the domain, submit the form,
    wait for results, and extract relevant details in snake_case format.
    """
    url = "https://www.urlvoid.com/"  # Base URLVoid homepage

    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--ignore-certificate-errors")  # Ignore SSL warnings
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        # Wait for the input field to load
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "hf-domain"))
        )
        input_field.clear()
        input_field.send_keys(domain)
        
        # Locate and click the submit button
        submit_button = driver.find_element(By.CLASS_NAME, "btn-success")
        submit_button.click()

        # Wait for results to load (approx. 15 seconds)
        time.sleep(15)  # Adjust based on network speed

        # Extract updated page source after the scan completes
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        # Extract relevant information
        raw_data = {
            "website_address": "unknown",
            "last_analysis": "unknown",
            "detections_counts": "unknown",
            "domain_registration": "unknown",
            "ip_address": "unknown",
            "reverse_dns": "unknown",
            "asn": "unknown",
            "server_location": "unknown",
            "latitude_longitude": "unknown",
            "city": "unknown",
            "region": "unknown"
        }

        # Locate result table
        table = soup.find("table", class_="table-custom")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) == 2:
                    key = cells[0].text.strip().lower().replace(" ", "_")  # Convert to snake_case
                    value = cells[1].text.strip()

                    if key in raw_data:
                        raw_data[key] = value

        return format_urlvoid_data(raw_data)

    except Exception as e:
        driver.quit()
        return {"error": f"failed_to_scrape_urlvoid: {str(e)}"}

def format_urlvoid_data(data):
    """
    Post-processes raw URLVoid data for better readability while ensuring snake_case formatting.
    """
    formatted_data = {}

    # 1️⃣ Keep only "XX hours ago" for last_analysis
    if "last_analysis" in data:
        formatted_data["last_analysis"] = re.sub(r"\s*\|\s*Rescan", "", data["last_analysis"])

    # 2️⃣ Format detection_count
    if "detections_counts" in data:
        match = re.match(r"(\d+)/(\d+)", data["detections_counts"])
        if match:
            formatted_data["detections_counts"] = {
                "detected": int(match.group(1)),
                "checks": int(match.group(2))
            }
        else:
            formatted_data["detections_counts"] = data["detections_counts"]

    # 3️⃣ Split domain_registration into registered_on & registered_since
    if "domain_registration" in data:
        parts = data["domain_registration"].split("|")
        formatted_data["registered_on"] = parts[0].strip() if len(parts) > 0 else "unknown"
        formatted_data["registered_since"] = parts[1].strip() if len(parts) > 1 else "unknown"

    # 4️⃣ Extract only the IP address
    if "ip_address" in data:
        formatted_data["ip_address"] = re.split(r"\s+", data["ip_address"])[0]

    # 5️⃣ Keep remaining values as they are
    for key in ["website_address", "reverse_dns", "asn", "server_location", "latitude_longitude", "city", "region"]:
        if key in data:
            formatted_data[key] = data[key]

    return formatted_data

if __name__ == "__main__":
    domain = "jenesys.co"  # Replace with the domain to check
    result = scrape_urlvoid(domain)
    print(result)
