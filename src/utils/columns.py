# src/utils/columns.py
import unicodedata
import logging
from typing import Iterable, Optional

logger = logging.getLogger(__name__)

def _normalize_col_name(s: str) -> str:
    """Normalize a column name: remove accents, uppercase and collapse non-alnum to spaces."""
    if s is None:
        return ""
    s = str(s)
    nfkd = unicodedata.normalize("NFKD", s)
    no_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    # keep alnum and underscore, replace other chars by space
    cleaned = "".join(ch if (ch.isalnum() or ch == "_") else " " for ch in no_accents)
    cleaned = " ".join(cleaned.split())  # collapse spaces
    return cleaned.upper()

def find_column(df, *candidates: Iterable[str]) -> Optional[str]:
    """
    Return the actual column name in df that matches any of the candidates.
    Matching is case-insensitive, accent-insensitive and ignores punctuation/spaces.
    Returns the first matched original column name, or None if not found.
    """
    if df is None:
        return None

    norm_map = { _normalize_col_name(col): col for col in df.columns }
    norm_candidates = [_normalize_col_name(c) for c in candidates if c]

    # exact matches by candidate order
    for nc in norm_candidates:
        if nc in norm_map:
            return norm_map[nc]

    # substring heuristics
    for nc in norm_candidates:
        for norm_col, orig in norm_map.items():
            if nc in norm_col or norm_col in nc:
                return orig

    return None

def find_column_values(df, candidates, default=None):
    """
    Return list with values from the first found candidate column.
    If none found returns default (or empty list).
    """
    col = find_column(df, *candidates)
    if col is None:
        logger.debug("find_column_values: no column found for candidates=%s, available=%s", candidates, list(df.columns))
        return default if default is not None else []
    return df[col].tolist()
