"""
Module: fetch_fas_gats_exports.py
Project: ERS Cooper Trade Data Automation
Description: Automates the extraction of agricultural export data from the FAS GATS API,
             including data release dates and export records.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import requests
import pandas as pd
from config import FAS_API_KEY, TIMEOUT


def fetch_fas_gats_export_release_dates():
    """
    Fetches export data release dates from the FAS GATS API.

    Returns:
        pd.DataFrame: Dataframe containing export data release dates.
    """
    api_url = "https://api.fas.usda.gov/api/gats/census/data/exports/dataReleaseDates"
    params = {"api_key": FAS_API_KEY}

    try:
        print(f"[*] Fetching FAS GATS export release dates from: {api_url}")
        response = requests.get(api_url, params=params, timeout=TIMEOUT)
        response.raise_for_status()

        # Parse JSON response into a dataframe
        data = response.json()
        if not data:
            print("[!] API returned an empty response.")
            return None

        df = pd.DataFrame(data)

        # Persist to local storage
        output_file = "FAS_GATS_Export_DataReleaseDates.csv"
        df.to_csv(output_file, index=False)

        print(f"[+] Successfully saved: {output_file}")
        print(df.head())
        return df

    except Exception as e:
        print(f"[!] Error fetching export release dates: {e}")
        return None


def fetch_fas_gats_export_data():
    """
    Fetches agricultural export records from the FAS GATS API.

    Returns:
        pd.DataFrame: Dataframe containing export data records.
    """
    api_url = "https://api.fas.usda.gov/api/gats/census/imports/"
    params = {"api_key": FAS_API_KEY}

    try:
        print(f"[*] Fetching FAS GATS export data from: {api_url}")
        response = requests.get(api_url, params=params, timeout=TIMEOUT)
        response.raise_for_status()

        # Parse JSON response into a dataframe
        data = response.json()
        if not data:
            print("[!] API returned an empty response.")
            return None

        df = pd.DataFrame(data)

        # Persist to local storage
        output_file = "FAS_GATS_Export_Data.csv"
        df.to_csv(output_file, index=False)

        print(f"[+] Successfully saved: {output_file}")
        print(df.head())
        return df

    except Exception as e:
        print(f"[!] Error fetching export data: {e}")
        return None


if __name__ == "__main__":
    fetch_fas_gats_export_release_dates()
    fetch_fas_gats_export_data()
