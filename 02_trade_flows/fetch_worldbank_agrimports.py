"""
Module: fetch_worldbank_agrimports.py
Project: ERS Cooper Trade Data Automation
Description: Automates the download of Agricultural Imports data from the World Bank
             Data360 portal using headless Selenium browser automation.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def download_worldbank_agrimports_data():
    """
    Navigates to the World Bank Agricultural Imports indicator page and
    triggers an SDMX CSV download via the Data dropdown menu.

    Returns:
        str: Path to the download directory.
    """
    url = "https://data360.worldbank.org/en/indicator/WB_WDI_TM_VAL_AGRI_ZS_UN"

    # Setup dedicated download directory
    download_dir = os.path.join(os.getcwd(), "worldbank_agrimports_downloads")
    os.makedirs(download_dir, exist_ok=True)

    # Configure Chrome preferences for silent, automated downloads
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        print(f"[*] Navigating to World Bank Agricultural Imports dataset: {url}")
        driver.get(url)

        # Allow dynamic content to fully render
        time.sleep(10)

        # Click the 'Data' dropdown button to reveal download options
        print("[*] Clicking the download dropdown button...")
        download_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class,'dropdown-toggle') and .//span[text()='Data']]")
        ))
        download_button.click()
        time.sleep(2)

        # Select the SDMX CSV format from the dropdown
        print("[*] Selecting 'SDMX CSV' download option...")
        sdmx_option = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[text()='SDMX CSV']")
        ))
        sdmx_option.click()

        # Allow time for the download to complete
        time.sleep(20)

        print(f"[+] Download triggered. Check folder: {download_dir}")
        return download_dir

    except Exception as e:
        print(f"[!] Error during automation: {e}")
        return None

    finally:
        driver.quit()


if __name__ == "__main__":
    download_worldbank_agrimports_data()
