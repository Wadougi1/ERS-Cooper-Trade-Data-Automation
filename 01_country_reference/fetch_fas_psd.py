"""
Module: fetch_fas_psd.py
Project: ERS Cooper Trade Data Automation
Description: Automates the extraction of country list data from the FAS and PSD APIs.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import requests
import pandas as pd
from config import FAS_API_KEY, TIMEOUT

def fetch_fas_country_data():
    """
    Fetches country list data from the FAS API.
    
    Returns:
        pd.DataFrame: Filtered dataframe containing Country FAS and ISO3.
    """
    url = "https://api.fas.usda.gov/api/esr/countries"
    params = {"api_key": FAS_API_KEY}

    try:
        print(f"[*] Fetching FAS data from: {url}")
        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        
        # Parse JSON response into a dataframe
        regions_data = response.json()
        fas_names = pd.DataFrame(regions_data)
        
        # Standardize column names
        fas_names = fas_names[['countryName', 'gencCode']].rename(
            columns={'countryName': 'Country FAS', 'gencCode': 'ISO3'}
        )
        
        # Persist to local storage
        output_file = 'Filtered_FAS.csv'
        fas_names.to_csv(output_file, index=False)
        
        print(f"[+] Successfully saved: {output_file}")
        return fas_names
        
    except Exception as e:
        print(f"[!] Failed to fetch FAS data: {e}")
        return None

def fetch_psd_country_data():
    """
    Fetches country list data from the PSD API.
    
    Returns:
        pd.DataFrame: Filtered dataframe containing Country PSD and ISO3.
    """
    url = "https://api.fas.usda.gov/api/psd/countries"
    params = {"api_key": FAS_API_KEY}

    try:
        print(f"[*] Fetching PSD data from: {url}")
        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        
        # Parse JSON response into a dataframe
        regions_data = response.json()
        psd_names = pd.DataFrame(regions_data)
        
        # Standardize column names
        psd_names_filtered = psd_names[['countryName', 'gencCode']].rename(
            columns={'countryName': 'Country PSD', 'gencCode': 'ISO3'}
        )
        
        # Persist to local storage
        output_file = "Filtered_PSD.csv"
        psd_names_filtered.to_csv(output_file, index=False)
        
        print(f"[+] Successfully saved: {output_file}")
        return psd_names_filtered
        
    except Exception as e:
        print(f"[!] Failed to fetch PSD data: {e}")
        return None

if __name__ == "__main__":
    fetch_fas_country_data()
    fetch_psd_country_data()
