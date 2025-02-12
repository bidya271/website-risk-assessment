# AI-Based Risk Assessment Tool

## Overview
The **AI-Based Risk Assessment Tool** automates the process of evaluating website riskiness for payment gateway onboarding. It leverages **web scraping, NLP, and AI-driven risk analysis** to continuously improve based on user feedback. The tool follows a **modular design**, making it easy to integrate new scrapers and evaluation methods.

## Features
- **Automated Risk Evaluation**: Extracts and analyzes key risk factors from websites.
- **Cloudflare URL Scanning**: Uses Cloudflare API to scan domains before analysis.
- **HTTPS & SSL Verification**: Checks domain security.
- **LinkedIn Presence Check**: Determines if a company has a LinkedIn profile.
- **Company Details Scraper**: Fetches incorporation and directors' details.
- **MCC Code Recognition**: Uses NLP to classify businesses based on their websites.
- **Modular Design**: Easily add or remove scraping components.
- **JSON Data Storage**: Stores results in structured JSON format.

## Project Structure
```
├── scrapers/                 # Individual website scrapers
│   ├── cloudflare_scraper.py  # Fetches domain scan_id
│   ├── get_scanid_data.py     # Retrieves scan results
│   ├── check_https.py         # Checks if a domain has HTTPS
│   ├── ssl_fingerprint.py     # Retrieves SSL certificate fingerprint
│   ├── linkedin_scraper.py    # Checks LinkedIn presence
│   ├── company_details.py     # Fetches incorporation & directors' info
│   ├── mcc_identifier.py      # Identifies MCC codes using NLP
│   ├── ...                    # Additional scrapers
├── main.py                   # Orchestrates the scrapers
├── save.py                    # Saves scraped data into JSON format
├── data/                      # Folder to store JSON results
├── requirements.txt           # Dependencies
├── README.md                  # Project documentation
```

## Installation
### Prerequisites
- Python 3.8+
- `pip` package manager

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/ai-risk-assessment.git
   cd ai-risk-assessment
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up Cloudflare API credentials (if required):
   - Update `CLOUDFLARE_API_KEY` in `config.py`

## Usage
1. Run the main script to analyze a domain:
   ```sh
   python main.py --domain example.com
   ```
2. The results will be saved in the `data/` folder as a JSON file.
3. You can also run individual scrapers separately for testing:
   ```sh
   python scrapers/check_https.py --domain example.com
   ```

## Configuration
- Modify risk scoring parameters in `config.py`.
- Enable or disable specific scrapers by editing `main.py`.

## Contributing
We welcome contributions! To add a new scraper:
1. Create a new `.py` file in `scrapers/`.
2. Follow the existing modular design.
3. Update `main.py` to include the new scraper.
4. Test and submit a pull request.

## License
Apache 2.0 License

