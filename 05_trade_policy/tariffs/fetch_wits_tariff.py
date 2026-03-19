"""
Module:      fetch_wits_tariff.py
Project:     ERS Cooper Trade Data Automation
Description: Automates the login and download of MFN (Most Favoured Nation)
             and Preferential (PRF) tariff datasets from the World Integrated
             Trade Solution (WITS) portal using Selenium WebDriver.
             Downloaded ZIP archives are recursively extracted until all
             nested ZIPs are fully unpacked, and resulting CSV files are
             listed for confirmation.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import glob
import logging
import os
import time
import zipfile

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from config import TIMEOUT

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WITS_LOGIN_URL    = "https://wits.worldbank.org/WITS/WITS/Restricted/Login.aspx"
WITS_DOWNLOAD_URL = (
    "https://wits.worldbank.org/WITS/WITS/Results/Queryview/"
    "QueryView.aspx?Page=DownloadandViewResults&Download=true"
)

# WITS query IDs for each tariff type
QUERY_ID_MFN = "2805730"
QUERY_ID_PRF = "2811793"

MFN_DOWNLOAD_DIR = os.path.join(os.getcwd(), "MFNdownloads")
PRF_DOWNLOAD_DIR = os.path.join(os.getcwd(), "PRFdownloads")


# ---------------------------------------------------------------------------
# Helper: Build headless Chrome driver with download preferences
# ---------------------------------------------------------------------------
def _build_driver(download_dir: str) -> webdriver.Chrome:
    """
    Builds and returns a headless Chrome WebDriver configured for
    silent file downloads.

    Args:
        download_dir (str): Directory where downloaded files will be saved.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance.
    """
    os.makedirs(download_dir, exist_ok=True)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("prefs", {
        "download.default_directory":   download_dir,
        "download.prompt_for_download": False,
        "safebrowsing.enabled":         True,
    })
    return webdriver.Chrome(options=options)


# ---------------------------------------------------------------------------
# Helper: Poll directory until a .zip file appears
# ---------------------------------------------------------------------------
def _wait_for_zip(directory: str, timeout: int = 300) -> str | None:
    """
    Polls the given directory until a .zip file appears or the timeout
    is reached.

    Args:
        directory (str): Directory to monitor for ZIP files.
        timeout   (int): Maximum seconds to wait.

    Returns:
        str | None: Full path to the first .zip file found, or None on timeout.
    """
    start = time.time()
    while time.time() - start < timeout:
        zips = [f for f in os.listdir(directory) if f.endswith(".zip")]
        if zips:
            zip_path = os.path.join(directory, zips[0])
            logger.info(f"[+] ZIP file detected: '{zip_path}'")
            return zip_path
        logger.info("[~] Waiting for ZIP download to complete ...")
        time.sleep(5)
    logger.warning(f"[!] Timed out waiting for ZIP in '{directory}'.")
    return None


# ---------------------------------------------------------------------------
# Helper: Recursively extract all nested ZIP files
# ---------------------------------------------------------------------------
def _extract_all_zips(root_dir: str) -> None:
    """
    Recursively extracts all .zip files found under `root_dir` until no
    ZIP files remain. Each ZIP is extracted in-place and then deleted.

    Args:
        root_dir (str): Root directory to scan for ZIP files.
    """
    extracted_any = True
    while extracted_any:
        extracted_any = False
        for zip_path in glob.glob(os.path.join(root_dir, "**", "*.zip"), recursive=True):
            folder = os.path.dirname(zip_path)
            try:
                logger.info(f"[*] Extracting: '{zip_path}' ...")
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(folder)
                os.remove(zip_path)
                extracted_any = True
            except Exception as e:
                logger.error(f"[!] Failed to extract '{zip_path}': {e}")


# ---------------------------------------------------------------------------
# Helper: Log all CSV files found after extraction
# ---------------------------------------------------------------------------
def _report_csv_files(root_dir: str) -> list[str]:
    """
    Scans `root_dir` recursively for CSV files and logs each one found.

    Args:
        root_dir (str): Root directory to scan.

    Returns:
        list[str]: List of absolute paths to all CSV files found.
    """
    csv_files = glob.glob(os.path.join(root_dir, "**", "*.csv"), recursive=True)
    if csv_files:
        logger.info(f"[+] {len(csv_files)} CSV file(s) found after extraction:")
        for f in csv_files:
            logger.info(f"    - {f}")
    else:
        logger.warning("[!] No CSV files found after extraction.")
    return csv_files


# ---------------------------------------------------------------------------
# Core: WITS Login, Download, and Extract
# ---------------------------------------------------------------------------
def _run_wits_download(
    query_id:     str,
    download_dir: str,
    label:        str,
    username:     str,
    password:     str,
) -> list[str]:
    """
    Orchestrates the full WITS download workflow for a given query ID:
      1. Logs in to the WITS portal.
      2. Navigates to the download results page.
      3. Clicks the download button for the specified query.
      4. Waits for the ZIP file to arrive.
      5. Recursively extracts all nested ZIPs.
      6. Reports extracted CSV files.

    Args:
        query_id     (str): WITS query ID embedded in the download button onclick.
        download_dir (str): Directory to save and extract downloaded files.
        label        (str): Human-readable label for logging (e.g. 'MFN', 'PRF').
        username     (str): WITS portal login username.
        password     (str): WITS portal login password.

    Returns:
        list[str]: Paths to all extracted CSV files, or an empty list on failure.
    """
    driver = _build_driver(download_dir)

    try:
        # Step 1: Login
        logger.info(f"[*] [{label}] Logging in to WITS portal ...")
        driver.get(WITS_LOGIN_URL)
        time.sleep(10)
        driver.find_element(By.XPATH, '//*[@id="UserNameTextBox"]').send_keys(username)
        driver.find_element(By.XPATH, '//*[@id="UserPassTextBox"]').send_keys(password)
        driver.find_element(By.XPATH, '//*[@id="btnSubmit"]').click()

        # Step 2: Navigate to download page
        logger.info(f"[*] [{label}] Navigating to download results page ...")
        driver.get(WITS_DOWNLOAD_URL)
        time.sleep(5)

        # Step 3: Click the query-specific download button
        logger.info(f"[*] [{label}] Clicking download button (query ID: {query_id}) ...")
        download_btn = driver.find_element(
            By.XPATH, f'//td[contains(@onclick, "{query_id}")]',
        )
        download_btn.click()

        # Step 4: Wait for ZIP
        logger.info(f"[*] [{label}] Waiting for ZIP file to download ...")
        zip_path = _wait_for_zip(download_dir, timeout=TIMEOUT)
        if not zip_path:
            logger.error(f"[!] [{label}] No ZIP file found — aborting.")
            return []

        # Step 5: Recursive extraction
        logger.info(f"[*] [{label}] Extracting all nested ZIP files ...")
        _extract_all_zips(download_dir)

        # Step 6: Report CSVs
        return _report_csv_files(download_dir)

    except Exception as e:
        logger.error(f"[!] [{label}] Unexpected error: {e}")
        return []
    finally:
        driver.quit()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def download_mfn_tariff(
    username:     str,
    password:     str,
    download_dir: str = MFN_DOWNLOAD_DIR,
) -> list[str]:
    """
    Downloads and extracts the MFN (Most Favoured Nation) tariff dataset
    from the WITS portal.

    Args:
        username     (str): WITS portal login username.
        password     (str): WITS portal login password.
        download_dir (str): Directory to save and extract downloaded files.

    Returns:
        list[str]: Paths to all extracted CSV files.
    """
    return _run_wits_download(
        query_id=QUERY_ID_MFN,
        download_dir=download_dir,
        label="MFN",
        username=username,
        password=password,
    )


def download_preferential_tariff(
    username:     str,
    password:     str,
    download_dir: str = PRF_DOWNLOAD_DIR,
) -> list[str]:
    """
    Downloads and extracts the Preferential (PRF) tariff dataset from
    the WITS portal.

    Args:
        username     (str): WITS portal login username.
        password     (str): WITS portal login password.
        download_dir (str): Directory to save and extract downloaded files.

    Returns:
        list[str]: Paths to all extracted CSV files.
    """
    return _run_wits_download(
        query_id=QUERY_ID_PRF,
        download_dir=download_dir,
        label="PRF",
        username=username,
        password=password,
    )


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os

    # Credentials are read from environment variables for security.
    # Set WITS_USERNAME and WITS_PASSWORD before running.
    wits_user = os.environ.get("WITS_USERNAME", "")
    wits_pass = os.environ.get("WITS_PASSWORD", "")

    if not wits_user or not wits_pass:
        logger.error(
            "[!] WITS credentials not set. "
            "Export WITS_USERNAME and WITS_PASSWORD as environment variables."
        )
    else:
        download_mfn_tariff(username=wits_user, password=wits_pass)
        download_preferential_tariff(username=wits_user, password=wits_pass)
