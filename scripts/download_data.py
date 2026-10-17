"""Download the two open T1D datasets (both CC BY 4.0) into data/raw/."""
from __future__ import annotations

import io
import os
import zipfile

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
HUPA_DATASET = "3hbcscwz44"
HUPA_PREPROCESSED_FOLDER = "c89e0831-7d0a-4fbb-9cb2-04e41161513c"
UOM_ZIP = ("https://zenodo.org/api/records/15806142/files/"
           "sharpic/ManchesterCSCoordinatedDiabetesStudy-V1.0.3.zip/content")


def hupa():
    out = os.path.join(RAW, "hupa_ucm")
    os.makedirs(out, exist_ok=True)
    files = requests.get(f"https://data.mendeley.com/public-api/datasets/{HUPA_DATASET}/files",
                         params={"folder_id": HUPA_PREPROCESSED_FOLDER, "version": 1}, timeout=60).json()
    for f in files:
        path = os.path.join(out, f["filename"])
        if os.path.exists(path) and os.path.getsize(path) == f.get("size"):
            continue
        r = requests.get(f["content_details"]["download_url"], timeout=300)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
        print("HUPA-UCM", f["filename"])


def uom():
    out = os.path.join(RAW, "t1d_uom")
    os.makedirs(out, exist_ok=True)
    r = requests.get(UOM_ZIP, timeout=300)
    r.raise_for_status()
    zipfile.ZipFile(io.BytesIO(r.content)).extractall(out)
    print("T1D-UOM extracted")


if __name__ == "__main__":
    hupa()
    uom()
