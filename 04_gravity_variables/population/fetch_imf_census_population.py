"""
Module:      fetch_imf_census_population.py
Project:     ERS Cooper Trade Data Automation
Description: Automates the download of population data from two sources:
               1. IMF World Economic Outlook DataMapper (LP indicator) —
                  downloads an Excel file and converts it to a clean .xlsx.
               2. U.S. Census Bureau International Data Base (IDB) —
                  downloads a custom-filtered CSV covering 1950–2025.
             Both routines use Selenium WebDriver in headless mode.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import glob
import logging
import os
import time

import pandas as pd
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
IMF_POPULATION_URL = (
    "https://www.imf.org/external/datamapper/LP@WEO/OEMDC/ADVEC/WEOWORLD"
)
IMF_DOWNLOAD_DIR   = os.path.join(os.getcwd(), "imf_population_downloads")

CENSUS_YEARS       = list(range(1950, 2026))
CENSUS_YEARS_STR   = ",".join(str(y) for y in CENSUS_YEARS)
CENSUS_URL         = (
    "https://www.census.gov/data-tools/demo/idb/#/table?"
    "dashboard_page=country&COUNTRY_YR_ANIM=2025&menu=tableViz&quickReports=CUSTOM"
    f"&CUSTOM_COLS=POP&TABLE_RANGE=1950,2024&TABLE_YEARS={CENSUS_YEARS_STR}"
    "&TABLE_USE_RANGE=Y&TABLE_USE_YEARS=Y&TABLE_STEP=1&TABLE_ADD_YEARS=2025"
)
CENSUS_DOWNLOAD_DIR = os.path.join(os.getcwd(), "us_census_population_downloads")


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
# IMF Population Downloader
# ---------------------------------------------------------------------------
def download_imf_population(download_dir: str = IMF_DOWNLOAD_DIR) -> str | None:
    """
    Downloads IMF WEO population data (LP indicator) from the IMF DataMapper
    portal as an Excel file, then converts it to a clean .xlsx file.

    The function:
      - Clicks the 'Download all data as Excel' button on the IMF DataMapper.
      - Reads the downloaded .xls file as an HTML table (IMF format).
      - Identifies the population table by column names.
      - Saves a cleaned version as 'IMF_Population_Cleaned.xlsx'.

    Args:
        download_dir (str): Directory to save the downloaded and converted files.

    Returns:
        str | None: Path to the cleaned .xlsx file on success, None on failure.
    """
    driver = _build_driver(download_dir)
    wait   = WebDriverWait(driver, 60)

    try:
        logger.info("[*] Navigating to IMF DataMapper population dashboard ...")
        driver.get(IMF_POPULATION_URL)
        time.sleep(15)

        # Click the Excel download button
        logger.info("[*] Clicking the Excel download button ...")
        download_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[@class='dm-share-button' and @data-type='excel' and @data-what='all']",
        )))
        download_btn.click()
        logger.info("[*] Download triggered — waiting for file to arrive ...")
        time.sleep(30)

        # Locate the most recently downloaded .xls file
        xls_files = sorted(
            glob.glob(os.path.join(download_dir, "*.xls")),
            key=os.path.getmtime,
            reverse=True,
        )
        if not xls_files:
            raise FileNotFoundError("No .xls file found after download.")

        downloaded_file = xls_files[0]
        xlsx_output     = os.path.join(download_dir, "IMF_Population_Cleaned.xlsx")

        # Parse the .xls file (IMF exports as HTML-wrapped XLS)
        logger.info(f"[*] Parsing '{downloaded_file}' as HTML table ...")
        tables = pd.read_html(downloaded_file)
        if not tables:
            raise ValueError("No tables found in the downloaded file.")

        # Identify the population table by column content
        population_df = None
        for table in tables:
            if any("Country" in str(col) or "LP" in str(col) for col in table.columns):
                population_df = table
                break

        if population_df is None:
            raise ValueError("No valid population table found in the file.")

        # Clean column headers and drop fully empty rows
        population_df.columns = (
            population_df.columns.astype(str).str.strip().str.replace("\n", " ")
        )
        population_df.dropna(how="all", inplace=True)
        if population_df.iloc[0].isnull().sum() > 5:
            population_df = population_df.iloc[1:].reset_index(drop=True)

        population_df.to_excel(xlsx_output, index=False)
        logger.info(f"[+] IMF population data saved to '{xlsx_output}' ({len(population_df):,} rows).")
        return xlsx_output

    except FileNotFoundError as e:
        logger.error(f"[!] File error: {e}")
    except ValueError as e:
        logger.error(f"[!] Parsing error: {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error: {e}")
    finally:
        driver.quit()

    return None


# ---------------------------------------------------------------------------
# U.S. Census Bureau Population Downloader
# ---------------------------------------------------------------------------
def download_census_population(download_dir: str = CENSUS_DOWNLOAD_DIR) -> str | None:
    """
    Downloads custom-filtered population data from the U.S. Census Bureau
    International Data Base (IDB) covering years 1950–2025 in CSV format.

    The function:
      - Navigates to the pre-filtered IDB table URL.
      - Clicks the download icon and selects the CSV option.
      - Waits for the file to appear in the download directory.

    Args:
        download_dir (str): Directory to save the downloaded CSV file.

    Returns:
        str | None: Path to the downloaded CSV file on success, None on failure.
    """
    driver = _build_driver(download_dir)
    wait   = WebDriverWait(driver, 60)

    try:
        logger.info("[*] Navigating to U.S. Census Bureau IDB population table ...")
        driver.get(CENSUS_URL)
        time.sleep(15)

        # Click the download icon
        logger.info("[*] Clicking the download icon ...")
        download_icon = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//mat-icon[@aria-label='Download current data set, with filters in effect.']",
        )))
        download_icon.click()

        # Select CSV format from the popup
        logger.info("[*] Selecting CSV format ...")
        csv_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//span[contains(text(),'CSV')]",
        )))
        csv_btn.click()

        # Poll for the downloaded file
        logger.info("[*] Waiting for CSV file to download ...")
        downloaded_file = None
        for _ in range(30):
            files = glob.glob(os.path.join(download_dir, "*.csv"))
            if files:
                downloaded_file = max(files, key=os.path.getctime)
                break
            time.sleep(1)

        if downloaded_file:
            logger.info(f"[+] Census population data saved to '{downloaded_file}'.")
            return downloaded_file
        else:
            logger.warning("[!] Download timed out — no CSV file found.")

    except Exception as e:
        logger.error(f"[!] Error during Census population download: {e}")
    finally:
        driver.quit()

    return None


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    download_imf_population()
    download_census_population()
