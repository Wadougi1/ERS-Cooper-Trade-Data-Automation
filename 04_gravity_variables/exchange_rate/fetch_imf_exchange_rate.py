"""
Module:      fetch_imf_exchange_rate.py
Project:     ERS Cooper Trade Data Automation
Description: Automates the extraction of IMF exchange rate data from the
             IMF Data Explorer using Selenium WebDriver. Supports both
             Annual-only and All-Frequencies download modes. Downloaded
             CSV files are automatically converted to Excel (.xlsx).
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
IMF_ER_URL       = "https://data.imf.org/en/Data-Explorer?datasetUrn=IMF.STA:ER(4.0.1)"
ANNUAL_DIR       = os.path.join(os.getcwd(), "imf_exchange_downloads_Annual")
ALL_FREQ_DIR     = os.path.join(os.getcwd(), "imf_exchange_downloads_AllFrequencies")

# IMF filter configuration
COMMON_FILTERS = [
    ("Country",                  "All"),
    ("Indicator",                "US Dollar per domestic currency"),
    ("Type of Transformation",   "Period average"),
]


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
# Helper: Select a filter option in the IMF Data Explorer sidebar
# ---------------------------------------------------------------------------
def _select_option(
    driver: webdriver.Chrome,
    wait:   WebDriverWait,
    dimension_name: str,
    option_title:   str,
) -> None:
    """
    Opens a filter dimension panel on the IMF Data Explorer and selects
    the specified option by its title attribute.

    Args:
        driver         (webdriver.Chrome): Active WebDriver instance.
        wait           (WebDriverWait):    Configured wait object.
        dimension_name (str):              data-automation-name of the dimension.
        option_title   (str):              Title of the option to select.
    """
    try:
        toggle = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            f"//div[@data-automation-name='{dimension_name}']"
            f"//div[contains(@class,'FacetTitlestyle')]",
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", toggle)
        driver.execute_script("arguments[0].click();", toggle)
        time.sleep(3)

        option = wait.until(EC.element_to_be_clickable((
            By.XPATH, f"//p[@title='{option_title}']",
        )))
        driver.execute_script("arguments[0].click();", option)
        logger.info(f"    [>] Selected '{option_title}' in '{dimension_name}'.")
        time.sleep(1)

    except Exception as e:
        logger.warning(f"    [~] Could not select '{option_title}' in '{dimension_name}': {e}")


# ---------------------------------------------------------------------------
# Helper: Apply all filters, trigger download, and convert CSV → XLSX
# ---------------------------------------------------------------------------
def _run_imf_download(
    download_dir:      str,
    frequency_option:  str,
) -> str | None:
    """
    Orchestrates the full IMF Data Explorer workflow: navigate, apply
    filters, trigger download, and convert the resulting CSV to XLSX.

    Args:
        download_dir     (str): Directory to save downloaded files.
        frequency_option (str): Frequency filter value (e.g. 'Annual' or 'All').

    Returns:
        str | None: Path to the converted .xlsx file on success, None on failure.
    """
    driver = _build_driver(download_dir)
    wait   = WebDriverWait(driver, 60)

    try:
        logger.info(f"[*] Navigating to IMF Exchange Rate dataset (Frequency: {frequency_option}) ...")
        driver.get(IMF_ER_URL)
        time.sleep(10)

        # Apply common filters
        for dimension, option in COMMON_FILTERS:
            _select_option(driver, wait, dimension, option)

        # Apply frequency filter
        _select_option(driver, wait, "Frequency", frequency_option)

        # Set Time Period to All
        try:
            toggle = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//div[@data-automation-name='Time Period']"
                "//div[contains(@class,'FacetTitlestyle')]",
            )))
            driver.execute_script("arguments[0].click();", toggle)
            time.sleep(3)

            radio_all = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//div[@data-automation-name='Time Period']//span[@title='All']",
            )))
            driver.execute_script("arguments[0].click();", radio_all)
            time.sleep(2)
        except Exception as e:
            logger.warning(f"[~] Could not set Time Period to All: {e}")

        # Apply selections
        try:
            apply_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//div[@title='Apply' and contains(@class,'PrimaryBtn')]",
            )))
            driver.execute_script("arguments[0].click();", apply_btn)
            logger.info("[*] Filters applied.")
            time.sleep(8)
        except Exception:
            logger.warning("[~] Apply button not found — skipping.")

        # Trigger download sequence
        logger.info("[*] Initiating data download ...")
        download_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[@title='Download']",
        )))
        driver.execute_script("arguments[0].click();", download_btn)
        time.sleep(2)

        data_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//span[text()='Data on this page']",
        )))
        driver.execute_script("arguments[0].click();", data_btn)
        time.sleep(6)

        final_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//span[text()='DOWNLOAD']",
        )))
        driver.execute_script("arguments[0].click();", final_btn)

        logger.info("[*] Waiting for download to complete ...")
        time.sleep(25)

        # Convert CSV → XLSX
        csv_files = sorted(
            glob.glob(os.path.join(download_dir, "*.csv")),
            key=os.path.getmtime,
            reverse=True,
        )
        if not csv_files:
            raise FileNotFoundError("No CSV file found after download.")

        xlsx_path = csv_files[0].replace(".csv", ".xlsx")
        df = pd.read_csv(csv_files[0])
        df.to_excel(xlsx_path, index=False)
        logger.info(f"[+] Exchange rate data saved to '{xlsx_path}' ({len(df):,} records).")
        return xlsx_path

    except FileNotFoundError as e:
        logger.error(f"[!] File error: {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error: {e}")
    finally:
        driver.quit()

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def download_imf_exchange_rate_annual(download_dir: str = ANNUAL_DIR) -> str | None:
    """
    Downloads IMF exchange rate data filtered to Annual frequency only.

    Args:
        download_dir (str): Directory to save the output file.

    Returns:
        str | None: Path to the .xlsx file on success, None on failure.
    """
    return _run_imf_download(download_dir, frequency_option="Annual")


def download_imf_exchange_rate_all_frequencies(download_dir: str = ALL_FREQ_DIR) -> str | None:
    """
    Downloads IMF exchange rate data for all available frequencies
    (Annual, Quarterly, Monthly).

    Args:
        download_dir (str): Directory to save the output file.

    Returns:
        str | None: Path to the .xlsx file on success, None on failure.
    """
    return _run_imf_download(download_dir, frequency_option="All")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    download_imf_exchange_rate_annual()
    download_imf_exchange_rate_all_frequencies()
