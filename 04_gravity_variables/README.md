# Gravity Model Variables Automation

This module automates the collection and harmonization of the independent variables required to estimate a **Gravity Model of International Trade**. 

## Research Context

In international economics, the Gravity Model predicts that the volume of trade between two countries is determined by their economic "mass" (GDP and Population) and the "resistance" to trade (Geographic Distance, Exchange Rates, and Policy Barriers). 

This automation pipeline specifically collects:
- **Economic Mass:** GDP and Population data from the IMF, World Bank, and UN to represent the market size of the U.S. and its trading partners.
- **Trade Resistance (Geography):** Bilateral distance, contiguity (shared borders), and common language data from CEPII to model transport costs and cultural proximity.
- **Macroeconomic Stability:** Exchange rate data to account for currency fluctuations that influence the competitiveness of U.S. agricultural exports.

By automating these sources, the project ensures that the gravity model estimation is based on the most recent and harmonized macroeconomic indicators available.

## Module Structure

The variables are organized into submodules based on their economic function:

| Subfolder | Variable | Sources |
| :--- | :--- | :--- |
| `gdp/` | Gross Domestic Product | IMF, World Bank, UN, WITS |
| `exchange_rate/` | Currency Exchange Rates | IMF, World Bank |
| `population/` | Total Population | World Bank, IMF, US Census |
| `geography/` | Distance & Contiguity | CEPII |

## Script Descriptions

### GDP Submodule
- `fetch_imf_gdp.py`: Retrieves current and historical GDP data from the IMF DataMapper API.
- `fetch_worldbank_gdp.py`: Extracts GDP (current US$) indicators from the World Bank API.
- `fetch_un_gdp.py`: Collects official UN national accounts data.
- `fetch_wits_gdp.py`: Integrates WITS-specific GDP reference data.

### Exchange Rate Submodule
- `fetch_imf_exchange_rate.py`: Automates the retrieval of official exchange rate series from the IMF.
- `fetch_worldbank_exchange_rate.py`: Collects annual exchange rate data from the World Bank.

### Population Submodule
- `fetch_worldbank_population.py`: Fetches total population counts for all trading partners.
- `fetch_imf_census_population.py`: Cross-references IMF and U.S. Census Bureau population estimates.

### Geography Submodule
- `fetch_cepii_distance.py`: Uses Selenium to download and extract the CEPII GeoDist dataset, providing bilateral distances between major cities and weighted distances.

## Usage
These scripts provide the foundational data for the gravity model's independent variables. Run the scripts within each subfolder to generate the harmonized datasets required for econometric analysis.