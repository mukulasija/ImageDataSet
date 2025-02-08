import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# Global variables
NUM_PRODUCTS = 5  # Number of products per category
IMAGES_PER_PRODUCT = 5  # Number of images per product

# Categories and corresponding search queries
CATEGORIES = {
    "Mobile Phones": "mobile phones",
    "Sportswear": "sportswear",
    "Home Appliances": "home appliances",
    "Electronics": "electronics",
    "Fashion_Clothing": "fashion clothing"
}

def setup_driver():
    """Set up Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    return webdriver.Chrome(options=options)

def get_product_links(driver, search_query, num_products):
    """Extract product page links from Flipkart search results."""
    search_url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(3)  # Wait for content to load

    # Scroll down to load more results
    for _ in range(3):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)

    # Parse page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find product links
    product_links = []
    for a_tag in soup.find_all("a", href=True):
        if "/p/" in a_tag["href"]:  # Flipkart product pages contain "/p/"
            product_links.append("https://www.flipkart.com" + a_tag["href"].split("?")[0])

    return list(set(product_links))[:num_products]  # Remove duplicates and limit results

def get_product_images(driver, product_url, num_images):
    """Extract multiple image URLs from a product page."""
    driver.get(product_url)
    time.sleep(2)  # Allow images to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Find all images in the product page
    image_tags = soup.find_all("img", {"src": True})
    image_urls = [img["src"] for img in image_tags if "http" in img["src"]]
    
    return image_urls[:num_images]  # Return the first `num_images` URLs

def download_images(image_urls, category, product_num):
    """Download images and save them in category-wise folders."""
    folder_path = os.path.join("flipkart_images", category, f"Product_{product_num}")
    os.makedirs(folder_path, exist_ok=True)

    for i, img_url in enumerate(image_urls):
        try:
            img_data = requests.get(img_url).content
            with open(f"{folder_path}/image_{i}.jpg", "wb") as f:
                f.write(img_data)
            print(f"Downloaded: {category}/Product_{product_num}/image_{i}.jpg")
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")

if __name__ == "__main__":
    driver = setup_driver()

    for category, query in CATEGORIES.items():
        print(f"\nProcessing category: {category}...")

        product_links = get_product_links(driver, query, NUM_PRODUCTS)

        for product_num, product_url in enumerate(product_links):
            print(f"Fetching images for Product {product_num + 1} in {category}...")
            image_urls = get_product_images(driver, product_url, IMAGES_PER_PRODUCT)
            download_images(image_urls, category, product_num + 1)

    driver.quit()
