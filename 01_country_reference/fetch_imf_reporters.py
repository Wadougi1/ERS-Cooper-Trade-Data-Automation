"""
Module: fetch_imf_reporters.py
Project: ERS Cooper Trade Data Automation
Description: Automates the extraction of country list data from the IMF and UN Comtrade APIs.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import requests
import pandas as pd
from config import TIMEOUT

def fetch_imf_country_data():
    """
    Fetches country list data from the IMF API.
    
    Returns:
        pd.DataFrame: Filtered dataframe containing Country IMF and ISO3.
    """
    url = "https://www.imf.org/external/datamapper/api/v1/countries"
    
    try:
        print(f"[*] Fetching IMF data from: {url}")
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        
        # Parse JSON response into a dataframe
        data = response.json()
        countries = data.get('countries', {})
        
        # Extract ISO codes and corresponding labels
        iso_codes = list(countries.keys())
        country_names = [countries[iso]['label'] for iso in iso_codes]
        
        # Standardize column names
        country_df = pd.DataFrame({'ISO3': iso_codes, 'Country IMF': country_names})
        
        # Persist to local storage
        output_file = "Filtered_IMF.csv"
        country_df.to_csv(output_file, index=False)
        
        print(f"[+] Successfully saved: {output_file}")
        return country_df
        
    except Exception as e:
        print(f"[!] Failed to fetch IMF data: {e}")
        return None

def fetch_reporter_country_data():
    """
    Fetches reporter country list data from the UN Comtrade API.
    
    Returns:
        pd.DataFrame: Filtered dataframe containing Country Reporters and ISO3.
    """
    url = "https://comtradeapi.un.org/files/v1/app/reference/Reporters.json"
    
    try:
        print(f"[*] Fetching Reporter data from: {url}")
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        
        # Parse JSON response into a dataframe
        data = response.json()
        reporter_data = data.get('results', [])
        reporter_df = pd.DataFrame(reporter_data)
        
        # Standardize column names
        reporter_df = reporter_df[['reporterCodeIsoAlpha3', 'text']].rename(
            columns={'reporterCodeIsoAlpha3': 'ISO3', 'text': 'Country Reporters'}
        )
        
        # Persist to local storage
        output_file = "Filtered_Reporters.csv"
        reporter_df.to_csv(output_file, index=False)
        
        print(f"[+] Successfully saved: {output_file}")
        return reporter_df
        
    except Exception as e:
        print(f"[!] Failed to fetch Reporter data: {e}")
        return None

if __name__ == "__main__":
    fetch_imf_country_data()
    fetch_reporter_country_data()
