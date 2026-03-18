"""
Module: fetch_trademap_exports.py
Project: ERS Cooper Trade Data Automation
Description: Automates the download and conversion of global export trade data
             from the TradeMap website using headless Selenium browser automation.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def download_trademap_export_data():
    """
    Navigates to the TradeMap export data page, triggers an Excel download,
    and converts the downloaded .xls file to a cleaned .xlsx format.

    Returns:
        str: Path to the cleaned Excel file.
    """
    url = (
        "https://www.trademap.org/Country_SelProduct_TS.aspx"
        "?nvpm=1%7c%7c%7c%7c%7cTOTAL%7c%7c%7c2%7c1%7c1%7c2%7c2%7c1%7c2%7c1%7c1%7c1"
    )

    # Setup dedicated download directory
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    # Configure Chrome preferences for automated downloads
    chrome_options = Options()
    prefs = {"download.default_directory": download_dir}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Step 1: Navigate to the TradeMap export data page
        print(f"[*] Opening TradeMap website: {url}")
        driver.get(url)

        # Allow the page to fully load before interacting
        time.sleep(10)

        # Step 2: Locate and click the Excel download button
        print("[*] Locating the download button...")
        download_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.ID, "ctl00_PageContent_GridViewPanelControl_ImageButton_ExportExcel")
            )
        )
        print("[*] Clicking the download button...")
        download_button.click()

        # Allow the download to initiate
        time.sleep(5)

        # Step 3: Poll until the .xls file appears in the download directory
        print("[*] Waiting for the file to download...")
        downloaded_file = None
        for _ in range(30):
            files = os.listdir(download_dir)
            for file in files:
                if file.endswith(".xls"):
                    downloaded_file = os.path.join(download_dir, file)
                    break
            if downloaded_file:
                break
            time.sleep(1)

        if not downloaded_file:
            raise FileNotFoundError("[!] File download failed or timed out.")

        print(f"[+] Download completed: {downloaded_file}")

        # Step 4: Parse the .xls file as an HTML table and extract trade data
        destination_file = os.path.join(download_dir, "TradeMap_ExportData.xlsx")
        print(f"[*] Reading {downloaded_file} as an HTML table...")
        dataframes = pd.read_html(downloaded_file)

        if not dataframes:
            raise ValueError("[!] No tables found in the downloaded file.")

        # Identify the correct trade data table by checking for 'Exporters' column
        trade_data = None
        for df in dataframes:
            if "Exporters" in df.columns:
                trade_data = df
                break

        if trade_data is None:
            raise ValueError("[!] Trade data table not found in the file.")

        # Drop the first row if it contains excessive NaN values (header artifact)
        if trade_data.iloc[0].isnull().sum() > 5:
            trade_data = trade_data.iloc[1:].reset_index(drop=True)

        # Standardize column names by removing newlines and extra whitespace
        trade_data.columns = trade_data.columns.str.replace("\n", " ").str.strip()

        # Step 5: Persist the cleaned data to Excel
        print(f"[*] Saving cleaned data to: {destination_file}")
        trade_data.to_excel(destination_file, index=False)

        print(f"[+] File successfully converted and saved to: {destination_file}")
        return destination_file

    except FileNotFoundError as fnfe:
        print(f"[!] File error: {fnfe}")
    except ValueError as ve:
        print(f"[!] Value error: {ve}")
    except ImportError as ie:
        print(f"[!] Import error: {ie}. Ensure 'pandas' and 'lxml' are installed.")
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")
    finally:
        print("[*] Closing the browser...")
        driver.quit()


if __name__ == "__main__":
    download_trademap_export_data()
