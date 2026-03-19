# Geography and Distance Data Automation

This submodule automates the retrieval of geographic variables used in gravity model estimation, with a primary focus on bilateral distance data.

## Research Context

Geographic variables are central to the Gravity Model of International Trade because they represent **trade resistance**. Distance is commonly used as a proxy for transportation costs, logistical complexity, and other frictions that affect trade between countries.

In agricultural trade analysis, longer distances often increase shipping and handling costs, reduce competitiveness, and influence market access. Geographic indicators therefore play an essential role in explaining the structure and intensity of U.S. agricultural exports.

## Data Source

- **CEPII GeoDist Database**
  - A widely used international dataset providing bilateral distance measures and related geographic indicators for empirical trade research.

## Files

| File | Description |
| :--- | :--- |
| `fetch_cepii_distance.py` | Downloads and prepares CEPII bilateral distance data for integration into gravity model datasets. |

## Usage

Run the script in this folder to retrieve geographic distance data for bilateral trade modeling.

## Output Purpose

The resulting dataset is intended to support:
- gravity-model estimation,
- transport-cost approximation,
- bilateral trade resistance measurement,
- and scenario-based trade analysis involving geographic frictions.