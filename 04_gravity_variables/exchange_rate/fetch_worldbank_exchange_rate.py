"""
Module:      fetch_worldbank_exchange_rate.py
Project:     ERS Cooper Trade Data Automation
Description: Downloads official exchange rate data (PA.NUS.FCRF) from the
             World Bank API for all countries, saves a long-format CSV, and
             also produces a wide-format (pivoted) CSV spanning 1960–2023.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import logging
import os

import pandas as pd
import requests

from config import TIMEOUT

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WB_EXCHANGE_URL = "https://api.worldbank.org/v2/country/all/indicator/PA.NUS.FCRF"
DOWNLOAD_DIR    = os.path.join(os.getcwd(), "exchange_rate_data")


# ---------------------------------------------------------------------------
# Helper: Flatten nested World Bank JSON response
# ---------------------------------------------------------------------------
def _flatten_wb_records(records: list) -> pd.DataFrame:
    """
    Flattens the nested country/indicator fields returned by the World Bank
    JSON API into a tidy DataFrame.

    Args:
        records (list): Raw list of record dicts from the API response.

    Returns:
        pd.DataFrame: Flattened DataFrame with standardised column names.
    """
    df = pd.DataFrame(records)
    df["Country Name"]      = df["country"].apply(lambda x: x["value"] if isinstance(x, dict) else x)
    df["Country Code"]      = df["country"].apply(lambda x: x["id"]    if isinstance(x, dict) else x)
    df["Indicator Name"]    = df["indicator"].apply(lambda x: x["value"] if isinstance(x, dict) else x)
    df["Indicator Code"]    = df["indicator"].apply(lambda x: x["id"]    if isinstance(x, dict) else x)
    df = df[["Country Name", "Country Code", "Indicator Name", "Indicator Code", "date", "value"]]
    df.columns = ["Country Name", "Country Code", "Indicator Name", "Indicator Code", "Year", "Exchange Rate"]
    return df


# ---------------------------------------------------------------------------
# Long-Format Downloader (2000–2023)
# ---------------------------------------------------------------------------
def download_wb_exchange_rates_long(
    download_dir: str = DOWNLOAD_DIR,
    output_file:  str = "world_bank_exchange_rates.csv",
    date_range:   str = "2000:2023",
) -> pd.DataFrame:
    """
    Downloads World Bank official exchange rate data in long format and
    saves it to CSV. Rows with missing exchange rate values are dropped.

    Args:
        download_dir (str): Directory to save the output CSV.
        output_file  (str): Filename for the saved CSV.
        date_range   (str): Year range in 'YYYY:YYYY' format.

    Returns:
        pd.DataFrame: Long-format exchange rate DataFrame,
                      or an empty DataFrame on failure.
    """
    os.makedirs(download_dir, exist_ok=True)
    params = {"format": "json", "date": date_range, "per_page": "5000"}

    try:
        logger.info(f"[*] Fetching World Bank exchange rates ({date_range}) ...")
        response = requests.get(WB_EXCHANGE_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()

        data = response.json()
        if len(data) < 2 or not data[1]:
            logger.warning("[!] No records returned from World Bank API.")
            return pd.DataFrame()

        df = _flatten_wb_records(data[1])
        df = df[["Country Name", "Country Code", "Year", "Exchange Rate"]]
        df.dropna(subset=["Exchange Rate"], inplace=True)

        output_path = os.path.join(download_dir, output_file)
        df.to_csv(output_path, index=False)
        logger.info(f"[+] Long-format exchange rates saved to '{output_path}' ({len(df):,} records).")
        return df

    except requests.RequestException as e:
        logger.error(f"[!] Network error: {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error: {e}")

    return pd.DataFrame()


# ---------------------------------------------------------------------------
# Wide-Format Downloader with Pagination (1960–2023)
# ---------------------------------------------------------------------------
def download_wb_exchange_rates_wide(
    download_dir: str = DOWNLOAD_DIR,
    output_file:  str = "wide_format_exchange_rate_data.csv",
    date_range:   str = "1960:2023",
) -> pd.DataFrame:
    """
    Downloads all pages of World Bank exchange rate data (1960–2023),
    pivots the result to wide format (one column per year), and saves to CSV.

    Args:
        download_dir (str): Directory to save the output CSV.
        output_file  (str): Filename for the saved CSV.
        date_range   (str): Year range in 'YYYY:YYYY' format.

    Returns:
        pd.DataFrame: Wide-format exchange rate DataFrame,
                      or an empty DataFrame on failure.
    """
    os.makedirs(download_dir, exist_ok=True)
    params      = {"format": "json", "date": date_range, "per_page": "5000", "page": 1}
    all_records = []

    try:
        logger.info(f"[*] Fetching paginated World Bank exchange rates ({date_range}) ...")

        while True:
            response = requests.get(WB_EXCHANGE_URL, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()

            if len(data) < 2 or not data[1]:
                logger.warning("[!] Empty page received — stopping pagination.")
                break

            all_records.extend(data[1])
            total_pages = data[0].get("pages", 1)
            logger.info(f"    [>] Page {params['page']} of {total_pages} fetched.")

            if params["page"] < total_pages:
                params["page"] += 1
            else:
                break

        if not all_records:
            logger.warning("[!] No records collected.")
            return pd.DataFrame()

        df = _flatten_wb_records(all_records)

        # Pivot to wide format
        wide_df = df.pivot(
            index=["Country Name", "Country Code", "Indicator Name", "Indicator Code"],
            columns="Year",
            values="Exchange Rate",
        )
        wide_df.reset_index(inplace=True)
        wide_df.columns.name = None

        output_path = os.path.join(download_dir, output_file)
        wide_df.to_csv(output_path, index=False)
        logger.info(f"[+] Wide-format exchange rates saved to '{output_path}' ({len(wide_df):,} countries).")
        return wide_df

    except requests.RequestException as e:
        logger.error(f"[!] Network error: {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error: {e}")

    return pd.DataFrame()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    download_wb_exchange_rates_long()
    download_wb_exchange_rates_wide()
