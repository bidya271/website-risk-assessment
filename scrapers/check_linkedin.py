import requests
from bs4 import BeautifulSoup
import tldextract
import re
import json

def fetch_and_parse_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException:
        return None

def check_social_presence(domain):
    """
    Checks for LinkedIn, Facebook, Instagram, Twitter, and YouTube presence in the website HTML.
    If no links are found, it falls back to checking LinkedIn via a constructed URL.
    """
    social_patterns = {
        'linkedin': r'linkedin\.com/company/|linkedin\.com/in/|linkedin\.com/school/',
        'facebook': r'facebook\.com/',
        'instagram': r'instagram\.com/',
        'twitter': r'twitter\.com/|x\.com/',
        'youtube': r'youtube\.com/|youtu\.be/'
    }
    
    details = {
        "domain_name": domain,
        "social_presence": {
            "linkedin": {"presence": False, "link": None},
            "facebook": {"presence": False, "link": None},
            "instagram": {"presence": False, "link": None, "link1": None},
            "twitter":{"presence": False, "link": None},
            "youtube": {"presence": False, "link": None}
        }
    }
    
    website_url = f"https://{domain}"
    soup = fetch_and_parse_html(website_url)
    found_any = False
    
    for platform, pattern in social_patterns.items():
        links = [a['href'] for a in soup.find_all('a', href=True) if re.search(pattern, a['href'], re.IGNORECASE)] if soup else []
        if links:
            details['social_presence'][platform]['presence'] = True
            details['social_presence'][platform]['link'] = links[0]
            if platform == "instagram" and len(links) > 1:
                details['social_presence'][platform]['link1'] = links[1]
            found_any = True
    
    # Fallback: Check LinkedIn based on constructed URL if no links were found
    if not found_any:
        base_domain = tldextract.extract(domain).domain
        linkedin_url = f"https://www.linkedin.com/company/{base_domain}"
        linkedin_soup = fetch_and_parse_html(linkedin_url)
        is_on_linkedin = linkedin_soup and linkedin_soup.title and 'Page Not Found' not in linkedin_soup.title.string
        
        details['social_presence']['linkedin']['presence'] = is_on_linkedin
        details['social_presence']['linkedin']['link'] = linkedin_url if is_on_linkedin else None
    
    return json.dumps(details, indent=4)

if __name__ == "__main__":
    domain = "remitpe.com"
    result = check_social_presence(domain)
    print(result)
