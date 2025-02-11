import json
import os
from datetime import datetime
from utils.save_data import save_data

# Define risk categories
RISK_CATEGORIES = {
    "low_risk": (0, 45),
    "med_risk": (45, 81),
    "high_risk": (81, 100)
}

def calculate_risk_score(data):
    """Calculates the risk score based on boolean-based conditions."""
    risk_score = 0

    try:
        # Privacy & Terms
        privacy_and_terms = data.get("privacy_and_terms")
        if privacy_and_terms:
            risk_score += 5 if privacy_and_terms.get("is_accessible") is False else 0
            risk_score += 5 if privacy_and_terms.get("terms_of_service_present") is False else 0
            risk_score += 5 if privacy_and_terms.get("privacy_policy_present") is False else 0

        # HTTPS & SSL
        https_check = data.get("https_check")
        ssl_fingerprint = data.get("ssl_sha_256_fingerprint")
        if https_check:
            risk_score += 12 if not https_check.get("has_https") else 0
        if ssl_fingerprint:
            risk_score += 12 if not ssl_fingerprint.get("has_sha256") else 0

        # Social Media Presence
        social_presence = json.loads(data.get("social_presence", "{}"))
        if social_presence:
            social_accounts = social_presence.get("social_presence", {})
            risk_score += 6 if not social_accounts.get("linkedin", {}).get("presence", False) else 0
            risk_score -= 2 if social_accounts.get("instagram", {}).get("presence", False) else 0
            risk_score -= 3 if social_accounts.get("youtube", {}).get("presence", False) else 0

        # Domain Age & WHOIS Info
        whois_creation_date = data.get("whois", {}).get("creation_date")
        urlvoid_registered_on = data.get("urlvoid", {}).get("registered_on")
        if not whois_creation_date and not urlvoid_registered_on:
            risk_score += 8  # Penalize only if both are missing

        # URLVoid & IPVoid Security Scans
        urlvoid = data.get("urlvoid")
        ipvoid = data.get("ipvoid")
        if urlvoid:
            risk_score += 6 if urlvoid.get("detections_counts", {}).get("detected", 0) > 0 else 0
        if ipvoid:
            risk_score += 6 if ipvoid.get("detections_count", {}).get("detected", 0) > 0 else 0

        # SSL Trust & Certificate Issues
        ssltrust_results = data.get("ssltrust_blacklist", {}).get("results", "").lower()
        if ssltrust_results:
            risk_score += 7 if "0 positives" not in ssltrust_results else 0

        ssl_org_report = data.get("ssl_org_report", {}).get("report_summary", {})
        if ssl_org_report:
            risk_score += 6 if "certificate is valid and trusted" not in ssl_org_report.get("status", "").lower() else 0
            risk_score += 6 if "warnings" in ssl_org_report.get("warnings", "").lower() else 0

        # Google Safe Browsing
        google_safe_status = data.get("google_safe_browsing", {}).get("Current Status", "").lower()
        if google_safe_status:
            risk_score += 7 if "no unsafe content found" not in google_safe_status else 0

        # Tranco Ranking
        tranco_rank = data.get("tranco_list", {}).get("Tranco Rank", "--")
        if tranco_rank in ["--", "0"]:
            risk_score += 4

        # SimilarWeb Data
        similarweb_data = data.get("similarweb_data", {})
        if not similarweb_data or all(value == "NA" for value in similarweb_data.values()):
            risk_score += 4  # Penalize if SimilarWeb data is not available

        # MXToolbox Blacklist & Email Issues
        for problem in data.get("mxtoolbox", {}).get("Problem Table", []):
            if problem.get("Status") == "Status Problem" and problem.get("Category") == "dmarc":
                risk_score += 8
            elif problem.get("Status") == "Status Problem" and problem.get("Category") == "blacklist":
                risk_score += 8
            elif problem.get("Status") == "Status Problem" and problem.get("Category") == "smtp":
                risk_score += 8

        # Page Size & Performance
        page_size_str = data.get("page_size", {}).get("Page Size (KB)", "0 KB").replace("~", "").split()[0]
        try:
            page_size_kb = int(page_size_str)
            risk_score += 9 if page_size_kb < 100 else 0
        except ValueError:
            pass

        # Popups & Ads
        popup_ads = data.get("popup_and_ads")
        if popup_ads:
            risk_score += 7 if popup_ads.get("has_popups") else 0
            risk_score += 4 if popup_ads.get("has_ads") else 0

    except Exception as e:
        print(f"⚠️ Error calculating risk score: {e}")

    return risk_score


def categorize_risk(score):
    """Assigns a risk category based on the score."""
    for category, (low, high) in RISK_CATEGORIES.items():
        if low <= score < high:
            return category
    return "high_risk"


def assess_risk(domain):
    """Loads JSON data, calculates risk, and saves the updated data."""
    json_file_path = os.path.join("data", f"{domain}.json")

    if not os.path.exists(json_file_path):
        print(f"❌ No data found for domain: {domain}")
        return

    with open(json_file_path, "r") as file:
        data = json.load(file)

    # Calculate risk score
    risk_score = calculate_risk_score(data)
    risk_category = categorize_risk(risk_score)
    assessment_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Append risk score to data
    data["risk_score"] = risk_score
    data["risk_category"] = risk_category
    data["datetime_assessment"] = assessment_time

    # Save updated data
    save_data(domain, **data)
    print(f"✅ Risk assessment completed for {domain} with score {risk_score} ({risk_category}).")


if __name__ == "__main__":
    domain_name = "amazon.com"
    assess_risk(domain_name)
