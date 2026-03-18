"""
Module: merge_country_datasets.py
Project: ERS Cooper Trade Data Automation
Description: Merges all fetched datasets into a final, harmonized Excel file.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import os
import pandas as pd

def merge_country_datasets():
    """
    Harmonizes and merges all CSV datasets into a single Excel file.
    
    Returns:
        pd.DataFrame: Final harmonized dataset.
    """
    # Define file paths for all datasets
    file_paths = {
        "FAO": "filtered_FAO.csv",
        "FAS": "Filtered_FAS.csv",
        "IMF": "Filtered_IMF.csv",
        "PSD": "Filtered_PSD.csv",
        "Reporters": "Filtered_Reporters.csv",
        "UN_Comtrade": "Filtered_UN_Comtrade.csv",
        "WITS": "Filtered_WITs.csv",
        "WITS_Partners": "Filtered_Wits_Partners_Country_list.csv",
        "Worldbank": "Filtered_Worldbank.csv",
        "US_Census": "filtered_USCensus_Country_List.csv"
    }

    # Load all CSVs into a dictionary of dataframes
    dataframes = {}
    for name, path in file_paths.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
            dataframes[name] = df
        else:
            print(f"[!] Warning: {path} not found. Skipping {name} in merge.")

    # Validate critical datasets for the merge process
    if "UN_Comtrade" not in dataframes or "US_Census" not in dataframes:
        print("[!] Critical Error: UN Comtrade or US Census data missing. Cannot complete merge.")
        return None

    un_comtrade_df = dataframes["UN_Comtrade"]
    us_census_df = dataframes["US_Census"]

    # Standardize ISO2/ISO3 for US Census merge
    if "ISO-alpha2 Code" in un_comtrade_df.columns:
        un_comtrade_df.rename(columns={"ISO-alpha2 Code": "ISO2"}, inplace=True)

    un_comtrade_df["ISO2"] = un_comtrade_df["ISO2"].astype(str).str.strip()
    us_census_df["ISO2"] = us_census_df["ISO2"].astype(str).str.strip()

    # Merge US Census with UN Comtrade on ISO2 to obtain ISO3
    us_census_merged = pd.merge(us_census_df, un_comtrade_df[["ISO2", "ISO3"]], on="ISO2", how="left")
    dataframes["US_Census"] = us_census_merged

    # Initialize the merged dataset
    merged_data = None
    for name, df in dataframes.items():
        if "ISO3" in df.columns:
            df["ISO3"] = df["ISO3"].astype(str).str.strip()
            if merged_data is None:
                merged_data = df
            else:
                # Outer merge to ensure all countries are captured
                merged_data = pd.merge(merged_data, df, on="ISO3", how="outer")

    # Load WBGDP dataset for filtering (Required for project scope)
    if os.path.exists("WBGDP.csv"):
        wbgdp_data = pd.read_csv("WBGDP.csv")
        wbgdp_data.columns = wbgdp_data.columns.str.strip()
        wbgdp_data.rename(columns={"Country Code": "ISO3"}, inplace=True)
        wbgdp_data["ISO3"] = wbgdp_data["ISO3"].astype(str).str.strip()

        # Filter merged dataset to only countries present in GDP dataset
        filtered_merged_data = merged_data[merged_data["ISO3"].isin(wbgdp_data["ISO3"])]
    else:
        print("[!] Warning: WBGDP.csv not found. Skipping GDP-based filtering.")
        filtered_merged_data = merged_data

    # Fill missing country names using 'Country UN' as the primary reference
    if "Country UN" in filtered_merged_data.columns:
        for col in ["Country FAS", "Country WITS", "Country Reporters"]:
            if col in filtered_merged_data.columns:
                filtered_merged_data[col] = filtered_merged_data[col].fillna(filtered_merged_data["Country UN"])

    # Remove duplicate rows based on the ISO3 column
    filtered_merged_data = filtered_merged_data.drop_duplicates(subset="ISO3", keep="first")

    # Persist final harmonized dataset to Excel
    merged_excel_path = "Merged_Countrylist_data.xlsx"
    filtered_merged_data.to_excel(merged_excel_path, index=False)
    
    print(f"[+] Final harmonized dataset saved as: {merged_excel_path}")
    return filtered_merged_data

if __name__ == "__main__":
    merge_country_datasets()
