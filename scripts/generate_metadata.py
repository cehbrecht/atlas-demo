#!/usr/bin/env python3
"""
Generate STAC-compatible sidecar JSONs for available NetCDF files.
Includes global attributes. Skips missing or unopenable files.
Compatible with DataLad.
"""

import os
import json
from pathlib import Path
import xarray as xr
import warnings
import numpy as np

# Suppress xarray fill-value warnings
warnings.filterwarnings("ignore", category=xr.SerializationWarning)

DATA_DIR = Path("atlas/data")
META_DIR = Path("atlas/metadata")
META_DIR.mkdir(exist_ok=True, parents=True)

# Find all NetCDF files recursively
nc_files = list(DATA_DIR.rglob("*.nc"))

# Only process files that exist locally
existing_files = [f for f in nc_files if f.exists()]

if not existing_files:
    print("No NetCDF files found locally. Skipping metadata generation.")
    exit(0)

def convert_recursive(obj):
    """Recursively convert NumPy types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_recursive(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

for nc_file in existing_files:
    print(f"Generating metadata sidecar for {nc_file.name}...")

    try:
        ds = xr.open_dataset(nc_file)
    except FileNotFoundError:
        print(f"Skipping {nc_file}: file not found locally.")
        continue
    except OSError as e:
        print(f"Skipping {nc_file}: cannot open file ({e}).")
        continue

    # Base metadata
    metadata = {
        "title": nc_file.stem,
        "variables": list(ds.data_vars),
        "dimensions": dict(ds.sizes),
        "bbox": None,
        "time_range": None,
        "attributes": dict(ds.attrs),  # global attributes
        "assets": {}
    }

    # Preserve subfolder structure for DataLad
    relative_path = nc_file.relative_to(DATA_DIR)
    metadata["assets"]["datalad"] = str(DATA_DIR / relative_path)

    # Bounding box if lon/lat exist
    if "lon" in ds and "lat" in ds:
        try:
            metadata["bbox"] = [
                float(ds.lon.min()), float(ds.lat.min()),
                float(ds.lon.max()), float(ds.lat.max())
            ]
        except Exception:
            pass

    # Time range if time exists
    if "time" in ds:
        try:
            metadata["time_range"] = [
                str(ds.time.min().values),
                str(ds.time.max().values)
            ]
        except Exception:
            pass

    ds.close()

    # Convert all NumPy types before writing JSON
    metadata_clean = convert_recursive(metadata)

    # Write sidecar JSON, preserving subfolders
    out_file = META_DIR / relative_path.parent / f"{nc_file.stem}.stac.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(metadata_clean, f, indent=2)

    print(f"Saved sidecar: {out_file}")
