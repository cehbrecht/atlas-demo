#!/usr/bin/env python3
"""
Run compliance checks (currently CF) on locally available NetCDF files.
Generates plain-text reports in atlas/checks/, preserving subfolder structure.
Skips files that are not present (DataLad safe).
"""

import subprocess
from pathlib import Path

DATA_DIR = Path("atlas/data")
REPORT_DIR = Path("atlas/checks")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Find all NetCDF files that exist locally
nc_files = [f for f in DATA_DIR.rglob("*.nc") if f.exists()]

if not nc_files:
    print("No local NetCDF files found. Skipping checks.")
    exit(0)

print(f"Running compliance checks on {len(nc_files)} NetCDF file(s)...")

for nc_file in nc_files:
    # Preserve subfolder structure under atlas/checks
    relative_path = nc_file.relative_to(DATA_DIR)
    out_file = REPORT_DIR / relative_path.parent / f"{relative_path.stem}_check.txt"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"→ Checking {nc_file} ...")

    cmd = [
        "compliance-checker",
        "-f", "text",
        "-o", str(out_file),
        "-t", "cf",
        str(nc_file),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Check failed for {nc_file}: {e}")
    else:
        print(f"✓ Report saved: {out_file}")
