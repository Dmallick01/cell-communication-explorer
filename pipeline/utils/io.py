from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str))


def load_metadata(path: str | None) -> pd.DataFrame | None:
    if not path:
        return None
    p = Path(path)
    if p.suffix.lower() in {".csv", ".tsv", ".txt"}:
        sep = "\t" if p.suffix.lower() == ".tsv" else ","
        return pd.read_csv(p, sep=sep, index_col=0)
    return None
