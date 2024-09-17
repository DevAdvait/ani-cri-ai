from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta

# URL to scrape
url = "https://www.magicbricks.com/property-for-sale/residential-real-estate?bedroom=2,3&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residential-House,Villa&cityName=Kalyan"

# Reference date (assumed to be 17th September 2024)
reference_date = datetime(2024, 9, 17)

# Function to scroll and load all the listings
def scroll_and_load():
    driver = webdriver.Chrome()
    driver.get(url)

    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    page_source = driver.page_source
    driver.quit()
    return page_source

# Function to process the 'Posted' field and calculate the exact date
def process_posted_date(posted_text):
    posted_text = posted_text.lower()  # Normalize to lowercase for easier comparisons

    if 'updated' in posted_text:
        # Extract the number and the time unit (e.g., "Updated 3 months ago")
        if 'months' in posted_text:
            try:
                months_ago = int(posted_text.split()[1])
                return reference_date - timedelta(days=months_ago * 30)
            except ValueError:
                return posted_text  # Return the original string if parsing fails
        elif 'week' in posted_text:
            try:
                weeks_ago = int(posted_text.split()[1])
                return reference_date - timedelta(weeks=weeks_ago)
            except ValueError:
                return posted_text  # Return the original string if parsing fails
        elif 'day' in posted_text:
            try:
                days_ago = int(posted_text.split()[1])
                return reference_date - timedelta(days=days_ago)
            except ValueError:
                return posted_text  # Return the original string if parsing fails
        elif 'yesterday' in posted_text:
            return reference_date - timedelta(days=1)
        elif 'a few moments ago' in posted_text:
            return reference_date
    elif 'posted:' in posted_text:
        # Parse the exact posted date like "Posted: Sep 15, '24"
        try:
            date_str = posted_text.replace('posted:', '').strip()
            return datetime.strptime(date_str, "%b %d, '%y")
        except ValueError:
            return posted_text  # Return the original string if parsing fails
    return posted_text  # Return the original string if no conditions match


# Function to scrape property data from the overview cards
def scrape_property_listings(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    property_cards = soup.find_all("div", class_="mb-srp__list")
    properties = []

    for card in property_cards:
        title = card.find("h2", class_="mb-srp__card--title").get_text(strip=True)
        price = card.find("div", class_="mb-srp__card__price--amount").get_text(strip=True)
        location = title.split("in")[-1].strip()
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
            card.find("div", class_="mb-srp__card__photo__fig--post").get_text(strip=True)
            if card.find("div", class_="mb-srp__card__photo__fig--post")
            else None
        )
        
        # Process the 'Posted' date to calculate the exact date
        posted_date = process_posted_date(posted)
        formatted_posted_date = (
            posted_date.strftime("%d-%m-%Y") 
            if isinstance(posted_date, datetime) 
            else posted_date
        )

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
                "Posted": formatted_posted_date,  # Use the formatted exact date
            }
        )


    return properties












# Function to save data to CSV
def save_to_csv(properties):
    df = pd.DataFrame(properties)
    df.to_csv("magicbricks_properties.csv", index=False)
    print(f"Data saved {len(properties)} to magicbricks_properties.csv")

if __name__ == "__main__":
    page_source = scroll_and_load()
    properties = scrape_property_listings(page_source)
    if properties:
        save_to_csv(properties)
    else:
        print("No properties found.")
