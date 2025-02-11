import re
import requests
from bs4 import BeautifulSoup

def scrape_ipvoid(ip_address):
    """
    Uses requests to fetch IPVoid blacklist data, then post-processes it for better readability.
    Ensures all output follows the snake_case format.
    """
    url = "https://www.ipvoid.com/ip-blacklist-check/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.ipvoid.com/",
    }

    form_data = {
        "ipaddr": ip_address
    }

    try:
        response = requests.post(url, headers=headers, data=form_data)
        if response.status_code != 200:
            return {"error": f"failed_to_fetch_data_for_ip_{ip_address}", "status_code": response.status_code}

        soup = BeautifulSoup(response.text, "html.parser")

        raw_data = {
            "checked_on": "unknown",
            "elapsed_time": "unknown",
            "detections_count": "unknown",
            "ip_address": "unknown",
            "reverse_dns": "unknown",
            "asn": "unknown",
            "isp": "unknown",
            "continent": "unknown",
            "country_code": "unknown",
            "latitude_longitude": "unknown",
            "city": "unknown",
            "region": "unknown"
        }

        table = soup.find("table", class_="table-striped")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) == 2:
                    key = cells[0].text.strip().lower().replace(" ", "_")  # Convert to snake_case
                    value = cells[1]

                    if key in raw_data:
                        raw_data[key] = value.text.strip()

                    if "ip_address" in key:
                        ip_address_element = value.find("strong")
                        raw_data["ip_address"] = ip_address_element.text.strip() if ip_address_element else "unknown"

                    if "latitude_longitude" in key:
                        latlong_link = value.find("a", href=True)
                        raw_data["latitude_longitude"] = latlong_link["href"] if latlong_link else "unknown"

        return format_ipvoid_data(raw_data)

    except Exception as e:
        return {"error": f"error_scraping_ip_{ip_address}", "details": str(e)}

def format_ipvoid_data(data):
    """
    Post-processes raw IPVoid data for better readability while ensuring snake_case formatting.
    """
    formatted_data = {}

    # 1️⃣ Extract "checked_on" and "elapsed_time"
    formatted_data["checked_on"] = data.get("checked_on", "unknown")
    formatted_data["elapsed_time"] = data.get("elapsed_time", "unknown")

    # 2️⃣ Format detection_count
    if "detections_count" in data:
        match = re.match(r"(\d+)/(\d+)", data["detections_count"])
        if match:
            formatted_data["detections_count"] = {
                "detected": int(match.group(1)),
                "checks": int(match.group(2))
            }
        else:
            formatted_data["detections_count"] = data["detections_count"]

    # 3️⃣ Extract only the IP address
    formatted_data["ip_address"] = data.get("ip_address", "unknown")

    # 4️⃣ Convert Latitude/Longitude into a Google Maps link
    formatted_data["location"] = data.get("latitude_longitude", "unknown")

    # 5️⃣ Keep other values unchanged
    for key in ["reverse_dns", "asn", "isp", "continent", "country_code", "city", "region"]:
        formatted_data[key] = data.get(key, "unknown")

    return formatted_data

if __name__ == "__main__":
    ip_address = "18.165.122.89"  # Replace with the IP to check
    result = scrape_ipvoid(ip_address)
    print(result)
