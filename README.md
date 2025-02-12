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
website_risk_assessment/
│
├── scrapers/                  # Folder for individual website scraping scripts
│   ├── website1_scraper.py    # Scraping script for website 1
│   ├── website2_scraper.py    # Scraping script for website 2
│   └── ...                    # Add more scripts for other websites
│
├── data/                      # Folder to store scraped data for each merchant
│   ├── abc.json               # Scraped data and risk assessment for abc.com
│   ├── xyz.json               # Scraped data and risk assessment for xyz.com
│   └── ...                    # Add more files for other merchants
│
├── utils/                     # Folder for utility functions
│   ├── collate_data.py        # Script to collate data from all scrapers
│   ├── risk_scoring.py        # Script to calculate risk scores
│   └── save_data.py           # Script to save data to JSON files
│
├── models/                    # Folder for AI models (if applicable)
│   ├── risk_model.pkl         # Trained AI model for risk assessment
│   └── ...                    # Add other model-related files
│
├── app/                       # Folder for the user interface (if applicable)
│   ├── main.py                # Main script for the Streamlit/Flask app
│   └── ...                    # Add other app-related files
│
├── requirements.txt           # List of Python dependencies
├── README.md                  # Project documentation
└── main.py                    # Main script to run the entire process
```

## Installation
### Prerequisites
- Python 3.8+
- `pip` package manager

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/bidya271/website-risk-assessment.git
   cd website-risk-assessment
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
   python main1.py --domain example.com
   ```
2. The results will be saved in the `data/` folder as a JSON file.
3. You can also run individual scrapers separately for testing:
   ```sh
   python scrapers/check_https.py --domain example.com
   ```

## Configuration
- Modify risk scoring parameters in `risk_scoring.py`.
- Enable or disable specific scrapers by editing `main.py`.

## Contributing
We welcome contributions! To add a new scraper:
1. Create a new `.py` file in `scrapers/`.
2. Follow the existing modular design.
3. Update `main.py` to include the new scraper.
4. Test and submit a pull request.

## License
Apache 2.0 License

