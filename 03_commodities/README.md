# Commodity and Product Reference Automation

This module manages the identification, classification, and grouping of agricultural commodities and products using international standards (HS codes) and USDA-specific classifications.

## Module Objectives
- Automate the retrieval of commodity master lists from USDA and WITS.
- Standardize product codes across different trade databases.
- Create logical groupings for agricultural products to support sector-level analysis.

## Script Descriptions

| File | Source | Method |
| :--- | :--- | :--- |
| `fetch_fas_commodities.py` | USDA FAS | API (JSON) |
| `fetch_wits_commodities.py` | WITS / World Bank | API (JSON) |
| `process_fas_commodity_groups.py` | USDA / Local | Pandas (Data Mapping) |

## Usage
These scripts provide the necessary lookup tables to ensure that trade flows (Imports/Exports) are correctly attributed to the right agricultural products and commodity groups.