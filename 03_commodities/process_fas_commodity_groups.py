"""
Module:      process_fas_commodity_groups.py
Project:     ERS Cooper Trade Data Automation
Description: Processes raw FAS BICO-HS10 commodity export files and separates
             them into distinct HS6 and HS10 reference datasets based on
             commodity code length.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import logging
import os

import pandas as pd

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_INPUT  = "ProductGroup-BICO-HS10.csv"
DEFAULT_HS6    = "fas_processed_hs6.csv"
DEFAULT_HS10   = "fas_processed_hs10.csv"


# ---------------------------------------------------------------------------
# Commodity Splitter
# ---------------------------------------------------------------------------
def split_fas_bico_data(
    input_csv:  str = DEFAULT_INPUT,
    hs6_output: str = DEFAULT_HS6,
    hs10_output: str = DEFAULT_HS10,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Reads a FAS ProductGroup CSV and splits records into HS6 and HS10 files
    based on the length of the commodity code.

    Codes with exactly 10 characters are classified as HS10.
    Codes with 8 or fewer characters are classified as HS6.

    Args:
        input_csv   (str): Path to the raw FAS BICO-HS10 CSV file.
        hs6_output  (str): Destination path for the HS6 output CSV.
        hs10_output (str): Destination path for the HS10 output CSV.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: A tuple of (hs6_df, hs10_df),
        both empty DataFrames on failure.
    """
    if not os.path.exists(input_csv):
        logger.error(f"[!] Input file not found: '{input_csv}'")
        return pd.DataFrame(), pd.DataFrame()

    try:
        logger.info(f"[*] Reading commodity file: '{input_csv}' ...")

        # The first row is metadata; the second row contains column headers
        df = pd.read_csv(input_csv, skiprows=1, dtype=str)

        if "Code" not in df.columns:
            logger.error("[!] Required column 'Code' is missing from the dataset.")
            return pd.DataFrame(), pd.DataFrame()

        # Normalise codes
        df["Code"] = df["Code"].str.strip()

        # Split by code length
        hs10_df = df[df["Code"].str.len() == 10].copy()
        hs6_df  = df[df["Code"].str.len() <= 8].copy()

        # Persist results
        hs6_df.to_csv(hs6_output,   index=False)
        hs10_df.to_csv(hs10_output, index=False)

        logger.info(
            f"[+] Split complete — "
            f"{len(hs6_df):,} HS6 records saved to '{hs6_output}', "
            f"{len(hs10_df):,} HS10 records saved to '{hs10_output}'."
        )
        return hs6_df, hs10_df

    except FileNotFoundError as e:
        logger.error(f"[!] File error: {e}")
    except KeyError as e:
        logger.error(f"[!] Column key error: {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error during commodity split: {e}")

    return pd.DataFrame(), pd.DataFrame()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    split_fas_bico_data()
