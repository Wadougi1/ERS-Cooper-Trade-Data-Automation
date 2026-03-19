"""
Module:      fetch_worldbank_gdp.py
Project:     ERS Cooper Trade Data Automation
Description: Downloads GDP data (NY.GDP.MKTP.CD) from the World Bank API,
             extracts the ZIP archive, and saves the contents locally.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import io
import logging
import os
import zipfile

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
WB_GDP_URL   = (
    "https://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.CD"
    "?downloadformat=csv"
)
DOWNLOAD_DIR = os.path.join(os.getcwd(), "world_bank_gdp_data")


# ---------------------------------------------------------------------------
# World Bank GDP Downloader
# ---------------------------------------------------------------------------
def download_worldbank_gdp(download_dir: str = DOWNLOAD_DIR) -> str | None:
    """
    Downloads the World Bank GDP indicator dataset as a ZIP archive and
    extracts all files into the specified directory.

    Args:
        download_dir (str): Local directory to extract the GDP data into.

    Returns:
        str | None: Path to the extraction directory on success, None on failure.
    """
    os.makedirs(download_dir, exist_ok=True)

    try:
        logger.info("[*] Downloading World Bank GDP ZIP archive ...")
        response = requests.get(WB_GDP_URL, timeout=TIMEOUT)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(download_dir)

        logger.info(f"[+] GDP data extracted to '{download_dir}'.")
        return download_dir

    except requests.RequestException as e:
        logger.error(f"[!] Network error downloading World Bank GDP data: {e}")
    except zipfile.BadZipFile as e:
        logger.error(f"[!] Invalid ZIP file received: {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error: {e}")

    return None


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    download_worldbank_gdp()
