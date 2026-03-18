"""
Module: fetch_fao_census.py
Project: ERS Cooper Trade Data Automation
Description: Automates the extraction of country list data from FAO FishBase 
             and the US Census Bureau using headless Selenium browser automation.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import csv
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def fetch_fao_country_data():
    """
    Scrapes country list data from the FAO FishBase website.
    
    Returns:
        list: Extracted country data rows.
    """
    url = 'https://fishbase.mnhn.fr/country/listofcountrycodes.php'
    
    # Configure headless Chrome
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        print(f"[*] Scraping FAO data from: {url}")
        driver.get(url)
        
        # Locate the data table
        tbody = driver.find_element(By.ID, 'dataTable')
        headers = ['Country FAO', 'ISO3']
        data = []

        # Iterate through table rows and extract columns
        for tr in tbody.find_elements(By.XPATH, './/tr'):
            row = [item.text.strip() for item in tr.find_elements(By.XPATH, './/td')]
            if row:
                # Extract Country FAO (index 0) and ISO3 (index 3)
                filtered_row = [row[0], row[3] if len(row) > 3 else 'N/A']
                data.append(filtered_row)

        # Persist to local storage
        output_file = "filtered_FAO.csv"
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(data)

        print(f"[+] Successfully saved: {output_file}")
        return data
        
    except Exception as e:
        print(f"[!] Failed to fetch FAO data: {e}")
        return None
    finally:
        driver.quit()

def fetch_us_census_country_data():
    """
    Scrapes country list data from the US Census Bureau website.
    
    Returns:
        pd.DataFrame: Filtered dataframe containing Country US Census and ISO2.
    """
    url = "https://www.census.gov/programs-surveys/international-programs/about/idb/countries-and-areas.html"
    
    # Configure headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"[*] Scraping US Census data from: {url}")
        driver.get(url)
        
        # Allow time for dynamic content to load
        time.sleep(5)
        
        # Locate the country table rows
        table_rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
        country_data = []

        # Iterate through rows, skipping the header
        for row in table_rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                iso2 = cells[0].text.strip()
                country_census = cells[1].text.strip()
                country_data.append([iso2, country_census])

        # Standardize column names
        df = pd.DataFrame(country_data, columns=["ISO2", "Country US Census"])
        
        # Persist to local storage
        output_file = "filtered_USCensus_Country_List.csv"
        df.to_csv(output_file, index=False)
        
        print(f"[+] Successfully saved: {output_file}")
        return df
        
    except Exception as e:
        print(f"[!] Failed to fetch US Census data: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_fao_country_data()
    fetch_us_census_country_data()
