import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# Global variable for the number of images per category
NUM_IMAGES = 20  

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

def download_images(search_query, category, num_images):
    """Download images for a given category."""
    driver = setup_driver()

    # Flipkart search URL
    search_url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}"
    driver.get(search_url)

    time.sleep(3)  # Wait for dynamic content to load

    # Scroll down to load more images
    for _ in range(3):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)

    # Get page source and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()  # Close Selenium driver

    # Find image elements
    image_tags = soup.find_all("img", {"src": True})

    # Create category-wise directory
    folder_path = os.path.join("flipkart_images", category)
    os.makedirs(folder_path, exist_ok=True)

    # Download images
    count = 0
    for img in image_tags:
        img_url = img["src"]
        if "http" not in img_url:
            continue  # Skip invalid URLs

        try:
            img_data = requests.get(img_url).content
            with open(f"{folder_path}/image_{count}.jpg", "wb") as f:
                f.write(img_data)
            print(f"Downloaded: {category}/image_{count}.jpg")
            count += 1

            if count >= num_images:
                break

        except Exception as e:
            print(f"Failed to download {img_url}: {e}")

if __name__ == "__main__":
    for category, query in CATEGORIES.items():
        print(f"\nDownloading images for category: {category}...")
        download_images(query, category, NUM_IMAGES)
