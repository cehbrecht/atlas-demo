# Atlas Demo

[![License](https://img.shields.io/github/license/cehbrecht/atlas-demo)](LICENSE)
![Python](https://img.shields.io/badge/python-≥3.10-blue)
![Conda](https://img.shields.io/badge/environment-conda--forge-green)
[![Build](https://github.com/cehbrecht/atlas-demo/actions/workflows/update_catalog.yml/badge.svg)](https://github.com/cehbrecht/atlas-demo/actions/workflows/update_catalog.yml)
[![STAC Browser](https://img.shields.io/badge/STAC-Browser-green)](https://radiantearth.github.io/stac-browser/#/external/https://raw.githubusercontent.com/cehbrecht/atlas-demo/main/catalogs/stac/catalog.json)
![DataLad](https://img.shields.io/badge/managed%20by-DataLad-orange)
[![DOI](https://zenodo.org/badge/DOI/10.5072/zenodo.0000000.svg)](https://zenodo.org/record/0000000)

---

## Overview

This repository demonstrates how to manage climate Atlas NetCDF data using:

- **DataLad** for version control and lightweight data management  
- **CF/IOOS compliance checks** for metadata validation  
- **STAC catalogs** for structured metadata and discovery  

All workflows are reproducible locally and run automatically on GitHub Actions when metadata updates are detected.

> The Zenodo badge above is for showcase purposes.  
> When you create a release and link the GitHub repository to Zenodo, a DOI will be automatically minted for each version.

---

## 🧰 Prepare Your System

Before running the workflow, ensure you have **DataLad** and **git-annex** installed.

👉 See the **[DataLad Handbook – Installation Guide](https://handbook.datalad.org/en/latest/intro/installation.html)** for detailed instructions and platform-specific notes.

### macOS

```bash
# Using Homebrew (recommended)
brew install datalad git-annex

# Verify installation
datalad --version
git annex version
```

> Alternatively, use Conda:
> ```bash
> conda install -c conda-forge datalad git-annex
> ```

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install datalad git-annex
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install datalad git-annex
```

Once installed, clone the dataset and you’re ready to go.

---

## Getting Started

### 1. Clone the repository/dataset

```bash
datalad clone https://github.com/cehbrecht/atlas-demo.git
cd atlas-demo
```

### 2. Create and activate Conda environment

```bash
conda env create -f environment.yml
conda activate atlas-demo
```

> Optional: install DataLad via Conda if not installed system-wide  
> ```bash
> conda install -c conda-forge datalad git-annex
> ```

---

## Adding and Managing Data

The file **`atlas/atlas_urls.csv`** lists available datasets from an **external data source**.  
Each row defines a *remote URL* and a *local storage path* inside `atlas/data/`.

Example snippet:

```csv
url,path
https://data.example.org/cmip6/cd_CMIP6_ssp126_yr_2015-2100_v02.nc,atlas/data/v02/CMIP6/ssp126/cd_CMIP6_ssp126_yr_2015-2100_v02.nc
https://data.example.org/cerra/cd_CERRA_yr_1985-2021_v02.nc,atlas/data/v02/CERRA/cd_CERRA_yr_1985-2021_v02.nc
```

To register these datasets in your local DataLad dataset (without downloading the actual files):

```bash
make addurls
```

This creates lightweight references in `atlas/data/` that can be retrieved later on demand:

```bash
datalad get atlas/data/<file>.nc
```

---

## Adding New Local Data

To add NetCDF files that are already available locally:

1. Copy the files into the appropriate folder under `atlas/data/`.
2. Extract metadata and validate the files by running the workflow:

```bash
make update
```

Or step-by-step:

```bash
make metadata    # extract STAC metadata for all available NetCDF files
make checks      # run CF/IOOS compliance checks
make catalogs    # generate STAC catalog
```

3. Save the new files and generated metadata to DataLad:

```bash
datalad save -m "Add new NetCDF data and metadata"
```

4. Push your changes to GitHub:

```bash
git push
```

> **Note:** Only STAC catalogs are rebuilt automatically on GitHub via Actions.  
> Metadata extraction and CF checks must be run locally before committing.

---

## Cleaning Generated Files

To remove generated metadata and catalogs:

```bash
make clean
```

---

## GitHub Actions Workflow

- Runs automatically on push or pull request affecting `atlas/metadata/**`
- Builds and commits updated STAC catalogs under `catalogs/stac/`
- Skips execution if no metadata changes are detected

---

## DataLad Resources

- **[Official Handbook](https://handbook.datalad.org/en/latest/)** – complete guide  
- **[Quick Guide](https://handbook.datalad.org/en/latest/intro/quickstart.html)** – get started quickly  
- **[Cheat Sheet](https://handbook.datalad.org/en/latest/_downloads/datalad-cheatsheet.pdf)** – handy commands reference  

---

## Usage Tips (DataLad)

- **Get file content**: `datalad get <file_or_dir>`  
- **Unlock a file for editing**: `datalad unlock <file>`  
- **Drop local content**: `datalad drop <file_or_dir>`  
- **Add new files**: `datalad add <file_or_dir>`  
- **Add files from URLs**: `datalad addurls -d . --fast atlas/atlas_urls.csv '{url}' '{path}'`  
- **Check dataset status**: `datalad status`  
- **Save changes**: `datalad save -m "commit message"`  

> Useful for working with large datasets without downloading all content.

---

## Directory Overview

```
atlas-demo/
├── atlas/                     # NetCDF data + metadata
├── catalogs/                  # STAC catalogs
├── scripts/                   # workflow scripts
├── .github/workflows/         # GitHub Actions definitions
├── environment.yml            # Conda environment
├── Makefile                   # local workflow automation
└── README.md
```

---

## Quick Commands

```bash
make help        # show help
make update      # run full local workflow
make metadata    # extract STAC metadata
make checks      # run CF compliance checks
make catalogs    # generate STAC catalog
make clean       # remove generated files
make lint        # lint Python scripts with Ruff
```

---

### Explore & Download via STAC Browser

Each STAC Item in the catalog now includes:

- **`datalad` asset** – points to the local DataLad-managed file  
- **`http` asset** – direct HTTP download link (for demo, using a fixed prefix URL)  

You can browse the catalog directly in a STAC Browser:

👉 **[Open in STAC Browser](https://radiantearth.github.io/stac-browser/#/external/https://raw.githubusercontent.com/cehbrecht/atlas-demo/main/catalogs/stac/stac_catalog.json)**

To download a file via HTTP:

1. Click on an Item in the STAC Browser.
2. Select the `"http"` asset.
3. Copy the URL or download directly in your browser or via `wget`/`curl`.

```bash
# Example using curl
curl -O https://data.mips.climate.copernicus.eu/thredds/fileServer/esg_c3s-cica-atlas/v02/CMIP6/historical/cdbals_CMIP6_historical_yr_1850-2014_v02.nc

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).
