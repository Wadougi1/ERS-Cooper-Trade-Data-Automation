"""
Module:      process_wto_rta_data.py
Project:     ERS Cooper Trade Data Automation
Description: Provides post-processing utilities for the WTO AllRTAs dataset.
             Transforms the 'Original signatories' column into structured
             analytical formats:
               1. expand_signatories_column()           — wide format (one column per country).
               2. transpose_agreement_countries()        — long format (one row per country).
               3. generate_signatory_pairs()             — unique unordered country pairs.
               4. generate_bidirectional_signatory_pairs()— all ordered directional pairs.
             Input files are expected in the 'downloads' directory by default.
Author:      Douglas Akwasi Kwarteng
Date:        2025
"""

import logging
import os
from itertools import combinations, permutations

import pandas as pd

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DOWNLOAD_DIR    = os.path.join(os.getcwd(), "downloads")
DEFAULT_SOURCE  = os.path.join(DOWNLOAD_DIR, "WTO_AllRTAs.xlsx")
SIGNATORIES_COL = "Original signatories"

# Metadata columns to carry through pairwise outputs
RTA_META_COLS = [
    "RTA Name",
    "Coverage",
    "Type",
    "Date of notification",
    "Notification",
    "Date of entry into force",
    "Status",
    "Remarks",
]


# ---------------------------------------------------------------------------
# Helper: Load and validate source Excel file
# ---------------------------------------------------------------------------
def _load_source(source_file: str, required_col: str | None = None) -> pd.DataFrame:
    """
    Loads an Excel file and optionally validates the presence of a required
    column.

    Args:
        source_file  (str):        Full path to the input Excel file.
        required_col (str | None): Column name that must exist in the file.

    Returns:
        pd.DataFrame: Loaded DataFrame.

    Raises:
        FileNotFoundError: If the source file does not exist.
        KeyError:          If the required column is missing.
    """
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"Source file not found: '{source_file}'")

    df = pd.read_excel(source_file)

    if required_col and required_col not in df.columns:
        raise KeyError(f"Required column '{required_col}' not found in '{source_file}'.")

    return df


# ---------------------------------------------------------------------------
# 1. Expand Signatories into Wide Format
# ---------------------------------------------------------------------------
def expand_signatories_column(
    source_file: str = DEFAULT_SOURCE,
    output_file: str = os.path.join(DOWNLOAD_DIR, "AgreementsList_Expanded.xlsx"),
) -> pd.DataFrame | None:
    """
    Splits the 'Original signatories' column (semicolon-delimited) into
    individual 'Country1', 'Country2', ... columns (wide format).

    Args:
        source_file (str): Path to the input Excel file.
        output_file (str): Path to save the expanded Excel file.

    Returns:
        pd.DataFrame | None: Expanded DataFrame on success, None on failure.
    """
    try:
        logger.info(f"[*] Loading data from '{source_file}' ...")
        data = _load_source(source_file, required_col=SIGNATORIES_COL)

        logger.info("[*] Splitting 'Original signatories' into wide-format columns ...")
        countries_split = data[SIGNATORIES_COL].str.split(";", expand=True)
        countries_split.columns = [f"Country{i + 1}" for i in range(countries_split.shape[1])]

        expanded_df = pd.concat(
            [data.drop(columns=[SIGNATORIES_COL]), countries_split], axis=1
        )

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        expanded_df.to_excel(output_file, index=False)
        logger.info(f"[+] Expanded data saved to '{output_file}' ({len(expanded_df):,} rows).")
        return expanded_df

    except (FileNotFoundError, KeyError) as e:
        logger.error(f"[!] {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error in expand_signatories_column: {e}")

    return None


# ---------------------------------------------------------------------------
# 2. Transpose Countries into Long Format
# ---------------------------------------------------------------------------
def transpose_agreement_countries(
    source_file: str = os.path.join(DOWNLOAD_DIR, "AgreementsList_Expanded.xlsx"),
    output_file: str = os.path.join(DOWNLOAD_DIR, "AgreementsList_Transposed.xlsx"),
) -> pd.DataFrame | None:
    """
    Transposes wide-format 'CountryX' columns into a single long-format
    'Country' column, with one row per country per agreement.

    Also adds an 'N_of_Countries' column indicating the country's
    position in the original signatory list.

    Args:
        source_file (str): Path to the expanded (wide-format) Excel file.
        output_file (str): Path to save the transposed Excel file.

    Returns:
        pd.DataFrame | None: Transposed DataFrame on success, None on failure.
    """
    try:
        logger.info(f"[*] Loading data from '{source_file}' ...")
        data = _load_source(source_file)

        country_cols = [col for col in data.columns if col.startswith("Country")]
        if not country_cols:
            raise ValueError("No 'CountryX' columns found in the dataset.")

        logger.info("[*] Transposing country columns into long format ...")
        transposed_rows = []

        for _, row in data.iterrows():
            base = row.drop(labels=country_cols).to_dict()
            for idx, col in enumerate(country_cols, start=1):
                country = row[col]
                if pd.notna(country) and str(country).strip():
                    new_row = base.copy()
                    new_row["Country"]       = str(country).strip()
                    new_row["N_of_Countries"] = idx
                    transposed_rows.append(new_row)

        final_df = pd.DataFrame(transposed_rows)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        final_df.to_excel(output_file, index=False)
        logger.info(f"[+] Transposed data saved to '{output_file}' ({len(final_df):,} rows).")
        return final_df

    except (FileNotFoundError, ValueError) as e:
        logger.error(f"[!] {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error in transpose_agreement_countries: {e}")

    return None


# ---------------------------------------------------------------------------
# 3. Generate Unique Unordered Country Pairs
# ---------------------------------------------------------------------------
def generate_signatory_pairs(
    source_file: str = DEFAULT_SOURCE,
    output_file: str = os.path.join(DOWNLOAD_DIR, "paired_signatories.xlsx"),
) -> pd.DataFrame | None:
    """
    Generates all unique unordered country pairs (combinations) from the
    'Original signatories' column, preserving agreement metadata.

    For an agreement with N signatories, this produces C(N, 2) pairs.

    Args:
        source_file (str): Path to the input Excel file.
        output_file (str): Path to save the paired signatories Excel file.

    Returns:
        pd.DataFrame | None: Pairs DataFrame on success, None on failure.
    """
    try:
        logger.info(f"[*] Loading data from '{source_file}' ...")
        data = _load_source(source_file, required_col=SIGNATORIES_COL)

        logger.info("[*] Generating unordered signatory pairs ...")

        def _make_pairs(row: pd.Series) -> pd.DataFrame:
            countries = [c.strip() for c in str(row[SIGNATORIES_COL]).split(";") if c.strip()]
            pairs     = list(combinations(countries, 2))
            meta      = {col: row.get(col) for col in RTA_META_COLS if col in data.columns}
            return pd.DataFrame({
                "Country1": [p[0] for p in pairs],
                "Country2": [p[1] for p in pairs],
                **meta,
            })

        pairs_df = pd.concat(
            [_make_pairs(row) for _, row in data.iterrows()],
            ignore_index=True,
        )

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        pairs_df.to_excel(output_file, index=False)
        logger.info(f"[+] Signatory pairs saved to '{output_file}' ({len(pairs_df):,} pairs).")
        return pairs_df

    except (FileNotFoundError, KeyError) as e:
        logger.error(f"[!] {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error in generate_signatory_pairs: {e}")

    return None


# ---------------------------------------------------------------------------
# 4. Generate All Directional (Bidirectional) Country Pairs
# ---------------------------------------------------------------------------
def generate_bidirectional_signatory_pairs(
    source_file: str = DEFAULT_SOURCE,
    output_file: str = os.path.join(DOWNLOAD_DIR, "paired_signatories_bothdirection.xlsx"),
) -> pd.DataFrame | None:
    """
    Generates all ordered directional country pairs (permutations) from the
    'Original signatories' column, preserving agreement metadata.

    For an agreement with N signatories, this produces P(N, 2) = N*(N-1) pairs,
    capturing both (A → B) and (B → A) directions.

    Args:
        source_file (str): Path to the input Excel file.
        output_file (str): Path to save the bidirectional pairs Excel file.

    Returns:
        pd.DataFrame | None: Bidirectional pairs DataFrame on success, None on failure.
    """
    try:
        logger.info(f"[*] Loading data from '{source_file}' ...")
        data = _load_source(source_file, required_col=SIGNATORIES_COL)

        logger.info("[*] Generating all directional signatory pairs ...")

        def _make_permutations(row: pd.Series) -> pd.DataFrame:
            countries = [c.strip() for c in str(row[SIGNATORIES_COL]).split(";") if c.strip()]
            pairs     = list(permutations(countries, 2))
            meta      = {col: row.get(col) for col in RTA_META_COLS if col in data.columns}
            return pd.DataFrame({
                "Country1": [p[0] for p in pairs],
                "Country2": [p[1] for p in pairs],
                **meta,
            })

        pairs_df = pd.concat(
            [_make_permutations(row) for _, row in data.iterrows()],
            ignore_index=True,
        )

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        pairs_df.to_excel(output_file, index=False)
        logger.info(
            f"[+] Bidirectional pairs saved to '{output_file}' ({len(pairs_df):,} pairs)."
        )
        return pairs_df

    except (FileNotFoundError, KeyError) as e:
        logger.error(f"[!] {e}")
    except Exception as e:
        logger.error(f"[!] Unexpected error in generate_bidirectional_signatory_pairs: {e}")

    return None


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Step 1: Expand signatories into wide format
    expand_signatories_column()

    # Step 2: Transpose wide format into long format
    transpose_agreement_countries()

    # Step 3: Generate unique unordered pairs
    generate_signatory_pairs()

    # Step 4: Generate all directional pairs
    generate_bidirectional_signatory_pairs()
