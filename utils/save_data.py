import json
import os

def save_data(domain_name, **scraped_data):
    """
    Saves the scraped data to a JSON file in the `data/` directory.

    Args:
        domain_name (str): The domain name being checked (e.g., "bizzycar.com").
        scraped_data (dict): A dictionary containing scraped data from various sources.
    """
    # Ensure the data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")

    # Construct file path
    file_path = f"data/{domain_name}.json"

    # Prepare JSON content
    data_to_save = {
        "domain": domain_name,
        **scraped_data  # Merge all scraper data dynamically
    }

    # Validate JSON format before saving
    try:
        json_data = json.dumps(data_to_save, indent=4)  # Ensures JSON validity
    except Exception as e:
        print(f"❌ Error: Invalid JSON format - {e}")
        return

    # Save JSON data to file
    try:
        with open(file_path, 'w') as f:
            f.write(json_data)
        print(f"✅ Data saved successfully to {file_path}")
    except Exception as e:
        print(f"❌ Error: Failed to save data - {e}")
