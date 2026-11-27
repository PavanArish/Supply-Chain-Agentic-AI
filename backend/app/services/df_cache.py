"""
Small in-process cache so we don't re-read/re-clean the file from disk on
every query for the same dataset within a server's lifetime. Falls back to
reading from disk (stored_path) on a cache miss (e.g. after server restart).
"""
import pandas as pd
from typing import Dict

_cache: Dict[int, pd.DataFrame] = {}


def set_df(dataset_id: int, df: pd.DataFrame) -> None:
    _cache[dataset_id] = df


def get_df(dataset_id: int):
    return _cache.get(dataset_id)


def load_from_disk(stored_path: str, file_type: str) -> pd.DataFrame:
    if file_type == "csv":
        return pd.read_csv(stored_path)
    return pd.read_excel(stored_path)


def get_or_load(dataset_id: int, stored_path: str, file_type: str) -> pd.DataFrame:
    df = get_df(dataset_id)
    if df is None:
        df = load_from_disk(stored_path, file_type)
        set_df(dataset_id, df)
    return df
