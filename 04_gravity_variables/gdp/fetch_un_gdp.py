"""
Module:      fetch_un_gdp.py
Project:     ERS Cooper Trade Data Automation
Description: Downloads the UN National Accounts GDP dataset for all countries
             directly from the UN Statistics Division API.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import logging
import os

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
UN_GDP_URL   = "https://unstats.un.org/unsd/amaapi/api/file/9"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "un_gdp_downloads")
OUTPUT_FILE  = "UN_GDP_All_Countries.xlsx"


# ---------------------------------------------------------------------------
# UN GDP Downloader
# ---------------------------------------------------------------------------
def download_un_gdp(
    download_dir: str = DOWNLOAD_DIR,
    output_file:  str = OUTPUT_FILE,
) -> str | None:
    """
    Downloads the UN SNA GDP dataset (all countries) as an Excel file
    from the UN Statistics Division API.

    Args:
        download_dir (str): Directory to save the downloaded file.
        output_file  (str): Filename for the saved Excel file.

    Returns:
        str | None: Full path to the saved file on success, None on failure.
    """
    os.makedirs(download_dir, exist_ok=True)
    output_path = os.path.join(download_dir, output_file)

    try:
        logger.info("[*] Downloading UN GDP dataset from UN SNA API ...")
        response = requests.get(UN_GDP_URL, timeout=TIMEOUT)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.info(f"[+] UN GDP data saved to '{output_path}'.")
        return output_path

    except requests.RequestException as e:
        logger.error(f"[!] Network error downloading UN GDP data: {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error: {e}")

    return None


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    download_un_gdp()
