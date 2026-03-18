"""
Module: fetch_wto_trade_data.py
Project: ERS Cooper Trade Data Automation
Description: Automates the download and extraction of WTO agricultural trade data
             (imports and exports with HS codes) using headless Selenium browser automation.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import os
import time
import glob
import tempfile
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def download_wto_agriculture_trade_data():
    """
    Navigates to the WTO agriculture trade page, locates the direct Excel download
    link, downloads the workbook, and extracts each sheet into a separate Excel file.

    Returns:
        str: Path to the download directory containing extracted sheets.
    """
    # Setup dedicated download directory and isolated Chrome profile
    base_dir = os.getcwd()
    download_dir = os.path.join(base_dir, "wto_agriculture_downloads")
    os.makedirs(download_dir, exist_ok=True)
    temp_profile = tempfile.mkdtemp()

    # Configure Chrome preferences for automated downloads
    options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument(f"--user-data-dir={temp_profile}")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        print("[*] Opening WTO agriculture trade page...")
        driver.get("https://www.wto.org/english/tratop_e/agric_e/ag_imp_exp_charts_e.htm")
        time.sleep(5)

        # Locate the direct Excel download link on the page
        print("[*] Locating direct Excel download link...")
        download_link = wait.until(EC.presence_of_element_located((
            By.XPATH, "//a[contains(@href, 'agriculture_trade_data_with_hscodes.xlsx')]"
        )))
        excel_url = download_link.get_attribute("href")

        # Ensure the URL is absolute
        if excel_url.startswith("/"):
            excel_url = "https://www.wto.org" + excel_url

        print(f"[*] Downloading Excel workbook from: {excel_url}")
        driver.get(excel_url)
        time.sleep(10)

        # Poll until the .xlsx file is fully downloaded
        print("[*] Waiting for file to finish downloading...")
        xlsx_file = None
        for _ in range(30):
            files = glob.glob(os.path.join(download_dir, "*.xlsx"))
            if files:
                xlsx_file = max(files, key=os.path.getctime)
                break
            time.sleep(1)

        if not xlsx_file:
            raise FileNotFoundError("[!] Excel file download failed or timed out.")

        print(f"[+] File downloaded: {xlsx_file}")

        # Extract each sheet from the workbook into a separate Excel file
        print("[*] Extracting all sheets from workbook...")
        all_sheets = pd.read_excel(xlsx_file, sheet_name=None)
        for name, df in all_sheets.items():
            cleaned_name = name.strip().replace(" ", "_").lower()
            output_path = os.path.join(download_dir, f"{cleaned_name}_data.xlsx")
            df.to_excel(output_path, index=False)
            print(f"[+] Sheet '{name}' saved as: {output_path}")

        return download_dir

    except Exception as e:
        print(f"[!] Error occurred: {e}")
        return None

    finally:
        driver.quit()
        print("[*] Browser closed.")


if __name__ == "__main__":
    download_wto_agriculture_trade_data()
