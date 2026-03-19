"""
Module:      fetch_cepii_distance.py
Project:     ERS Cooper Trade Data Automation
Description: Downloads and converts CEPII geographic and pairwise distance
             datasets from the CEPII Distance Database (GeoDist) page.
             Two datasets are retrieved:
               1. geo_cepii.xls  — Country-level geographic attributes
                                   (coordinates, landlocked status, etc.)
               2. dist_cepii.zip — Dyadic (pairwise) bilateral distance
                                   and geographic variables between all
                                   country pairs.
             Both XLS files are converted to XLSX format after download.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import logging
import os
import zipfile
from io import BytesIO

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CEPII_PAGE_URL = "https://www.cepii.fr/cepii/en/bdd_modele/bdd_modele_item.asp?id=6"
GEO_FILE_SUFFIX = "geo_cepii.xls"
DIST_FILE_SUFFIX = "dist_cepii.zip"
DIST_EXTRACT_DIR = os.path.join(os.getcwd(), "dist_cepii_data")


# ---------------------------------------------------------------------------
# Helper: Scrape CEPII page and return a download URL by file suffix
# ---------------------------------------------------------------------------
def _get_cepii_download_url(suffix: str) -> str | None:
    """
    Scrapes the CEPII GeoDist page and returns the href of the first
    anchor tag whose href ends with the given suffix.

    Args:
        suffix (str): File suffix to search for (e.g. 'geo_cepii.xls').

    Returns:
        str | None: Absolute or relative URL of the matching file,
                    or None if not found.
    """
    logger.info(f"[*] Scraping CEPII page for '{suffix}' ...")
    response = requests.get(CEPII_PAGE_URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    tag  = soup.find(
        "a",
        class_="titre-actu",
        href=lambda x: x and x.endswith(suffix),
    )

    if tag:
        url = tag["href"]
        logger.info(f"[+] Found URL: {url}")
        return url

    logger.warning(f"[!] No link ending with '{suffix}' found on CEPII page.")
    return None


# ---------------------------------------------------------------------------
# Helper: Convert an XLS file to XLSX in-place
# ---------------------------------------------------------------------------
def _xls_to_xlsx(xls_path: str) -> str:
    """
    Reads an XLS file using the xlrd engine and saves it as an XLSX file
    in the same directory.

    Args:
        xls_path (str): Full path to the source .xls file.

    Returns:
        str: Full path to the newly created .xlsx file.
    """
    xlsx_path = xls_path.replace(".xls", ".xlsx")
    logger.info(f"[*] Converting '{os.path.basename(xls_path)}' to XLSX ...")
    df = pd.read_excel(xls_path, engine="xlrd")
    df.to_excel(xlsx_path, index=False)
    logger.info(f"[+] Saved as: '{xlsx_path}'")
    return xlsx_path


# ---------------------------------------------------------------------------
# Public API: Download country-level geographic data (geo_cepii)
# ---------------------------------------------------------------------------
def download_geo_cepii(output_dir: str = os.getcwd()) -> str | None:
    """
    Downloads the CEPII country-level geographic attributes file
    (geo_cepii.xls) and converts it to XLSX format.

    The file contains country-level variables such as geographic
    coordinates, landlocked status, island status, and continent.

    Args:
        output_dir (str): Directory where the downloaded and converted
                          files will be saved. Defaults to the current
                          working directory.

    Returns:
        str | None: Path to the converted .xlsx file on success,
                    or None on failure.
    """
    url = _get_cepii_download_url(GEO_FILE_SUFFIX)
    if not url:
        return None

    file_name = os.path.basename(url)
    xls_path  = os.path.join(output_dir, file_name)

    try:
        logger.info(f"[*] Downloading '{file_name}' ...")
        r = requests.get(url, timeout=60)
        r.raise_for_status()

        os.makedirs(output_dir, exist_ok=True)
        with open(xls_path, "wb") as f:
            f.write(r.content)
        logger.info(f"[+] Downloaded: '{xls_path}'")

        return _xls_to_xlsx(xls_path)

    except Exception as e:
        logger.error(f"[!] Failed to download geo_cepii: {e}")
        return None


# ---------------------------------------------------------------------------
# Public API: Download pairwise dyadic distance data (dist_cepii)
# ---------------------------------------------------------------------------
def download_dist_cepii(extract_dir: str = DIST_EXTRACT_DIR) -> list[str]:
    """
    Downloads the CEPII dyadic bilateral distance ZIP archive
    (dist_cepii.zip), extracts its contents, and converts any
    enclosed XLS files to XLSX format.

    The dataset contains pairwise bilateral variables between all
    country pairs, including simple and weighted distances, contiguity,
    common language, colonial links, and more.

    Args:
        extract_dir (str): Directory where the ZIP contents will be
                           extracted. Defaults to 'dist_cepii_data/'
                           in the current working directory.

    Returns:
        list[str]: Paths to all converted .xlsx files on success,
                   or an empty list on failure.
    """
    url = _get_cepii_download_url(DIST_FILE_SUFFIX)
    if not url:
        return []

    try:
        logger.info(f"[*] Downloading dist_cepii.zip ...")
        r = requests.get(url, timeout=120)
        r.raise_for_status()

        os.makedirs(extract_dir, exist_ok=True)
        zip_bytes = BytesIO(r.content)

        with zipfile.ZipFile(zip_bytes) as zf:
            zf.extractall(extract_dir)
            names = zf.namelist()
        logger.info(f"[+] ZIP extracted to '{extract_dir}'")

        # Convert any XLS files found in the archive
        xlsx_files = []
        for fname in names:
            if fname.endswith(".xls"):
                xls_path = os.path.join(extract_dir, fname)
                xlsx_path = _xls_to_xlsx(xls_path)
                xlsx_files.append(xlsx_path)

        return xlsx_files

    except Exception as e:
        logger.error(f"[!] Failed to download dist_cepii: {e}")
        return []


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    tasks = [
        ("Country-level geographic data (geo_cepii)", download_geo_cepii),
        ("Pairwise dyadic distance data (dist_cepii)", download_dist_cepii),
    ]

    for label, func in tasks:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"[>] {label}")
        logger.info(f"{'=' * 60}")
        try:
            result = func()
            if result:
                logger.info(f"[+] Completed: {label}")
            else:
                logger.warning(f"[!] No output returned for: {label}")
        except Exception as e:
            logger.error(f"[!] Error in '{label}': {e}")
