import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to scrape a table from a given URL
def scrape_table_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', id='Resultlist')

    if table is None:
        print(f"Table with ID 'Resultlist' not found at {url}.")
        return pd.DataFrame()

    # Initialize lists to hold data
    headers = []
    rows = []

    # Extract headers
    header_row = table.find('tr')
    headers = [th.text.strip() for th in header_row.find_all('th')]

    # Extract data rows
    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        columns = [col for col in columns if 'KategorieHeader' not in col.get('class', [])]
        rows.append([col.text.strip() for col in columns])

    # Create a DataFrame
    return pd.DataFrame(rows, columns=headers)

# URL of the main page
main_url = 'https://statistik.d-u-v.org/geteventlist.php'

# Send a GET request to the website
response = requests.get(main_url)
response.raise_for_status()  # Check if the request was successful

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find the main table
main_table = soup.find('table', id='Resultlist')

if main_table is None:
    print("Main table with ID 'Resultlist' not found.")
else:
    # Initialize a DataFrame to hold all data
    all_data = pd.DataFrame()

    # Extract links and scrape each
    for row in main_table.find_all('tr')[1:]:  # Skip header row
        cells = row.find_all('td')
        links = [cell.find('a') for cell in cells if cell.find('a')]

        for link in links:
            href = link.get('href')
            full_url = requests.compat.urljoin(main_url, href)  # Construct the full URL
            print(f"Scraping data from {full_url}")

            # Scrape data from the linked page
            data_df = scrape_table_from_url(full_url)

            # Append to the main DataFrame
            all_data = pd.concat([all_data, data_df], ignore_index=True)

            # Optional: Sleep to avoid too many requests too quickly
            time.sleep(1)  # Sleep for 1 second between requests

    # Save all collected data to a CSV file
    all_data.to_csv('all_scraped_data.csv', index=False)
    print("All data has been successfully scraped and saved to 'all_scraped_data.csv'.")
