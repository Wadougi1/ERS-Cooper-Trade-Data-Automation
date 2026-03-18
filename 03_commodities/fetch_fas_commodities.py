"""
Module:      fetch_fas_commodities.py
Project:     ERS Cooper Trade Data Automation
Description: Automates the extraction of HS6 and HS10 commodity data from
             the USDA FAS GATS API.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import logging

import pandas as pd
import requests

from config import FAS_API_KEY, TIMEOUT

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HS6 Commodity Fetcher
# ---------------------------------------------------------------------------
def fetch_fas_hs6_commodities(api_key: str, save_path: str = "FAS_HS6_data.csv") -> pd.DataFrame:
    """
    Fetches HS6 commodity data from the FAS GATS API and saves it to CSV.

    Args:
        api_key   (str): FAS GATS API key.
        save_path (str): Destination CSV file path.

    Returns:
        pd.DataFrame: DataFrame containing the fetched HS6 commodity records,
                      or an empty DataFrame on failure.
    """
    url    = "https://api.fas.usda.gov/api/gats/HS6Commodities"
    params = {"api_key": api_key}

    try:
        logger.info(f"[*] Fetching FAS HS6 commodity data from {url} ...")
        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()

        df = pd.DataFrame(response.json())
        df.to_csv(save_path, index=False)
        logger.info(f"[+] HS6 data saved to '{save_path}' ({len(df):,} records).")
        return df

    except requests.RequestException as e:
        logger.error(f"[!] Network error while fetching HS6 data: {e}")
    except ValueError as e:
        logger.error(f"[!] JSON parse error for HS6 data: {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error fetching HS6 data: {e}")

    return pd.DataFrame()


# ---------------------------------------------------------------------------
# HS10 Commodity Fetcher
# ---------------------------------------------------------------------------
def fetch_fas_hs10_commodities(api_key: str, save_path: str = "FAS_HS10_data.csv") -> pd.DataFrame:
    """
    Fetches HS10 commodity data from the FAS GATS API and saves it to CSV.

    Args:
        api_key   (str): FAS GATS API key.
        save_path (str): Destination CSV file path.

    Returns:
        pd.DataFrame: DataFrame containing the fetched HS10 commodity records,
                      or an empty DataFrame on failure.
    """
    url    = "https://api.fas.usda.gov/api/gats/commodities"
    params = {"api_key": api_key}

    try:
        logger.info(f"[*] Fetching FAS HS10 commodity data from {url} ...")
        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()

        data = response.json()
        if not data:
            logger.warning("[!] API returned an empty response for HS10 data.")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df.to_csv(save_path, index=False)
        logger.info(f"[+] HS10 data saved to '{save_path}' ({len(df):,} records).")
        return df

    except requests.RequestException as e:
        logger.error(f"[!] Network error while fetching HS10 data: {e}")
    except ValueError as e:
        logger.error(f"[!] JSON parse error for HS10 data: {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error fetching HS10 data: {e}")

    return pd.DataFrame()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    fetch_fas_hs6_commodities(api_key=FAS_API_KEY)
    fetch_fas_hs10_commodities(api_key=FAS_API_KEY)
