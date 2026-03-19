"""
Module:      fetch_imf_gdp.py
Project:     ERS Cooper Trade Data Automation
Description: Automates the extraction of IMF GDP growth and GDP per capita
             datasets using Selenium WebDriver. Converts downloaded files
             to Excel format where applicable.
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
IMF_GROWTH_URL    = (
    "https://www.imf.org/external/datamapper/NGDP_RPCH@WEO"
    "/OEMDC/ADVEC/WEOWORLD"
)
IMF_PERCAPITA_URL = (
    "https://data.imf.org/en/Data-Explorer"
    "?datasetUrn=IMF.RES:WEO(6.0.0)&INDICATOR=NGDPRPC"
)
GROWTH_DIR        = os.path.join(os.getcwd(), "imf_gdp_growth_downloads")
PERCAPITA_DIR     = os.path.join(os.getcwd(), "imf_gdp_per_capita_downloads")


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
# IMF GDP Growth Downloader
# ---------------------------------------------------------------------------
def download_imf_gdp_growth(download_dir: str = GROWTH_DIR) -> str | None:
    """
    Downloads the IMF GDP growth rate (NGDP_RPCH) dataset from the IMF
    DataMapper and converts the resulting .xls file to .xlsx using pandas.

    Args:
        download_dir (str): Directory to save the downloaded file.

    Returns:
        str | None: Path to the converted .xlsx file on success, None on failure.
    """
    driver = _build_driver(download_dir)
    wait   = WebDriverWait(driver, 30)

    try:
        logger.info("[*] Navigating to IMF GDP Growth DataMapper ...")
        driver.get(IMF_GROWTH_URL)
        time.sleep(10)

        logger.info("[*] Clicking download button ...")
        button = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[@class='dm-share-button' and @data-what='all']",
        )))
        button.click()
        time.sleep(20)

        # Locate the most recently downloaded .xls file
        xls_files = sorted(
            glob.glob(os.path.join(download_dir, "*.xls")),
            key=os.path.getmtime,
            reverse=True,
        )
        if not xls_files:
            raise FileNotFoundError("No .xls file found after download.")

        xls_path  = xls_files[0]
        xlsx_path = xls_path.replace(".xls", ".xlsx")

        logger.info(f"[*] Converting '{xls_path}' to .xlsx ...")
        df = pd.read_excel(xls_path)
        df.to_excel(xlsx_path, index=False)
        logger.info(f"[+] IMF GDP Growth saved to '{xlsx_path}'.")
        return xlsx_path

    except FileNotFoundError as e:
        logger.error(f"[!] File error: {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error downloading IMF GDP Growth: {e}")
    finally:
        driver.quit()

    return None


# ---------------------------------------------------------------------------
# IMF GDP Per Capita Downloader
# ---------------------------------------------------------------------------
def _select_checkbox_option(
    driver: webdriver.Chrome,
    wait: WebDriverWait,
    dimension_name: str,
    option_title: str,
) -> None:
    """
    Opens a filter dimension panel on the IMF Data Explorer and selects
    the specified checkbox option.

    Args:
        driver         (webdriver.Chrome): Active WebDriver instance.
        wait           (WebDriverWait):    Configured wait object.
        dimension_name (str):              Data-automation-name of the dimension.
        option_title   (str):              Title attribute of the option to select.
    """
    try:
        toggle = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            f"//div[@data-automation-name='{dimension_name}']"
            f"//div[contains(@class,'FacetTitlestyle')]",
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", toggle)
        driver.execute_script("arguments[0].click();", toggle)
        time.sleep(2)

        search_input = wait.until(EC.presence_of_element_located((
            By.XPATH,
            f"//div[@data-automation-name='{dimension_name}']"
            f"//input[@type='search']",
        )))
        search_input.clear()
        search_input.send_keys(option_title)
        time.sleep(3)

        checkbox = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            f"//div[@data-automation-name='{dimension_name}']"
            f"//div[@data-automation-id='FacetCheckbox' "
            f"and .//p[@title="{option_title}"]]",
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        driver.execute_script("arguments[0].click();", checkbox)
        logger.info(f"    [>] Selected '{option_title}' in '{dimension_name}'.")
        time.sleep(2)

    except Exception as e:
        logger.warning(f"    [~] Could not select '{option_title}' in '{dimension_name}': {e}")


def download_imf_gdp_per_capita(download_dir: str = PERCAPITA_DIR) -> str | None:
    """
    Navigates the IMF Data Explorer, applies filters for the NGDPRPC
    indicator, downloads the dataset as CSV, and converts it to .xlsx.

    Args:
        download_dir (str): Directory to save the downloaded file.

    Returns:
        str | None: Path to the converted .xlsx file on success, None on failure.
    """
    driver = _build_driver(download_dir)
    wait   = WebDriverWait(driver, 60)
    driver.implicitly_wait(10)

    try:
        logger.info("[*] Navigating to IMF GDP Per Capita dataset ...")
        driver.get(IMF_PERCAPITA_URL)
        time.sleep(10)

        # Open filters sidebar
        filters_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(@class,'FiltersButton') and contains(text(),'Filters')]",
        )))
        driver.execute_script("arguments[0].click();", filters_btn)
        time.sleep(3)

        # Apply dimension filters
        _select_checkbox_option(driver, wait, "Indicator",  "NGDPRPC")
        _select_checkbox_option(driver, wait, "Frequency",  "All")

        # Select Time Period: All
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
            time.sleep(8)
        except Exception:
            logger.warning("[~] Apply button not found — skipping.")

        # Trigger download
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
        time.sleep(40)

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
        logger.info(f"[+] IMF GDP Per Capita saved to '{xlsx_path}'.")
        return xlsx_path

    except FileNotFoundError as e:
        logger.error(f"[!] File error: {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error downloading IMF GDP Per Capita: {e}")
    finally:
        driver.quit()

    return None


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    download_imf_gdp_growth()
    download_imf_gdp_per_capita()
