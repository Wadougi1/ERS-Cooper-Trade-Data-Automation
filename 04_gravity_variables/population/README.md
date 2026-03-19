# Population Data Automation

This submodule automates the retrieval and harmonization of population data used in gravity model estimation and international trade analysis.

## Research Context

Population is an important explanatory variable in gravity models because it serves as a proxy for **market size**, **labor force availability**, and **domestic demand potential**. In the context of U.S. agricultural trade, population data helps explain the scale of consumption opportunities in partner countries and the size of exporting or importing markets.

By collecting population data from multiple authoritative sources, this submodule supports cross-validation and improves the reliability of downstream econometric analysis.

## Data Sources

- **World Bank**
  - Provides annual total population estimates for most countries.
- **IMF / U.S. Census Bureau**
  - Supports additional validation and reference checks for country-level population data.

## Files

| File | Description |
| :--- | :--- |
| `fetch_worldbank_population.py` | Fetches total population data from the World Bank API. |
| `fetch_imf_census_population.py` | Retrieves and reconciles population-related data from IMF and U.S. Census sources. |

## Usage

Run the scripts in this folder to generate harmonized population reference data for use in gravity model estimation and broader trade analysis workflows.

## Output Purpose

The resulting datasets are intended to support:
- gravity-model estimation,
- market-size comparisons across countries,
- country-level macroeconomic integration,
- and international trade scenario analysis.