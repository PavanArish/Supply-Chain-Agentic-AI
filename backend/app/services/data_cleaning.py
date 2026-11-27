"""
Data Validation & Cleaning step of the Input Processor.
Keeps things conservative: drop fully-empty rows/columns, strip whitespace
from string columns, coerce obvious numeric/date columns, and report what
was done so it's transparent to the user.
"""
import pandas as pd
from typing import Dict, List, Tuple


def clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    notes: List[str] = []
    original_rows = len(df)

    # Drop fully empty rows/columns
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")
    if len(df) != original_rows:
        notes.append(f"Dropped {original_rows - len(df)} fully-empty row(s).")

    # Strip whitespace from string/object columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip().replace({"nan": None, "None": None, "": None})

    # Drop exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    if len(df) != before:
        notes.append(f"Removed {before - len(df)} duplicate row(s).")

    df = df.reset_index(drop=True)
    return df, notes


def profile_dataframe(df: pd.DataFrame) -> Dict:
    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
        "missing": {c: int(df[c].isna().sum()) for c in df.columns},
    }
