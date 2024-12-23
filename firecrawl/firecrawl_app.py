import requests

def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text  # In a real scraper, you'd extract specific data
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to scrape the website: {e}")
