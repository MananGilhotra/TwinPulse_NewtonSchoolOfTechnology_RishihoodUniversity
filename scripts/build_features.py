"""Build the unified 5-minute tables and the nightly / real-time feature tables from data/raw/."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from twinpulse.data import PROCESSED, load_all  # noqa: E402
from twinpulse.features import nightly_table, realtime_table  # noqa: E402


def main():
    df = load_all(cache=False)
    nights = nightly_table(df)
    nights.to_parquet(os.path.join(PROCESSED, "nights.parquet"))
    rt = realtime_table(df)
    rt.to_parquet(os.path.join(PROCESSED, "realtime.parquet"))
    print(f"{df.patient.nunique()} patients, {len(nights)} nights, {len(rt)} real-time rows")


if __name__ == "__main__":
    main()
