"""
Module:      fetch_wto_trade_agreements.py
Project:     ERS Cooper Trade Data Automation
Description: Automates the scraping and downloading of WTO Regional Trade
             Agreement (RTA) and Preferential Trade Agreement (PTA) data
             from the WTO RTAIS and PTADB portals using Selenium WebDriver.
             Provides three functions:
               1. fetch_wto_agreements()  — scrapes the RTA agreement list.
               2. fetch_pta_list()        — scrapes the PTA agreement list.
               3. download_wto_rta_excel()— downloads the full AllRTAs Excel file.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

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
RTA_HOME_URL  = "https://rtais.wto.org/UI/PublicMaintainRTAHome.aspx"
RTA_TABLE_URL = "https://rtais.wto.org/UI/publicPreDefRepByCountry.aspx"
PTA_LIST_URL  = "https://ptadb.wto.org/ptaList.aspx"
DOWNLOAD_DIR  = os.path.join(os.getcwd(), "downloads")


# ---------------------------------------------------------------------------
# Helper: Build headless Chrome driver with download preferences
# ---------------------------------------------------------------------------
def _build_driver(download_dir: str | None = None) -> webdriver.Chrome:
    """
    Builds and returns a headless Chrome WebDriver. If a download directory
    is provided, configures Chrome for silent file downloads.

    Args:
        download_dir (str | None): Directory for downloaded files, or None
                                   if no file download is expected.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if download_dir:
        os.makedirs(download_dir, exist_ok=True)
        options.add_experimental_option("prefs", {
            "download.default_directory":   download_dir,
            "download.prompt_for_download": False,
            "safebrowsing.enabled":         True,
        })

    return webdriver.Chrome(options=options)


# ---------------------------------------------------------------------------
# 1. WTO RTA Agreement List Scraper
# ---------------------------------------------------------------------------
def fetch_wto_agreements(
    output_file:  str = "wto_agreement_list.csv",
    download_dir: str = DOWNLOAD_DIR,
) -> pd.DataFrame | None:
    """
    Scrapes the WTO RTAIS agreement list table and saves it to a CSV file.

    Navigates to the WTO RTA homepage and the pre-defined country report
    page, then extracts the agreement table (CSS class: Grid table-striped).

    Args:
        output_file  (str): Filename for the saved CSV.
        download_dir (str): Directory to save the output CSV.

    Returns:
        pd.DataFrame | None: Scraped DataFrame on success, None on failure.
    """
    os.makedirs(download_dir, exist_ok=True)
    driver = _build_driver()
    wait   = WebDriverWait(driver, 10)

    try:
        # Visit both pages to establish session context
        for url in [RTA_HOME_URL, RTA_TABLE_URL]:
            logger.info(f"[*] Navigating to: {url}")
            driver.get(url)
            time.sleep(5)

        logger.info("[*] Waiting for the RTA agreement table to load ...")
        table = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "table.Grid.table-striped")
        ))

        rows    = table.find_elements(By.XPATH, ".//tr")
        headers = [th.text for th in table.find_elements(By.XPATH, ".//th")]
        data    = [
            [cell.text for cell in row.find_elements(By.XPATH, ".//td")]
            for row in rows
        ]

        df = pd.DataFrame(data[1:], columns=headers)
        df.dropna(how="all", inplace=True)

        output_path = os.path.join(download_dir, output_file)
        df.to_csv(output_path, index=False)
        logger.info(f"[+] WTO agreement list saved to '{output_path}' ({len(df):,} rows).")
        return df

    except Exception as e:
        logger.error(f"[!] Error scraping WTO agreement list: {e}")
        return None
    finally:
        driver.quit()


# ---------------------------------------------------------------------------
# 2. WTO PTA List Scraper
# ---------------------------------------------------------------------------
def fetch_pta_list(
    output_file:  str = "PTA_List.csv",
    download_dir: str = DOWNLOAD_DIR,
) -> pd.DataFrame | None:
    """
    Scrapes the WTO PTADB preferential trade agreement list and saves it
    to a CSV file.

    Args:
        output_file  (str): Filename for the saved CSV.
        download_dir (str): Directory to save the output CSV.

    Returns:
        pd.DataFrame | None: Scraped DataFrame on success, None on failure.
    """
    os.makedirs(download_dir, exist_ok=True)
    driver = _build_driver()
    wait   = WebDriverWait(driver, 10)

    try:
        logger.info("[*] Navigating to WTO RTA homepage ...")
        driver.get(RTA_HOME_URL)
        time.sleep(3)

        logger.info("[*] Navigating to WTO PTA list page ...")
        driver.get(PTA_LIST_URL)
        time.sleep(3)

        logger.info("[*] Waiting for the PTA table to load ...")
        table = wait.until(EC.presence_of_element_located(
            (By.ID, "MainContent_ptaListControl1_GridView1")
        ))

        rows    = table.find_elements(By.XPATH, ".//tr")
        headers = [th.text for th in table.find_elements(By.XPATH, ".//th")]
        data    = [
            [cell.text for cell in row.find_elements(By.XPATH, ".//td")]
            for row in rows
        ]

        df = pd.DataFrame(data[1:], columns=headers)
        df.dropna(how="all", inplace=True)

        output_path = os.path.join(download_dir, output_file)
        df.to_csv(output_path, index=False)
        logger.info(f"[+] WTO PTA list saved to '{output_path}' ({len(df):,} rows).")
        return df

    except Exception as e:
        logger.error(f"[!] Error scraping WTO PTA list: {e}")
        return None
    finally:
        driver.quit()


# ---------------------------------------------------------------------------
# 3. WTO AllRTAs Excel Downloader
# ---------------------------------------------------------------------------
def download_wto_rta_excel(
    download_dir: str = DOWNLOAD_DIR,
    wait_time:    int = 20,
) -> str | None:
    """
    Downloads the full WTO AllRTAs Excel file from the RTAIS portal by
    clicking the export link, then re-saves it as 'WTO_AllRTAs.xlsx'.

    Args:
        download_dir (str): Directory to save the downloaded Excel file.
        wait_time    (int): Seconds to wait for the download to complete.

    Returns:
        str | None: Path to the saved 'WTO_AllRTAs.xlsx' file on success,
                    None on failure.
    """
    driver = _build_driver(download_dir)
    wait   = WebDriverWait(driver, 20)

    try:
        logger.info("[*] Navigating to WTO RTA homepage ...")
        driver.get(RTA_HOME_URL)
        time.sleep(3)

        logger.info("[*] Clicking the export link ...")
        export_btn = wait.until(EC.element_to_be_clickable(
            (By.ID, "ContentPlaceHolder1_lnkExport")
        ))
        driver.execute_script("arguments[0].click();", export_btn)

        logger.info(f"[*] Waiting {wait_time}s for download to complete ...")
        time.sleep(wait_time)

        source = os.path.join(download_dir, "AllRTAs.xlsx")
        target = os.path.join(download_dir, "WTO_AllRTAs.xlsx")

        if not os.path.exists(source):
            raise FileNotFoundError(f"Expected download not found: '{source}'")

        df = pd.read_excel(source)
        df.to_excel(target, index=False)
        logger.info(f"[+] WTO AllRTAs Excel saved to '{target}' ({len(df):,} rows).")
        return target

    except FileNotFoundError as e:
        logger.error(f"[!] File error: {e}")
    except Exception as e:
        logger.error(f"[!] Error downloading WTO RTA Excel: {e}")
    finally:
        driver.quit()

    return None


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    fetch_wto_agreements()
    fetch_pta_list()
    download_wto_rta_excel()
