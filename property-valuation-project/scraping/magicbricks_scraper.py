import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# URL to scrape
url = "https://www.magicbricks.com/property-for-sale/residential-real-estate?bedroom=2,3&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residential-House,Villa&cityName=Kalyan"

# Function to scroll and load all the listings
def scroll_and_load():
    # Initialize Selenium WebDriver (Make sure to have the appropriate driver, e.g., chromedriver)
    driver = webdriver.Chrome()

    # Navigate to the page
    driver.get(url)

    # Scroll until all elements are loaded
    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new posts to load
        time.sleep(SCROLL_PAUSE_TIME)
        
        # Calculate new scroll height and compare with the last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # After scrolling, get the full page source
    page_source = driver.page_source
    driver.quit()
    return page_source

# Function to scrape property data from the overview cards
def scrape_property_listings(page_source):
    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Extract the relevant property cards
    property_cards = soup.find_all("div", class_="mb-srp__list")

    # List to hold the scraped data
    properties = []

    # Iterate through the property cards
    for card in property_cards:
        # Scraping various details from each card
        title = card.find("h2", class_="mb-srp__card--title").get_text(strip=True)
        price = card.find("div", class_="mb-srp__card__price--amount").get_text(
            strip=True
        )
        location = title.split("in")[-1].strip()  # Extracting location from title
        area = (
            card.find("div", {"data-summary": "carpet-area"})
            .find("div", class_="mb-srp__card__summary--value")
            .get_text(strip=True)
            if card.find("div", {"data-summary": "carpet-area"})
            else None
        )
        status = (
            card.find("div", {"data-summary": "status"})
            .find("div", class_="mb-srp__card__summary--value")
            .get_text(strip=True)
            if card.find("div", {"data-summary": "status"})
            else None
        )
        floor = (
            card.find("div", {"data-summary": "floor"})
            .find("div", class_="mb-srp__card__summary--value")
            .get_text(strip=True)
            if card.find("div", {"data-summary": "floor"})
            else None
        )
        furnishing = (
            card.find("div", {"data-summary": "furnishing"})
            .find("div", class_="mb-srp__card__summary--value")
            .get_text(strip=True)
            if card.find("div", {"data-summary": "furnishing"})
            else None
        )
        bathrooms = (
            card.find("div", {"data-summary": "bathroom"})
            .find("div", class_="mb-srp__card__summary--value")
            .get_text(strip=True)
            if card.find("div", {"data-summary": "bathroom"})
            else None
        )
        balconies = (
            card.find("div", {"data-summary": "balcony"})
            .find("div", class_="mb-srp__card__summary--value")
            .get_text(strip=True)
            if card.find("div", {"data-summary": "balcony"})
            else None
        )
        parking = (
            card.find("div", {"data-summary": "parking"})
            .find("div", class_="mb-srp__card__summary--value")
            .get_text(strip=True)
            if card.find("div", {"data-summary": "parking"})
            else None
        )
        facing = (
            card.find("div", {"data-summary": "facing"})
            .find("div", class_="mb-srp__card__summary--value")
            .get_text(strip=True)
            if card.find("div", {"data-summary": "facing"})
            else None
        )
        img_url = (
            card.find("img", class_="mb-srp__card__photo__fig--graphic")["src"]
            if card.find("img", class_="mb-srp__card__photo__fig--graphic")
            else None
        )
        posted = (
            card.find("div", class_="mb-srp__card__photo__fig--post").get_text(
                strip=True
            )
            if card.find("div", class_="mb-srp__card__photo__fig--post")
            else None
        )

        # Add the data to the list of properties
        properties.append(
            {
                "Title": title,
                "Price": price,
                "Location": location,
                "Carpet Area": area,
                "Status": status,
                "Floor": floor,
                "Furnishing": furnishing,
                "Bathrooms": bathrooms,
                "Balconies": balconies,
                "Parking": parking,
                "Facing": facing,
                "Image URL": img_url,
                "Posted": posted,
            }
        )

    return properties


# Function to save data to CSV
def save_to_csv(properties):
    # Create a DataFrame from the scraped data
    df = pd.DataFrame(properties)

    # Save to CSV
    df.to_csv("magicbricks_properties.csv", index=False)
    print(f"Data saved {len(properties)} to magicbricks_properties.csv")


if __name__ == "__main__":
    # Scroll and load the full page
    page_source = scroll_and_load()

    # Scrape properties from the loaded page
    properties = scrape_property_listings(page_source)

    if properties:
        save_to_csv(properties)
    else:
        print("No properties found.")
