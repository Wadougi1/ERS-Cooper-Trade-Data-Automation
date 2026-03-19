"""
Module:      fetch_worldbank_tariff.py
Project:     ERS Cooper Trade Data Automation
Description: Automates the download of tariff data from the World Bank
             DataBank portal using Selenium WebDriver. Navigates to the
             pre-configured Tariffs report, opens the download menu, and
             triggers a CSV download. The resulting ZIP archive is then
             extracted to a local directory.
             Note: A configurable pause is built in before the CSV download
             is triggered to allow manual filter adjustments if needed.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import logging
import os
import time
import zipfile

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WB_TARIFF_URL = "https://databank.worldbank.org/id/71125ba8?Report_Name=Tarrifs"
DOWNLOAD_DIR  = os.path.join(os.getcwd(), "worldbank_downloads")

# Seconds to pause before triggering the CSV download.
# Increase this value if manual filter adjustments are needed.
PRE_DOWNLOAD_PAUSE = 120


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
# Main Downloader
# ---------------------------------------------------------------------------
def download_worldbank_tariff(
    download_dir:       str = DOWNLOAD_DIR,
    pre_download_pause: int = PRE_DOWNLOAD_PAUSE,
) -> str | None:
    """
    Navigates to the World Bank DataBank Tariffs report, opens the download
    menu, waits for a configurable pause (to allow manual filter adjustments),
    triggers a CSV download, and extracts the resulting ZIP archive.

    Args:
        download_dir       (str): Directory to save and extract downloaded files.
        pre_download_pause (int): Seconds to wait before clicking the CSV
                                  download button. Set to 0 for fully automated
                                  runs with no manual interaction.

    Returns:
        str | None: Path to the extracted directory on success, None on failure.
    """
    driver = _build_driver(download_dir)
    wait   = WebDriverWait(driver, 15)

    try:
        logger.info("[*] Navigating to World Bank DataBank Tariffs report ...")
        driver.get(WB_TARIFF_URL)

        # Wait for the download menu button to be available
        logger.info("[*] Waiting for the download menu to become available ...")
        try:
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "download")))
        except Exception:
            logger.error("[!] Download button not found — aborting.")
            return None

        # Open the download dropdown
        logger.info("[*] Opening the download dropdown ...")
        driver.find_element(By.CLASS_NAME, "download").click()
        time.sleep(2)

        # Optional pause for manual filter adjustments
        if pre_download_pause > 0:
            logger.info(
                f"[~] Pausing {pre_download_pause}s for manual filter adjustments ..."
            )
            time.sleep(pre_download_pause)

        # Click the CSV download option
        logger.info("[*] Clicking the CSV download button ...")
        try:
            csv_btn = driver.find_element(By.XPATH, "//li[@id='liCSVDownload']/a")
            csv_btn.click()
        except Exception:
            logger.error("[!] CSV download button not found — aborting.")
            return None

        logger.info("[*] CSV download initiated — waiting for ZIP file ...")
        time.sleep(20)

        # Wait for ZIP to appear
        zip_path = _wait_for_zip(download_dir)
        if not zip_path:
            logger.error("[!] No ZIP file found — aborting.")
            return None

        # Extract ZIP
        extracted_dir = os.path.join(download_dir, "extracted")
        os.makedirs(extracted_dir, exist_ok=True)

        logger.info(f"[*] Extracting '{zip_path}' to '{extracted_dir}' ...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extracted_dir)

        logger.info(f"[+] World Bank tariff data extracted to '{extracted_dir}'.")
        return extracted_dir

    except Exception as e:
        logger.error(f"[!] Unexpected error: {e}")
        return None
    finally:
        driver.quit()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    download_worldbank_tariff()
