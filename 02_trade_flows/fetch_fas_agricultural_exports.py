"""
Module: fetch_fas_agricultural_exports.py
Project: ERS Cooper Trade Data Automation
Description: Automates the scraping of agricultural export data (1967–2024) from the
             USDA FAS GATS Express Query tool using Selenium browser automation.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def fetch_fas_agricultural_export_data():
    """
    Navigates to the USDA FAS GATS Express Query tool, selects all partners,
    agricultural products, and the full year range (1967–2024), then scrapes
    and saves the resulting trade data table to CSV.

    Returns:
        pd.DataFrame: Scraped agricultural export data.
    """
    # Configure Chrome to remain open after script completes (for debugging)
    options = Options()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 120)  # Extended timeout for large data loads

    try:
        # Step 1: Navigate to the GATS Express Query page
        print("[*] Navigating to USDA FAS GATS Express Query...")
        driver.get("https://apps.fas.usda.gov/gats/default.aspx")
        time.sleep(2)
        driver.get("https://apps.fas.usda.gov/gats/ExpressQuery1.aspx")

        # Step 2: Select all trade partners
        print("[*] Selecting All Partners...")
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_lb_Partners")))
        Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lb_Partners")).select_by_value("ALLPT")
        print("[+] Selected All Partners.")

        # Step 3: Select agricultural products category
        print("[*] Selecting Agricultural Products...")
        product_box = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lb_Products"))
        product_box.deselect_all()
        product_box.select_by_value("M1")
        print("[+] Selected Agricultural Products.")

        # Step 4: Set the year range (1967–2024)
        print("[*] Setting year range: 1967 – 2024...")
        Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlStartYear")).select_by_visible_text("1967")
        time.sleep(1)
        Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlEndYear")).select_by_visible_text("2024")
        print("[+] Year range set.")

        # Step 5: Trigger data retrieval via JavaScript click (more reliable than direct click)
        print("[*] Triggering data retrieval...")
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_btnRetrieveData")))
        driver.execute_script("document.getElementById('ctl00_ContentPlaceHolder1_btnRetrieveData').click();")
        print("[*] Waiting for data table to load...")

        # Step 6: Wait for the results table to appear
        wait.until(EC.presence_of_element_located((By.ID, "igtabctl00_ContentPlaceHolder1_UltraWebTab1")))
        print("[+] Table loaded. Beginning data extraction...")

        # Step 7: Scrape all rows from the results table
        data = []
        rows = driver.find_elements(
            By.XPATH, "//table[@id='igtabctl00_ContentPlaceHolder1_UltraWebTab1']//tr"
        )

        for i in range(2, len(rows) + 1):  # Skip the header row
            try:
                row = driver.find_elements(
                    By.XPATH,
                    f"(//table[@id='igtabctl00_ContentPlaceHolder1_UltraWebTab1']//tr)[{i}]/td"
                )
                if len(row) > 5:
                    # Extract: Partner (index 1), Product (index 3), Year values (index 4+)
                    partner = row[1].text.strip()
                    product = row[3].text.strip()
                    values = [cell.text.strip().replace(",", "") for cell in row[4:]]
                    data.append([partner, product] + values)
            except Exception as e:
                print(f"[!] Skipped row {i}: {e}")

        # Step 8: Build and save the dataframe
        if data:
            num_columns = len(data[0])
            print(f"[*] Detected {num_columns} columns per row.")

            # Auto-generate column headers based on detected column count
            columns = (
                ["Partner", "Product"]
                + [f"Year_{i}" for i in range(1, num_columns - 1)]
                + ["Period/Period % Change (Value)"]
            )

            # Assign column names only if count matches; otherwise use auto-naming
            if len(columns) == num_columns:
                df = pd.DataFrame(data, columns=columns)
            else:
                df = pd.DataFrame(data)

            output_file = "FAS_Agricultural_Export_1967_2024.csv"
            df.to_csv(output_file, index=False)
            print(f"[+] Data saved to: {output_file}")
            return df
        else:
            print("[!] No data was scraped.")
            return None

    except Exception as e:
        print(f"[!] An error occurred: {e}")
        return None


if __name__ == "__main__":
    fetch_fas_agricultural_export_data()
