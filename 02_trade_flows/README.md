# Trade Flows Data Automation

This module automates the collection of agricultural trade flow data (imports and exports) from multiple international trade databases.

## Module Objectives
- Automate the download of bilateral agricultural trade data.
- Support gravity model estimation with import and export flow variables.
- Collect data across multiple sources to ensure robustness and cross-validation.

## Script Descriptions

| File | Source | Method |
| :--- | :--- | :--- |
| `fetch_wits_imports.py` | WITS / World Bank | Selenium (Excel Download) |
| `fetch_wits_exports.py` | WITS / World Bank | Selenium (Excel Download) |
| `fetch_wto_trade_data.py` | WTO | Selenium (Multi-sheet Excel) |
| `fetch_fas_agricultural_exports.py` | USDA FAS GATS | Selenium (Table Scraping) |
| `fetch_fas_gats_exports.py` | USDA FAS API | REST API (JSON) |
| `fetch_worldbank_agriexports.py` | World Bank Data360 | Selenium (SDMX CSV) |
| `fetch_worldbank_agrimports.py` | World Bank Data360 | Selenium (SDMX CSV) |
| `fetch_trademap_exports.py` | TradeMap | Selenium (XLS to XLSX) |

## Usage
Run each script individually to download trade flow data from its respective source. Outputs are saved to dedicated local download directories.