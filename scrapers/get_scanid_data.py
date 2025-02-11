import os
import json
import time
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Load API key from environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def stage_1_extract_html(scan_id):
    """
    Extracts and saves the entire HTML content of the Cloudflare Radar technology page for the given scan_id.
    """
    try:
        tech_url = f"https://radar.cloudflare.com/scan/{scan_id}/technology"

        # Set up Chrome options for Selenium
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Initialize Selenium WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Load the page
        driver.get(tech_url)

        # Wait for 5 seconds to allow the page to load completely
        time.sleep(5)

        # Extract the HTML content
        html_content = driver.page_source

        # Save the HTML content to a file
        with open("scan_result.html", "w", encoding="utf-8") as file:
            file.write(html_content)

        print("✅ Stage 1 Complete: HTML content saved to 'scan_result.html'")
        return "scan_result.html"

    except Exception as e:
        print(f"An error occurred in Stage 1: {str(e)}")
        return None

    finally:
        driver.quit()

def stage_2_analyze_html(file_path):
    """
    Reads the saved HTML file and uses GPT-4 to analyze the technologies present.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        # Limit the HTML content to 30,000 tokens
        max_tokens = 30000
        html_tokens = html_content.split()
        if len(html_tokens) > max_tokens:
            html_content = ' '.join(html_tokens[:max_tokens])

        # Use GPT-4 to analyze the HTML and extract technologies
        prompt = (
            "Analyze the following HTML content and extract details of the technologies used on the website. "
            "Ensure the response is a valid JSON array formatted as follows:\n"
            "[\n"
            "    {\n"
            "        \"Name\": \"Technology Name\",\n"
            "        \"Description\": \"Brief Description of the Technology\",\n"
            "        \"Website\": \"Official Technology Website\"\n"
            "    }\n"
            "]\n"
            "Only provide the JSON response, without any additional explanation or text.\n\n"
            f"HTML Content:\n{html_content}"
        )

        response = openai.ChatCompletions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in analyzing website technologies."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,  # Adjust based on your needs
            temperature=0.3
        )

        # Extract response content
        response_content = response.choices[0].message["content"].strip()

        # Debugging: Print raw response before JSON parsing
        print("🔍 RAW GPT-4 Response:", response_content)

        # Parse JSON response
        technology_details = json.loads(response_content)

        print("✅ Stage 2 Complete: Technologies extracted successfully!")
        return technology_details

    except json.JSONDecodeError:
        print("Error: Failed to parse JSON. Response content might be invalid.")
        return None
    except Exception as e:
        print(f"An error occurred in Stage 2: {str(e)}")
        return None

if __name__ == "__main__":
    scan_id = "5d5d7ece-3841-4ae1-97f7-658628d65849"

    # Stage 1: Extract HTML
    html_file = stage_1_extract_html(scan_id)

    if html_file:
        # Stage 2: Analyze extracted HTML using GPT-4
        tech_details = stage_2_analyze_html(html_file)

        if tech_details:
            print(json.dumps(tech_details, indent=4))
        else:
            print("❌ Failed to retrieve technology details.")
