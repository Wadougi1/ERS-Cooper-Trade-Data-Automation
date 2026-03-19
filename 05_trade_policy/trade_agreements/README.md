## Files

| File | Description |
| :--- | :--- |
| `fetch_wto_trade_agreements.py` | Downloads the full WTO RTA database. |
| `fetch_pairwise_trade_agreements.py` | Generates bilateral (pairwise) agreement indicators for gravity model estimation. |
| `process_wto_rta_data.py` | Cleans and filters RTA data for research-specific analysis. |

## Research Importance
The **pairwise** script is essential for gravity modeling as it creates the binary indicator (0 or 1) for whether a trade agreement exists between a specific exporter and importer pair.