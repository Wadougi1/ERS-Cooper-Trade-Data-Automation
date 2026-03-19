"""
Module:      fetch_wits_gdp.py
Project:     ERS Cooper Trade Data Automation
Description: Automates the download and cleaning of GDP per capita data
             from the World Bank WITS portal using Selenium WebDriver.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import glob
import logging
import os
import time

import pandas as pd
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
WITS_GDP_URL = (
    "https://wits.worldbank.org/CountryProfile/en/Country/BY-COUNTRY"
    "/StartYear/1988/EndYear/2022/Indicator/NY-GDP-PCAP-CD"
)
DOWNLOAD_DIR = os.path.join(os.getcwd(), "wits_gdp_downloads")
SHEET_NAME   = "Country-Timeseries"


# ---------------------------------------------------------------------------
# WITS GDP Downloader
# ---------------------------------------------------------------------------
def download_and_clean_wits_gdp(
    download_dir: str = DOWNLOAD_DIR,
    output_file:  str = "Cleaned_WITS_GDP.xlsx",
) -> str | None:
    """
    Opens the WITS GDP per capita page, triggers an Excel download,
    reads the 'Country-Timeseries' sheet, and saves a cleaned copy.

    Args:
        download_dir (str): Directory to save the downloaded file.
        output_file  (str): Filename for the cleaned output Excel file.

    Returns:
        str | None: Path to the cleaned output file on success, None on failure.
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

    driver = webdriver.Chrome(options=options)
    wait   = WebDriverWait(driver, 30)

    try:
        logger.info("[*] Opening WITS GDP per capita page ...")
        driver.get(WITS_GDP_URL)
        time.sleep(10)

        logger.info("[*] Clicking download icon ...")
        download_icon = wait.until(EC.element_to_be_clickable((By.ID, "DataDownload")))
        download_icon.click()

        logger.info("[*] Selecting Excel format ...")
        excel_option = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "li.excel a[data-customlink*='xls']",
        )))
        excel_option.click()

        # Poll until the .xlsx file is fully downloaded
        logger.info("[*] Waiting for download to complete ...")
        downloaded_file = None
        deadline = time.time() + 60

        while time.time() < deadline:
            xlsx_files    = glob.glob(os.path.join(download_dir, "*.xlsx"))
            crdownloads   = glob.glob(os.path.join(download_dir, "*.crdownload"))
            if xlsx_files and not crdownloads:
                downloaded_file = max(xlsx_files, key=os.path.getctime)
                break
            time.sleep(1)

        if not downloaded_file:
            raise FileNotFoundError("Downloaded .xlsx file not found or still incomplete.")

        logger.info(f"[*] Reading sheet '{SHEET_NAME}' from '{downloaded_file}' ...")
        df = pd.read_excel(downloaded_file, sheet_name=SHEET_NAME)

        output_path = os.path.join(download_dir, output_file)
        df.to_excel(output_path, index=False)
        logger.info(f"[+] Cleaned WITS GDP data saved to '{output_path}'.")
        return output_path

    except FileNotFoundError as e:
        logger.error(f"[!] File error: {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error downloading WITS GDP: {e}")
    finally:
        driver.quit()

    return None


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    download_and_clean_wits_gdp()
