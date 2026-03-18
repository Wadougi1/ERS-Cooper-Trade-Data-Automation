"""
Module:      fetch_wits_commodities.py
Project:     ERS Cooper Trade Data Automation
Description: Scrapes WITS HS6 product descriptions and downloads the World
             Bank HS Nomenclature dataset using Selenium WebDriver.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import logging
import os
import time
import zipfile

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
WITS_HS6_URL   = "https://wits.worldbank.org/trade/country-byhs6product.aspx?"
WITS_LOGIN_URL = "https://wits.worldbank.org/WITS/WITS/Restricted/Login.aspx"
WITS_DL_URL    = (
    "https://wits.worldbank.org/WITS/WITS/Results/Queryview/"
    "QueryView.aspx?Page=DownloadandViewResults&Download=true"
)
DOWNLOAD_DIR   = os.path.join(os.getcwd(), "temp_wits_commodities")


# ---------------------------------------------------------------------------
# Helper: Build headless Chrome driver
# ---------------------------------------------------------------------------
def _build_driver(download_dir: str | None = None) -> webdriver.Chrome:
    """
    Builds and returns a headless Chrome WebDriver instance.

    Args:
        download_dir (str | None): Optional directory for file downloads.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if download_dir:
        os.makedirs(download_dir, exist_ok=True)
        prefs = {"download.default_directory": download_dir}
        options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=options)


# ---------------------------------------------------------------------------
# WITS HS6 Product List Scraper
# ---------------------------------------------------------------------------
def scrape_wits_hs6_list(output_file: str = "WITS_HS6_List.csv") -> pd.DataFrame:
    """
    Scrapes the interactive HS6 product list from the WITS portal.

    Args:
        output_file (str): Destination CSV file path.

    Returns:
        pd.DataFrame: DataFrame with columns ['Code', 'Description'],
                      or an empty DataFrame on failure.
    """
    driver = _build_driver()

    try:
        logger.info("[*] Navigating to WITS HS6 product page ...")
        driver.get(WITS_HS6_URL)

        wait  = WebDriverWait(driver, 20)
        tbody = wait.until(EC.presence_of_element_located((By.ID, "searchResults")))

        flattened_data = []
        for tr in tbody.find_elements(By.TAG_NAME, "tr"):
            for td in tr.find_elements(By.TAG_NAME, "td"):
                text = td.text
                if "--" in text:
                    parts = text.split("--", 1)
                    flattened_data.append([parts[0].strip(), parts[1].strip()])

        df = pd.DataFrame(flattened_data, columns=["Code", "Description"])
        df.to_csv(output_file, index=False)
        logger.info(f"[+] Saved {len(df):,} HS6 products to '{output_file}'.")
        return df

    except Exception as e:
        logger.error(f"[!] WITS HS6 scraper error: {e}")
        return pd.DataFrame()

    finally:
        driver.quit()


# ---------------------------------------------------------------------------
# World Bank HS Nomenclature Downloader
# ---------------------------------------------------------------------------
def download_wb_nomenclature(
    username: str,
    password: str,
    output_file: str = "WB_HS_Nomenclature.csv",
) -> pd.DataFrame:
    """
    Logs into the WITS portal and downloads the World Bank HS Nomenclature
    dataset, extracts the ZIP archive, and saves the result to CSV.

    Args:
        username    (str): WITS account username.
        password    (str): WITS account password.
        output_file (str): Destination CSV file path.

    Returns:
        pd.DataFrame: The downloaded nomenclature data,
                      or an empty DataFrame on failure.
    """
    driver = _build_driver(download_dir=DOWNLOAD_DIR)

    try:
        logger.info("[*] Logging into WITS for Nomenclature download ...")
        driver.get(WITS_LOGIN_URL)

        driver.find_element(By.ID, "UserNameTextBox").send_keys(username)
        driver.find_element(By.ID, "UserPassTextBox").send_keys(password)
        driver.find_element(By.ID, "btnSubmit").click()
        time.sleep(5)

        logger.info("[*] Navigating to download page ...")
        driver.get(WITS_DL_URL)

        save_btn = driver.find_element(
            By.XPATH, "//td[@title='Save' and contains(@onclick, 'SaveJob')]"
        )
        save_btn.click()

        logger.info("[*] Waiting for download to complete ...")
        time.sleep(15)

        # Locate and extract ZIP
        zip_path = next(
            (
                os.path.join(DOWNLOAD_DIR, f)
                for f in os.listdir(DOWNLOAD_DIR)
                if f.endswith(".zip")
            ),
            None,
        )

        if not zip_path:
            logger.error("[!] No ZIP file found in download directory.")
            return pd.DataFrame()

        extracted_dir = os.path.join(DOWNLOAD_DIR, "extracted")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extracted_dir)
        logger.info(f"[*] Extracted ZIP to '{extracted_dir}'.")

        # Locate the CSV inside the extracted folder
        csv_path = next(
            (
                os.path.join(extracted_dir, f)
                for f in os.listdir(extracted_dir)
                if f.endswith(".csv") and "DataJobID" in f
            ),
            None,
        )

        if not csv_path:
            logger.error("[!] Target CSV not found in extracted archive.")
            return pd.DataFrame()

        df = pd.read_csv(csv_path, encoding="ISO-8859-1")
        df.to_csv(output_file, index=False)
        logger.info(f"[+] WB HS Nomenclature saved to '{output_file}' ({len(df):,} records).")
        return df

    except Exception as e:
        logger.error(f"[!] WB Nomenclature download error: {e}")
        return pd.DataFrame()

    finally:
        driver.quit()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    scrape_wits_hs6_list()
    # Uncomment and supply credentials to run the WB Nomenclature downloader:
    # download_wb_nomenclature(username="your_user", password="your_pass")
