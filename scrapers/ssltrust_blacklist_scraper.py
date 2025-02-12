from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_ssltrust_blacklist(domain_name):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Initialize WebDriver without ChromeDriverManager
    service = Service()  # Use the system-installed ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://www.ssltrust.com/ssl-tools/website-security-check")
        
        # Wait for the input field and enter the domain
        input_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.el-input__inner"))
        )
        input_field.clear()
        input_field.send_keys(domain_name)

        # Click the submit button
        submit_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.el-button.el-button--primary"))
        )
        submit_button.click()

        # Wait for results to load completely
        time.sleep(15)  # Additional wait time to ensure processing completes
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//p/strong[contains(text(),'Status:')]/.."))
        )

        # Extract results
        results = {"Status": "Unknown", "Results": "Unknown"}
        
        try:
            status_element = driver.find_element(By.XPATH, "//p/strong[contains(text(),'Status:')]/..")
            results["Status"] = status_element.text.replace("Status:", "").strip()

            results_element = driver.find_element(By.XPATH, "//p/strong[contains(text(),'Results:')]/..")
            results["Results"] = results_element.text.replace("Results:", "").strip()

        except Exception as e:
            results["error"] = f"Failed to extract results: {e}"

        return results

    except Exception as e:
        return {"error": f"Error scraping {domain_name}: {e}"}

    finally:
        driver.quit()

if __name__ == "__main__":
    domain = "remitpe.com"
    result = scrape_ssltrust_blacklist(domain)
    print(result)
