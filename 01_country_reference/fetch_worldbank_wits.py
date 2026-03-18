"""
Module: fetch_worldbank_wits.py
Project: ERS Cooper Trade Data Automation
Description: Automates the extraction of country list data from the World Bank and WITS APIs.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from config import TIMEOUT

def fetch_worldbank_country_data():
    """
    Fetches country list data from the World Bank API.
    
    Returns:
        pd.DataFrame: Filtered dataframe containing Country WB and ISO3.
    """
    url = "https://api.worldbank.org/v2/country?format=json&per_page=300"
    
    try:
        print(f"[*] Fetching World Bank data from: {url}")
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        
        # Parse JSON response into a dataframe
        data = response.json()
        countries = data[1]
        worldbank_names = pd.DataFrame(countries)
        
        # Standardize column names
        worldbank_names = worldbank_names[['id', 'name']].rename(
            columns={'id': 'ISO3', 'name': 'Country WB'}
        )
        
        # Persist to local storage
        output_file = "Filtered_Worldbank.csv"
        worldbank_names.to_csv(output_file, index=False)
        
        print(f"[+] Successfully saved: {output_file}")
        return worldbank_names
        
    except Exception as e:
        print(f"[!] Failed to fetch World Bank data: {e}")
        return None

def fetch_wits_country_data():
    """
    Fetches country list data from the WITS World Bank API.
    
    Returns:
        pd.DataFrame: Filtered dataframe containing Country WITS and ISO3.
    """
    namespaces = {'wits': 'http://wits.worldbank.org'}
    url = "https://wits.worldbank.org/API/V1/wits/datasource/trn/dataavailability/country/all/year/2000;2001"
    
    try:
        print(f"[*] Fetching WITS data from: {url}")
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        
        # Parse XML response into a dataframe
        root = ET.fromstring(response.content)
        data = []
        for country in root.findall(".//wits:reporter", namespaces):
            iso3_code = country.get("iso3Code") if country.get("iso3Code") is not None else "N/A"
            member_name = country.find("wits:name", namespaces).text if country.find("wits:name", namespaces) is not None else "N/A"
            data.append({"ISO3": iso3_code, "Country WITS": member_name})

        wits_country_list = pd.DataFrame(data)
        wits_country_list = wits_country_list.drop_duplicates()
        
        # Persist to local storage
        output_file = "Filtered_WITs.csv"
        wits_country_list.to_csv(output_file, index=False)
        
        print(f"[+] Successfully saved: {output_file}")
        return wits_country_list
        
    except Exception as e:
        print(f"[!] Failed to fetch WITS data: {e}")
        return None

if __name__ == "__main__":
    fetch_worldbank_country_data()
    fetch_wits_country_data()
