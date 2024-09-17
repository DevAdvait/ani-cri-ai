import pandas as pd
from datetime import datetime, timedelta
import logging
import re

# Set up logging
logging.basicConfig(filename='date_processing.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Reference date (today's date)
reference_date = datetime.now()

# Function to process the 'Posted' field and calculate the exact date
def process_posted_date(posted_text):
    posted_text = posted_text.lower().strip()  # Normalize to lowercase and strip extra spaces

    try:
        if "updated" in posted_text:
            if "today" in posted_text:
                return reference_date
            elif "yesterday" in posted_text:
                return reference_date - timedelta(days=1)
            elif "month" in posted_text:
                try:
                    # Extract number of months
                    match = re.search(r'(\d+)\s*month', posted_text)
                    if match:
                        months_ago = int(match.group(1))
                        return reference_date - timedelta(days=months_ago * 30)
                    else:
                        logging.info(f"Unprocessed date (updated months): {posted_text}")
                        return posted_text
                except ValueError:
                    logging.info(f"Unprocessed date (updated months): {posted_text}")
                    return posted_text
            elif "week" in posted_text:
                try:
                    # Extract number of weeks
                    match = re.search(r'(\d+)\s*week', posted_text)
                    if match:
                        weeks_ago = int(match.group(1))
                        return reference_date - timedelta(weeks=weeks_ago)
                    else:
                        logging.info(f"Unprocessed date (updated weeks): {posted_text}")
                        return posted_text
                except ValueError:
                    logging.info(f"Unprocessed date (updated weeks): {posted_text}")
                    return posted_text
            elif "day" in posted_text:
                try:
                    # Extract number of days
                    match = re.search(r'(\d+)\s*day', posted_text)
                    if match:
                        days_ago = int(match.group(1))
                        return reference_date - timedelta(days=days_ago)
                    else:
                        logging.info(f"Unprocessed date (updated days): {posted_text}")
                        return posted_text
                except ValueError:
                    logging.info(f"Unprocessed date (updated days): {posted_text}")
                    return posted_text
            elif "a few moments ago" in posted_text:
                return reference_date
            elif re.search(r'updated\s\w{3}\s\d{1,2},\s\'\d{2}', posted_text):
                try:
                    # Parse the exact date format "updated Jun 21, '24"
                    date_str = re.sub(r'updated\s+', '', posted_text).strip()
                    return datetime.strptime(date_str, "%b %d, '%y")
                except ValueError:
                    logging.info(f"Unprocessed date (updated exact): {posted_text}")
                    return posted_text
        elif "posted:" in posted_text:
            if "yesterday" in posted_text:
                return reference_date - timedelta(days=1)
            elif "month" in posted_text:
                try:
                    # Extract number of months from 'posted: X months ago'
                    match = re.search(r'(\d+)\s*month', posted_text)
                    if match:
                        months_ago = int(match.group(1))
                        return reference_date - timedelta(days=months_ago * 30)
                    else:
                        logging.info(f"Unprocessed date (posted months): {posted_text}")
                        return posted_text
                except ValueError:
                    logging.info(f"Unprocessed date (posted months): {posted_text}")
                    return posted_text
            elif "day" in posted_text:
                try:
                    # Extract number of days from 'posted: X days ago'
                    match = re.search(r'(\d+)\s*day', posted_text)
                    if match:
                        days_ago = int(match.group(1))
                        return reference_date - timedelta(days=days_ago)
                    else:
                        logging.info(f"Unprocessed date (posted days): {posted_text}")
                        return posted_text
                except ValueError:
                    logging.info(f"Unprocessed date (posted days): {posted_text}")
                    return posted_text
            else:
                try:
                    # Parse the exact posted date like "Posted: Sep 15, '24"
                    date_str = posted_text.replace("posted:", "").strip()
                    return datetime.strptime(date_str, "%b %d, '%y")
                except ValueError:
                    logging.info(f"Unprocessed date (posted exact): {posted_text}")
                    return posted_text
    except Exception as e:
        logging.error(f"Error processing date: {posted_text} - {e}")
        return posted_text

    # If no conditions match, log and return the original string
    logging.info(f"Unprocessed date (fallback): {posted_text}")
    return posted_text

# Function to process the CSV file
def process_csv(input_file, output_file):
    df = pd.read_csv(input_file)

    # Process the 'Posted' date to calculate the exact date
    df["Posted"] = df["Posted"].apply(lambda x: process_posted_date(x))

    # Format the date
    df["Posted"] = df["Posted"].apply(
        lambda x: x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x
    )

    df.to_csv(output_file, index=False)
    print(f"{len(output_file)} Processed dates saved to {output_file}")

if __name__ == "__main__":
    input_file = "magicbricks_raw_properties.csv"
    output_file = "magicbricks_properties.csv"
    process_csv(input_file, output_file)
