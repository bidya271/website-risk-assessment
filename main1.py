import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrapers.check_https import check_https
from scrapers.whois_sraper import get_whois_data
from scrapers.get_ssl_fingerprint import get_ssl_fingerprint
from scrapers.check_privacy_term import check_privacy_term
from scrapers.cloudflare_scraper import initiate_scan
from scrapers.godaddy_whois_scraper import scrape_godaddy_whois
from scrapers.urlvoid_scraper import scrape_urlvoid
from scrapers.ipvoid_scraper import scrape_ipvoid
from scrapers.ssl_org_scraper import scrape_ssl_org
from scrapers.ssltrust_blacklist_scraper import scrape_ssltrust_blacklist
from scrapers.google_safe_browsing_scraper import scrape_google_safe_browsing
from scrapers.tranco_list_scraper import scrape_tranco_list
from scrapers.scrape_similarweb_data import scrape_similarweb_data
from scrapers.mxtool_scraper import scrape_mxtoolbox
from scrapers.pagesize_scraper import scrape_page_size
from scrapers.check_linkedin import check_social_presence
from scrapers.check_popup_ads import check_popups_ads
from utils.save_data import save_data
from utils.risk_scoring import assess_risk  

# Define risky country codes
RISKY_COUNTRIES = {
    "CU", "IR", "KP", "SY", "RU", "BY", "MM", "VE", "YE", "ZW", 
    "SD", "SS", "LY", "SO", "CF", "CD", "UA"
}

def run_scraper(scraper_func, domain, default_value=None, delay=0):
    """Runs a scraper and catches exceptions, returning a default value on failure."""
    try:
        result = scraper_func(domain)
        time.sleep(delay)  # Maintain execution delays
        return result
    except Exception as e:
        print(f"⚠️ Error in {scraper_func.__name__}: {e}")
        return default_value

def main():
    domain_name = input("Enter the domain name to check: ").strip()
    scraped_results = {}

    # **Step 1: Initiate Cloudflare Scan (Runs Separately)**
    print("⏳ Starting Cloudflare Scan...")
    cloudflare_result = run_scraper(initiate_scan, domain_name, {}, delay=5)
    scraped_results["cloudflare_scan"] = cloudflare_result
    print("✅ Cloudflare Scan Initiated.")

    # **Step 2: Define Scrapers & Their Execution Delays**
    scrapers = {
        "privacy_and_terms": (check_privacy_term, 3),
        "https_check": (check_https, 3),
        "ssl_sha_256_fingerprint": (get_ssl_fingerprint, 3),
        "social_presence": (check_social_presence, 3),
        "whois": (get_whois_data, 3),
        "godaddy_whois": (scrape_godaddy_whois, 5),
        "urlvoid": (scrape_urlvoid, 3),
        "ssltrust_blacklist": (scrape_ssltrust_blacklist, 5),
        "ssl_org_report": (scrape_ssl_org, 5),
        "google_safe_browsing": (scrape_google_safe_browsing, 5),
        "tranco_list": (scrape_tranco_list, 5),
        "similarweb_data": (scrape_similarweb_data, 5),
        "mxtoolbox": (scrape_mxtoolbox, 10),
        "page_size": (scrape_page_size, 3),
        "popup_and_ads": (check_popups_ads, 3),
    }

    # **Step 3: Run Scrapers Concurrently**
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_scraper = {
            executor.submit(run_scraper, scraper, domain_name, {}, delay): name
            for name, (scraper, delay) in scrapers.items()
        }

        for future in as_completed(future_to_scraper):
            name = future_to_scraper[future]
            try:
                scraped_results[name] = future.result()
                print(f"✅ {name.replace('_', ' ').title()} Data Retrieved.")
            except Exception as e:
                print(f"⚠️ Error retrieving {name}: {e}")
                scraped_results[name] = {}

    # **Step 4: Extract IP and Run IPVoid**
    ip_address = scraped_results.get("urlvoid", {}).get("ip_address")
    if ip_address:
        scraped_results["ipvoid"] = run_scraper(scrape_ipvoid, ip_address, {}, delay=4)
        print(f"✅ IPVoid Data Retrieved for IP: {ip_address}")
    else:
        scraped_results["ipvoid"] = {"error": "No IP Address found in URLVoid."}
        print("⚠️ No IP Address found in URLVoid response, skipping IPVoid.")

    # **Step 5: Geopolitical Risk Assessment**
    is_risky = False
    country_code = scraped_results.get("ipvoid", {}).get("country_code", "").split(" ")[0].strip("()")  

    if country_code in RISKY_COUNTRIES:
        is_risky = True
        print(f"⚠️ Domain {domain_name} is associated with a risky country: {country_code}")

    scraped_results["is_risky_geopolitical"] = {
        "domain": domain_name,
        "is_risky": is_risky,
        "check_datetime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

    # **Step 6: Save & Assess Risk**
    save_data(domain_name, **scraped_results)
    print(f"\n✅ Data saved successfully for {domain_name}!\n")
    assess_risk(domain_name)

if __name__ == "__main__":
    main()
