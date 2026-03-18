"""
Module: fetch_wits_imports.py
Project: ERS Cooper Trade Data Automation
Description: Automates the download and cleaning of WITS Import data using
             headless Selenium browser automation.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import os
import time
import glob
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def download_and_clean_wits_imports():
    """
    Navigates to the WITS Import Data page, triggers an Excel download,
    waits for the file to complete, and cleans the 'Country-Timeseries' sheet.

    Returns:
        str: Path to the cleaned Excel file.
    """
    url = "https://wits.worldbank.org/CountryProfile/en/Country/BY-COUNTRY/StartYear/1988/EndYear/2022/Indicator/TM-VAL-MRCH-XD-WD"

    # Setup dedicated download directory
    base_dir = os.getcwd()
    download_dir = os.path.join(base_dir, "wits_imports_downloads")
    os.makedirs(download_dir, exist_ok=True)

    # Configure Chrome preferences for automated downloads
    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        print(f"[*] Opening WITS Import Data page: {url}")
        driver.get(url)

        # Allow the page to fully load before interacting
        time.sleep(10)

        # Trigger the download dialog
        print("[*] Clicking download button...")
        download_button = wait.until(EC.element_to_be_clickable((By.ID, "DataDownload")))
        download_button.click()

        # Select Excel format from the dropdown
        print("[*] Selecting Excel format...")
        excel_option = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "li.excel a[data-customlink*='xls']")
        ))
        excel_option.click()

        # Poll until the .xlsx file is fully downloaded (no .crdownload in progress)
        print("[*] Waiting for download to complete...")
        downloaded_file = None
        start_time = time.time()
        timeout = 60

        while time.time() - start_time < timeout:
            xlsx_files = glob.glob(os.path.join(download_dir, "*.xlsx"))
            crdownloads = glob.glob(os.path.join(download_dir, "*.crdownload"))

            if xlsx_files and not crdownloads:
                # Select the most recently created file
                downloaded_file = max(xlsx_files, key=os.path.getctime)
                break

            time.sleep(1)

        if not downloaded_file:
            raise FileNotFoundError("[!] Downloaded .xlsx file not found or still incomplete.")

        # Read and clean the target sheet
        print(f"[*] Reading 'Country-Timeseries' sheet from: {downloaded_file}")
        df = pd.read_excel(downloaded_file, sheet_name="Country-Timeseries")

        # Persist cleaned data to local storage
        cleaned_path = os.path.join(download_dir, "Cleaned_WITS_Imports.xlsx")
        df.to_excel(cleaned_path, index=False)

        print(f"[+] Download and cleanup complete. Saved to: {cleaned_path}")
        return cleaned_path

    except Exception as e:
        print(f"[!] Error: {e}")
        return None

    finally:
        driver.quit()
        print("[*] Browser closed.")


if __name__ == "__main__":
    download_and_clean_wits_imports()
