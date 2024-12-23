# import requests
# from bs4 import BeautifulSoup
# import json
# import re
# import logging
# import random
# import time

# # Configure logging
# logging.basicConfig(
#     filename='scraper.log',
#     filemode='a',
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

# SCRAPERAPI_KEY = '6691a8fe740598b48c52131581d4d296'
# USER_AGENTS = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
# ]

# def fetch_page_content(url):
#     api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}&render=true"
#     headers = {'User-Agent': random.choice(USER_AGENTS)}

#     try:
#         response = requests.get(api_url, headers=headers, timeout=70)
#         if response.status_code == 200:
#             with open("response_debug.html", "w", encoding="utf-8") as f:
#                 f.write(response.text)
#             logging.info(f"Successfully fetched URL: {url}")
#             return response.text
#         else:
#             logging.error(f"Failed to fetch URL: {url} - Status Code: {response.status_code}")
#             return None
#     except requests.exceptions.RequestException as e:
#         logging.error(f"An error occurred while fetching the page: {e}")
#         return None

# def clean_text(text):
#     """
#     Clean and strip unnecessary spaces from the text.
#     """
#     return re.sub(r'\s+', ' ', text.strip()) if text else "N/A"

# def parse_products(html_content):
#     """
#     Parse product data from the HTML content.
#     """
#     soup = BeautifulSoup(html_content, 'html.parser')
#     product_list = []

#     # Save the HTML content for debugging
#     with open("debug.html", "w", encoding="utf-8") as f:
#         f.write(html_content)

#     # Find all product containers
#     # Updated selector based on the current BestBuy HTML structure
#     product_containers = soup.find_all('li', {'class': re.compile('^sku-item')})

#     if not product_containers:
#         logging.warning("No product containers found. Check 'debug.html' for potential issues.")
#         return product_list

#     print(f"Found {len(product_containers)} product containers")

#     for container in product_containers:
#         try:
#             # Extract Product Name
#             product_name_tag = container.select_one('h4.sku-header a')  # Adjust this selector
#             if not product_name_tag:
#                 # Try an alternative selector
#                 product_name_tag = container.select_one('h4.product-title a')
#             product_name = clean_text(product_name_tag.text) if product_name_tag else "N/A"

#             # Extract Product Link
#             product_link = f"https://www.bestbuy.com{product_name_tag['href']}" if product_name_tag else "N/A"

#             # Extract Price
#             price_tag = container.find('div', class_='priceView-hero-price priceView-customer-price')
#             product_price = clean_text(price_tag.find('span').text) if price_tag else "N/A"

#             # Extract Image URL
#             image_tag = container.find('img', class_=re.compile('^product-image'))
#             image_url = image_tag['src'] if image_tag else "N/A"

#             # Extract Rating
#             rating_tag = container.find('span', class_=re.compile('c-review-average'))
#             if not rating_tag:
#                 # Try an alternative selector
#                 rating_tag = container.find('span', class_=re.compile('rating'))
#             rating = clean_text(rating_tag.text) if rating_tag else "N/A"

#             # Extract Number of Reviews
#             reviews_count_tag = container.find('span', class_=re.compile('c-review-count'))
#             if not reviews_count_tag:
#                 # Try an alternative selector
#                 reviews_count_tag = container.find('span', class_=re.compile('review-count'))
#             reviews_count = clean_text(reviews_count_tag.text) if reviews_count_tag else "N/A"

#             # Append product details to the list
#             product_list.append({
#                 "name": product_name,
#                 "link": product_link,
#                 "price": product_price,
#                 "image_url": image_url,
#                 "rating": rating,
#                 "reviews_count": reviews_count,
#             })

#         except Exception as e:
#             logging.error(f"Error parsing product container: {e}")
#             product_list.append({
#                 "name": "Error",
#                 "link": "Error",
#                 "price": "Error",
#                 "image_url": "Error",
#                 "rating": "Error",
#                 "reviews_count": "Error",
#             })

#     return product_list

# def process_product_page(url):
#     """
#     Fetch, parse, and process product data from the target URL.
#     """
#     print(f"Processing: {url}")
#     html_content = fetch_page_content(url)

#     if html_content:
#         products = parse_products(html_content)
#         print("Structured Data:")
#         print(json.dumps(products, indent=4))
#         return products
#     return None

# def save_to_json(data, filename="products_data.json"):
#     """
#     Save the parsed product data to a JSON file.
#     """
#     try:
#         with open(filename, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=4)
#         logging.info(f"Product data saved to {filename}")
#         print(f"Product data saved to {filename}")
#     except IOError as e:
#         logging.error(f"An error occurred while saving to {filename}: {e}")
#         print(f"An error occurred while saving to {filename}: {e}")

# if __name__ == "__main__":
#     # Replace with the URL of your target page
#     target_url = 'https://www.bestbuy.com/site/searchpage.jsp?st=apple'
#     products_data = process_product_page(target_url)
#     if products_data:
#         save_to_json(products_data)
#     time.sleep(random.uniform(1, 3))
import requests
from bs4 import BeautifulSoup
import json
import re
import logging
import random
import time

# Configure logging
logging.basicConfig(
    filename='scraper.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

SCRAPERAPI_KEY = '6691a8fe740598b48c52131581d4d296'

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]

def fetch_page_content(url):
    api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}&render=true"
    headers = {'User-Agent': random.choice(USER_AGENTS)}

    try:
        response = requests.get(api_url, headers=headers, timeout=70)
        if response.status_code == 200:
            with open("response_debug.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            logging.info(f"Successfully fetched URL: {url}")
            return response.text
        else:
            logging.error(f"Failed to fetch URL: {url} - Status Code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching the page: {e}")
        return None

def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

def parse_products(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    product_list = []

    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})

    if not product_containers:
        logging.warning("No product containers found. Check 'debug.html' for potential issues.")
        return product_list

    print(f"Found {len(product_containers)} product containers")

    for container in product_containers:
        try:
            # Extract Product Name
            product_name = container.h2.text if container.h2 else "N/A"

            # Extract Product Link
            product_link = container.h2.a['href'] if container.h2 and container.h2.a else "N/A"
            if product_link != "N/A":
                product_link = f"https://www.amazon.in{product_link}"

            # Extract Price
            price_whole = container.find('span', class_='a-price-whole')
            price_fraction = container.find('span', class_='a-price-fraction')
            product_price = "N/A"
            if price_whole:
                product_price = price_whole.text.replace(',', '').strip()
                if price_fraction:
                    product_price += f".{price_fraction.text.strip()}"

            # Extract Image URL
            image_tag = container.find('img', class_='s-image')
            image_url = image_tag['src'] if image_tag else "N/A"

            # Extract Rating
            rating_tag = container.find('span', class_='a-icon-alt')
            rating = rating_tag.text if rating_tag else "N/A"

            # Extract Number of Reviews
            reviews_count_tag = container.find('span', {'class': 'a-size-base'})
            reviews_count = reviews_count_tag.text.replace(',', '') if reviews_count_tag else "N/A"

            # Append product details to the list
            product_list.append({
                "name": clean_text(product_name),
                "link": product_link,
                "price": product_price,
                "image_url": image_url,
                "rating": clean_text(rating),
                "reviews_count": clean_text(reviews_count),
            })

        except Exception as e:
            logging.error(f"Error parsing product container: {e}")

    return product_list

def process_product_page(url):
    print(f"Processing: {url}")
    html_content = fetch_page_content(url)

    if html_content:
        products = parse_products(html_content)
        print("Structured Data:")
        print(json.dumps(products, indent=4))
        return products
    return None

def save_to_json(data, filename="products_data.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logging.info(f"Product data saved to {filename}")
        print(f"Product data saved to {filename}")
    except IOError as e:
        logging.error(f"An error occurred while saving to {filename}: {e}")
        print(f"An error occurred while saving to {filename}: {e}")

if __name__ == "__main__":
    target_url = 'https://www.amazon.in/s?k=tv'
    products_data = process_product_page(target_url)
    if products_data:
        save_to_json(products_data)
    time.sleep(random.uniform(1, 3))
