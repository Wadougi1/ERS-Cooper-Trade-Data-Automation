"""
Module: fetch_un_comtrade.py
Project: ERS Cooper Trade Data Automation
Description: Automates the extraction of country list data from the UN Comtrade M49 overview.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import requests
import pandas as pd
from config import TIMEOUT

def fetch_un_comtrade_country_data():
    """
    Fetches and parses the UN M49 country/area overview table.
    
    Returns:
        pd.DataFrame: Filtered dataframe containing Country UN, ISO3, and ISO2.
    """
    url = "https://unstats.un.org/unsd/methodology/m49/overview"
    
    try:
        print(f"[*] Fetching UN Comtrade data from: {url}")
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        
        # Parse HTML tables from the response content
        dfs = pd.read_html(response.content)
        un_comtrade_df = dfs[0]

        # Standardize column names for the harmonization engine
        un_comtrade_df.rename(columns={
            "ISO-alpha3 Code": "ISO3",
            "ISO-alpha2 Code": "ISO2",
            "Country or Area": "Country UN"
        }, inplace=True)

        # Validate required columns exist
        required_cols = {"Country UN", "ISO3", "ISO2"}
        if required_cols.issubset(un_comtrade_df.columns):
            filtered_data = un_comtrade_df[["Country UN", "ISO3", "ISO2"]]
            
            # Persist to local storage
            output_file = "Filtered_UN_Comtrade.csv"
            filtered_data.to_csv(output_file, index=False)
            
            print(f"[+] Successfully saved: {output_file}")
            return filtered_data
        else:
            print("[!] Error: Required columns missing from UN Comtrade dataset.")
            return None
            
    except Exception as e:
        print(f"[!] Failed to fetch UN Comtrade data: {e}")
        return None

if __name__ == "__main__":
    fetch_un_comtrade_country_data()
