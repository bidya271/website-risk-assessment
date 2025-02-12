from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import tldextract
import json
import time
import re

def setup_driver():
    """
    Initializes a Selenium WebDriver with necessary options.
    """
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--ignore-certificate-errors")  # Bypass SSL errors
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service()  # Use system-installed ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def extract_text(driver, by, value):
    """
    Extracts text safely from an element, handling missing elements gracefully.
    """
    try:
        text = driver.find_element(by, value).text.strip()
        return text if text else None
    except:
        return None

def extract_link(driver, by, value):
    """
    Extracts link safely from an element.
    """
    try:
        link = driver.find_element(by, value).get_attribute("href")
        return link if link else None
    except:
        return None

def get_social_links(domain, driver):
    """
    Scrapes the homepage of the domain for LinkedIn, Facebook, Instagram, Twitter, and YouTube URLs.
    """
    website_url = f"https://{domain}"
    social_links = {
        "linkedin": None,
        "facebook": None,
        "instagram": None,
        "twitter": None,
        "youtube": None
    }

    try:
        driver.get(website_url)
        time.sleep(5)  # Allow JavaScript to load

        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            if href:
                if "linkedin.com/company" in href and not social_links["linkedin"]:
                    social_links["linkedin"] = href
                elif "facebook.com" in href and not social_links["facebook"]:
                    social_links["facebook"] = href
                elif "instagram.com" in href and not social_links["instagram"]:
                    social_links["instagram"] = href
                elif "twitter.com" in href or "x.com" in href and not social_links["twitter"]:
                    social_links["twitter"] = href
                elif "youtube.com" in href or "youtu.be" in href and not social_links["youtube"]:
                    social_links["youtube"] = href

    except Exception as e:
        print(f"Failed to scrape homepage: {str(e)}")

    return social_links

def check_social_presence(domain):
    """
    Uses Selenium to check for social media presence, scrape LinkedIn 'About Us', company details, employees list, and employee count.
    """
    details = {
        "domain_name": domain,
        "social_presence": {
            "linkedin": {"presence": False, "link": None},
            "facebook": {"presence": False, "link": None},
            "instagram": {"presence": False, "link": None},
            "twitter": {"presence": False, "link": None},
            "youtube": {"presence": False, "link": None}
        },
        "linkedin_company_details": {},
        "employees": [],
        "employee_count": None
    }

    driver = setup_driver()

    # **Step 1: Get Social Media URLs from Website**
    social_links = get_social_links(domain, driver)

    # Assign found social links and set presence to True
    for platform, link in social_links.items():
        if link:
            details["social_presence"][platform] = {"presence": True, "link": link}

    # **Step 2: Get LinkedIn URL from website or construct it**
    linkedin_url = social_links["linkedin"]
    if not linkedin_url:
        base_domain = tldextract.extract(domain).domain
        linkedin_url = f"https://www.linkedin.com/company/{base_domain}"

    try:
        driver.get(linkedin_url)
        time.sleep(5)  # Wait for page to load

        if "Page Not Found" not in driver.title:
            details["social_presence"]["linkedin"]["presence"] = True
            details["social_presence"]["linkedin"]["link"] = linkedin_url

            # Scrape About Us section
            linkedin_data = {
                "about_us": extract_text(driver, By.CSS_SELECTOR, "p[data-test-id='about-us__description']"),
                "website": extract_link(driver, By.CSS_SELECTOR, "a[data-tracking-control-name='about_website']"),
                "industry": extract_text(driver, By.CSS_SELECTOR, "dd[data-test-id='about-us__industry']"),
                "company_size": extract_text(driver, By.CSS_SELECTOR, "dd[data-test-id='about-us__size']"),
                "type": extract_text(driver, By.CSS_SELECTOR, "dd[data-test-id='about-us__organizationType']"),
                "founded": extract_text(driver, By.CSS_SELECTOR, "dd[data-test-id='about-us__foundedOn']"),
                "specialties": extract_text(driver, By.CSS_SELECTOR, "dd[data-test-id='about-us__specialties']")
            }

            # Remove empty/null fields
            details["linkedin_company_details"] = {k: v for k, v in linkedin_data.items() if v}

            # Extract and clean employee count
            employee_count_text = extract_text(driver, By.CSS_SELECTOR, "p.face-pile__text")
            if employee_count_text:
                count_match = re.search(r"\d+", employee_count_text)  # Extracts only numbers
                details["employee_count"] = count_match.group(0) if count_match else None

            # Scrape employee details
            employees = driver.find_elements(By.CSS_SELECTOR, "a[data-tracking-control-name='org-employees']")
            for employee in employees:
                employee_data = {
                    "name": extract_text(employee, By.CSS_SELECTOR, "h3.base-main-card__title"),
                    "position": extract_text(employee, By.CSS_SELECTOR, "h4.base-main-card__subtitle"),
                    "profile_link": employee.get_attribute("href"),
                    "profile_image": extract_link(employee, By.TAG_NAME, "img")
                }

                # Remove empty/null fields
                filtered_employee = {k: v for k, v in employee_data.items() if v}
                if filtered_employee:  # Only add if there is data
                    details["employees"].append(filtered_employee)

    except Exception as e:
        details["error"] = f"Failed to scrape LinkedIn: {str(e)}"

    driver.quit()  # Close the WebDriver

    # Remove empty fields from the final JSON output
    details = {k: v for k, v in details.items() if v and v != {}}

    return json.dumps(details, indent=4)

if __name__ == "__main__":
    domain = "adworld.ie"
    result = check_social_presence(domain)
    print(result)
