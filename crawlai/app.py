import asyncio
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import json
import re
import random
import logging
import time

# Configure logging
logging.basicConfig(
    filename='bestbuy_scraper.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# List of User Agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    ' Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)'
    ' Chrome/91.0.4472.124 Safari/537.36',
    # Add more user agents as needed
]

async def main():
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
    }

    async with AsyncWebCrawler(headers=headers, verbose=True) as crawler:
        start_url = 'https://www.bestbuy.com/site/searchpage.jsp?st=tv&intl=nosplash'
        all_products = []
        current_url = start_url

        while current_url:
            logging.info(f"Processing URL: {current_url}")
            result = await crawler.arun(url=current_url)
            html_content = result.html

            # Save HTML for debugging
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(html_content)

            soup = BeautifulSoup(html_content, 'html.parser')
            product_containers = soup.find_all('li', class_=re.compile('^sku-item'))

            if not product_containers:
                logging.warning(f"No product containers found on {current_url}.")
                break

            print(f"Found {len(product_containers)} product containers on {current_url}")

            for container in product_containers:
                try:
                    # Extract Product Name
                    product_name_tag = container.select_one('h4.sku-header a') or container.select_one('h4.product-title a')
                    product_name = product_name_tag.get_text(strip=True) if product_name_tag else "N/A"

                    # Extract Product Link
                    product_link = f"https://www.bestbuy.com{product_name_tag['href']}" if product_name_tag and 'href' in product_name_tag.attrs else "N/A"

                    # Extract Price
                    price_tag = container.find('div', class_=re.compile('priceView-hero-price'))
                    product_price = price_tag.find('span').get_text(strip=True) if price_tag else "N/A"

                    # Extract Image URL
                    image_tag = container.find('img', class_=re.compile('product-image'))
                    image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else "N/A"

                    # Extract Rating
                    rating_tag = container.find('span', class_=re.compile('c-review-average'))
                    rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

                    # Extract Number of Reviews
                    reviews_count_tag = container.find('span', class_=re.compile('c-review-count'))
                    reviews_count = reviews_count_tag.get_text(strip=True) if reviews_count_tag else "N/A"

                    # Append to all_products list
                    all_products.append({
                        "name": product_name,
                        "link": product_link,
                        "price": product_price,
                        "image_url": image_url,
                        "rating": rating,
                        "reviews_count": reviews_count,
                    })

                except Exception as e:
                    logging.error(f"Error parsing a product container: {e}")
                    logging.debug(f"Container HTML: {container.prettify()}")
                    continue

            # Find the next page URL
            next_page_tag = soup.find('a', {'aria-label': 'Next Page'})
            if next_page_tag and 'href' in next_page_tag.attrs:
                next_page_url = f"https://www.bestbuy.com{next_page_tag['href']}"
                if next_page_url == current_url:
                    logging.info("Next page URL is the same as current. Ending pagination.")
                    break
                current_url = next_page_url
                await asyncio.sleep(random.uniform(1, 3))  # Rate limiting
            else:
                logging.info("No next page found. Ending pagination.")
                break

        # Save the extracted data to JSON
        if all_products:
            with open("bestbuy_products.json", "w", encoding="utf-8") as f:
                json.dump(all_products, f, indent=4)
            logging.info("Product data saved to bestbuy_products.json")
            print("Product data saved to bestbuy_products.json")
        else:
            logging.warning("No products were extracted.")

if __name__ == "__main__":
    asyncio.run(main())
