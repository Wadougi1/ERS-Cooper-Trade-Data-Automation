# ERS Cooper Trade Data Automation

A comprehensive data automation and harmonization pipeline developed to support empirical and scenario-based analysis of how **Free Trade Agreements (FTAs)** and **tariff changes** influence **U.S. agricultural exports**.

This project was developed as part of a research effort connected to an **ERS/USDA cooperative research project** and later refined to support a graduate thesis on the impact of FTAs on U.S. agricultural trade. The work integrates international trade, macroeconomic, and policy datasets from multiple global sources into a structured and reusable research workflow.

## Project Overview

The purpose of this repository is to automate the collection, cleaning, standardization, and merging of country-level trade reference data from multiple international sources. These automated scripts reduce manual data handling, improve reproducibility, and create a reliable input pipeline for downstream trade and policy analysis.

The project supports a broader analytical framework used to:
- quantify the impact of U.S. Free Trade Agreements on U.S. agricultural exports,
- evaluate how tariff changes influence export performance,
- integrate macroeconomic, trade, and policy variables into a unified dataset,
- support gravity-model estimation and tariff scenario analysis.

## Research Background

The original research proposal focused on **quantifying trade creation and trade diversion due to Free Trade Agreements**, with particular attention to U.S. FTAs and their effect on agricultural commodities.

As the research developed, the final project evolved into a broader and more applied framework centered on:
- **automated trade-data integration**,
- **FTA and tariff impact analysis**,
- **scenario-based modeling of U.S. agricultural exports**.

The final thesis framework examined how trade agreements, tariffs, distance, GDP, exchange rates, and other trade-related factors shape export outcomes. In addition to supporting empirical estimation, the automation pipeline created a repeatable process for integrating data from diverse international institutions.

## Key Objectives

- Build an automated framework for collecting country and trade reference data from multiple international sources.
- Standardize country names and ISO codes across inconsistent datasets.
- Reduce manual data collection errors in international trade research.
- Produce harmonized outputs that can be used in econometric and scenario analysis workflows.
- Support the analysis of how FTAs and tariff changes affect U.S. agricultural exports.

## Data Sources

The automation workflow uses data from multiple sources, including:
- **UN Comtrade**
- **USDA Foreign Agricultural Service (FAS)**
- **USDA Production, Supply and Distribution (PSD)**
- **World Bank**
- **WITS (World Integrated Trade Solution)**
- **IMF DataMapper**
- **FAO / FishBase**
- **U.S. Census Bureau**
- **CEPII GeoDist Database**
- **WTO RTA Database**

## Repository Structure

```text
ERS-Cooper-Trade-Data-Automation/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── 01_country_reference/
│   ├── README.md
│   ├── config.py
│   ├── fetch_un_comtrade.py
│   ├── fetch_fas_psd.py
│   ├── fetch_worldbank_wits.py
│   ├── fetch_imf_reporters.py
│   ├── fetch_fao_census.py
│   └── merge_country_datasets.py
│
├── 02_trade_flows/
│   ├── README.md
│   ├── fetch_wits_imports.py
│   ├── fetch_wits_exports.py
│   ├── fetch_wto_trade_data.py
│   ├── fetch_fas_agricultural_exports.py
│   ├── fetch_fas_gats_exports.py
│   ├── fetch_worldbank_agriexports.py
│   ├── fetch_worldbank_agrimports.py
│   └── fetch_trademap_exports.py
│
├── 03_commodities/
│   ├── README.md
│   ├── fetch_fas_commodities.py
│   ├── fetch_wits_commodities.py
│   └── process_fas_commodity_groups.py
│
├── 04_gravity_variables/
│   ├── README.md
│   ├── gdp/
│   ├── exchange_rate/
│   ├── population/
│   └── geography/
│
└── 05_trade_policy/
    ├── README.md
    ├── tariffs/
    └── trade_agreements/
```
## Module Descriptions

| File | Description |
|---|---|
| `config.py` | Central configuration file for API keys, environment variables, and global settings such as timeouts. |
| `fetch_un_comtrade.py` | Extracts and cleans M49-based country reference data from the UN Comtrade source. |
| `fetch_fas_psd.py` | Connects to USDA FAS and PSD APIs to retrieve and standardize country reference data. |
| `fetch_worldbank_wits.py` | Processes World Bank JSON responses and WITS XML data for country-level integration. |
| `fetch_imf_reporters.py` | Retrieves country data from IMF DataMapper and UN Comtrade reporters reference files. |
| `fetch_fao_census.py` | Uses headless Selenium automation to scrape country data from FAO FishBase and the U.S. Census Bureau. |
| `merge_country_datasets.py` | Merges all generated outputs into a harmonized country reference dataset and Excel export. |

#### Workflow Summary

The automation workflow follows these general steps:

1. Collect country reference data from APIs, websites, and structured online sources.
2. Clean the extracted data by selecting relevant fields and standardizing variable names.
3. Normalize ISO country codes and naming conventions across datasets.
4. Merge the cleaned source files into a unified harmonized dataset.
5. Export final outputs for use in downstream trade, econometric, and scenario analysis.

### Professional Features

This repository was designed to reflect a professional and research-oriented data engineering workflow.

### Highlights
- Modular script design for maintainability and clarity
- Environment-based configuration for secure API key handling
- Error handling to prevent source-specific failures from breaking the entire pipeline
- Headless browser automation for websites that do not offer direct APIs
- Data harmonization logic to reconcile inconsistent country naming conventions
- Reusable outputs suitable for econometric modeling and policy analysis

### Installation

Install the required dependencies with:

#### pip install -r requirements.txt


If you do not yet have a requirements.txt, the main dependencies used in this project include:

#### pip install requests pandas selenium tabulate lxml openpyxl

### Configuration

Some scripts require an API key for USDA FAS/PSD access.

#### Set the API key as an environment variable:

#### export FAS_API_KEY="your_key_here"


On Windows PowerShell:

#### $env:FAS_API_KEY="your_key_here"


The scripts are designed to read this key through the configuration module.

## How to Run

You can run each fetcher individually to update specific sources, then run the merge script to create the final harmonized output.

Examples: 

| Step | Command | Purpose |
|---|---|---|
| 1 | `python 01_country_reference/fetch_un_comtrade.py` | Fetches and prepares UN Comtrade country reference data. |
| 2 | `python 01_country_reference/fetch_fas_psd.py` | Retrieves and standardizes USDA FAS and PSD country reference data. |
| 3 | `python 01_country_reference/fetch_worldbank_wits.py` | Processes World Bank and WITS country-level reference data. |
| 4 | `python 01_country_reference/fetch_imf_reporters.py` | Retrieves country data from IMF DataMapper and UN Comtrade reporter references. |
| 5 | `python 01_country_reference/fetch_fao_census.py` | Scrapes and prepares country data from FAO FishBase and the U.S. Census Bureau. |
| 6 | `python 01_country_reference/merge_country_datasets.py` | Merges all cleaned source outputs into the final harmonized dataset. |

### Outputs

Typical outputs generated by this workflow include:

- cleaned country reference CSV files
- harmonized merged datasets
- Excel exports for research use
- standardized ISO-based lookup tables for downstream analysis

These outputs are intended to support broader trade research workflows involving:

- gravity-model estimation
- tariff scenario analysis
- FTA impact evaluation
- agricultural export analysis

### Research Relevance

This repository contributes to research on international trade policy by creating a reproducible data preparation workflow for studying the relationship between:

- Free Trade Agreements
- tariffs
- macroeconomic conditions
- U.S. agricultural export performance

The automation pipeline improves research efficiency and helps reduce errors associated with manual international dataset collection and integration.

### Thesis Connection

This repository supports a larger research project titled:

Quantifying the Impact of Free Trade Agreements on U.S. Agriculture Exports: A Data-Driven Scenario Analysis

The final analytical framework emphasized:

- the positive role of FTAs in promoting exports
- the negative effect of tariffs and distance on trade flows
- the importance of automated data integration for reliable research outputs

### Future Improvements

Potential next steps for the repository include:

- adding automated logging with Python’s logging module
- converting output generation into a configurable pipeline
- adding unit tests for data validation
- building commodity-level modules for imports, exports, tariffs, GDP, and exchange rates
- integrating notebook-based or dashboard-based result visualization

### Author

Douglas Akwasi Kwarteng<br>
Graduate Researcher | Cybersecurity & Data Automation<br>
Master’s Research in Agribusiness, International Trade, and 
Applied Data Analysis

### License

This repository is intended for academic, research, and professional portfolio purposes unless otherwise specified.
