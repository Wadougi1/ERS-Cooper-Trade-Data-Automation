# Country Reference Data Automation

This module contains a suite of Python scripts designed to automate the collection, cleaning, and harmonization of country-level reference data from multiple international sources.

## Module Objectives
- Automate data extraction from global trade and economic databases.
- Standardize inconsistent country naming conventions and ISO codes.
- Provide a unified source of truth for country metadata used in trade analysis.

## Script Descriptions

| File | Source | Method |
| :--- | :--- | :--- |
| `fetch_un_comtrade.py` | UN Comtrade | API (JSON) |
| `fetch_fas_psd.py` | USDA FAS/PSD | API (JSON) |
| `fetch_worldbank_wits.py` | World Bank / WITS | API & XML |
| `fetch_imf_reporters.py` | IMF DataMapper | API (JSON) |
| `fetch_fao_census.py` | FAO & US Census | Selenium (Scraping) |
| `merge_country_datasets.py` | All Sources | Pandas (Merging) |
| `config.py` | Local | Environment Variables |

## Usage
Ensure your API keys are set in your environment variables, then run the scripts individually or use the merge script to generate the final harmonized dataset.