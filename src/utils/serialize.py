# src/utils/serialize.py
import pandas as pd
import numpy as np
from datetime import datetime, date

def df_to_safe_records(df: pd.DataFrame):
    """
    Converte um pandas DataFrame para uma lista de dicts segura para jsonify/JSON:
    - substitui NaN/NaT por None (-> null no JSON)
    - converte numpy scalars para tipos nativos Python
    - formata pd.Timestamp/datetime/date para strings ISO
    - retorna [] para None ou df vazio
    """
    if df is None or df.empty:
        return []

    # cópia defensiva
    df2 = df.copy()

    # substituir NaN/NaT por None
    df2 = df2.where(pd.notnull(df2), None)

    records = []
    for row in df2.to_dict("records"):
        r = {}
        for k, v in row.items():
            if v is None:
                r[k] = None
                continue

            # numpy integer/float/bool -> python nativos
            if isinstance(v, (np.integer,)):
                r[k] = int(v)
            elif isinstance(v, (np.floating,)):
                r[k] = float(v)
            elif isinstance(v, (np.bool_,)):
                r[k] = bool(v)
            # pandas Timestamp or datetime -> ISO string
            elif isinstance(v, (pd.Timestamp, datetime)):
                try:
                    r[k] = v.isoformat()
                except Exception:
                    r[k] = str(v)
            elif isinstance(v, date):
                r[k] = v.isoformat()
            else:
                # se for numpy scalar com .item()
                try:
                    if hasattr(v, "item"):
                        r[k] = v.item()
                    else:
                        r[k] = v
                except Exception:
                    r[k] = str(v)
        records.append(r)
    return records
