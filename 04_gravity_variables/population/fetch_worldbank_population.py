"""
Module:      fetch_worldbank_population.py
Project:     ERS Cooper Trade Data Automation
Description: Automates the download of World Bank total population data
             (SP.POP.TOTL) from the World Bank Data360 portal using
             Selenium WebDriver. The file is downloaded in SDMX CSV format
             to a local directory for further processing.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import logging
import os
import time

from selenium import webdriver
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
WB_POPULATION_URL = "https://data360.worldbank.org/en/indicator/WB_WDI_SP_POP_TOTL"
DOWNLOAD_DIR      = os.path.join(os.getcwd(), "worldbank_population_downloads")


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
    options = webdriver.ChromeOptions()
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
# Main Downloader
# ---------------------------------------------------------------------------
def download_worldbank_population(download_dir: str = DOWNLOAD_DIR) -> None:
    """
    Navigates to the World Bank Data360 population indicator page and
    downloads the dataset in SDMX CSV format.

    The downloaded file is saved to `download_dir`. No further
    transformation is applied — the raw SDMX CSV is preserved for
    downstream processing.

    Args:
        download_dir (str): Directory to save the downloaded file.
    """
    driver = _build_driver(download_dir)
    wait   = WebDriverWait(driver, 30)

    try:
        logger.info("[*] Navigating to World Bank Data360 population dataset ...")
        driver.get(WB_POPULATION_URL)
        time.sleep(10)

        # Open the Data download dropdown
        logger.info("[*] Opening the download dropdown ...")
        download_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(@class,'dropdown-toggle') and .//span[text()='Data']]",
        )))
        download_btn.click()
        time.sleep(2)

        # Select SDMX CSV from the dropdown menu
        logger.info("[*] Selecting 'SDMX CSV' download option ...")
        sdmx_option = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//span[text()='SDMX CSV']",
        )))
        sdmx_option.click()

        logger.info("[*] Download triggered — waiting for file to arrive ...")
        time.sleep(20)
        logger.info(f"[+] World Bank population data saved to '{download_dir}'.")

    except Exception as e:
        logger.error(f"[!] Error during World Bank population download: {e}")
    finally:
        driver.quit()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    download_worldbank_population()
