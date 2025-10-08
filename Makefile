# Atlas Demo Makefile
PYTHON := python

# Directories
DATA_DIR := atlas/data
META_DIR := atlas/metadata
CHECKS_DIR := atlas/checks
CATALOGS_DIR := catalogs/stac

.PHONY: all help addurls metadata checks catalog status save clean lint

# Default target shows help
all: help

# Show Makefile commands
help:
	@echo "Makefile commands:"
	@echo "  make help       - Show this help message"
	@echo "  make addurls    - Add URLs to DataLad dataset (fast, no get)"
	@echo "  make metadata   - Generate STAC metadata sidecars"
	@echo "  make checks     - Run CF/IOOS compliance checks on available NetCDF files"
	@echo "  make catalog    - Generate static STAC catalog from metadata"
	@echo "  make update     - run checks, metadata, and catalog (recommended workflow)"
	@echo "  make status     - Show DataLad status"
	@echo "  make save       - Save all changes to DataLad"
	@echo "  make clean      - Remove generated metadata, CF reports, catalogs"

# Initialize real data from URLs (fast)
addurls:
	@echo "Adding URLs to DataLad dataset..."
	datalad addurls -d . --key sha256 --fast atlas/atlas_urls.csv '{url}' '{path}'

# Extract metadata
metadata:
	@echo "Extracting metadata ..."
	datalad run \
		-m "Extract metadata" \
		--output '$(META_DIR)' \
		$(PYTHON) scripts/generate_metadata.py

# Run CF/IOOS compliance checks on existing local NetCDF files
checks:
	@echo "Running CF/IOOS compliance checks..."
	datalad run \
		-m "Run CF/IOOS checks on available NetCDF files" \
		--output '$(CHECKS_DIR)' \
		$(PYTHON) scripts/run_checks.py

# Generate static STAC catalog from metadata
catalog:
	@echo "Generating STAC catalog ..."
	datalad run \
		-m "Generate STAC catalog" \
		--output '$(CATALOGS_DIR)' \
		$(PYTHON) scripts/generate_catalog.py

# Update workflow: run checks, metadata, catalog
update: checks metadata catalog
	@echo "Update workflow completed."

# Show DataLad status
status:
	@echo "DataLad status:"
	datalad status

# Save all changes to DataLad
save:
	@echo "Saving all changes to DataLad..."
	datalad save -m "Save all generated files"

# Clean generated files (metadata, CF reports, catalogs)
clean:
	@echo "Cleaning generated metadata, CF reports, and catalogs ..."
	rm -rf $(META_DIR)/*.json $(CHECKS_DIR)/*.txt $(CATALOGS_DIR)/*

# Lint Python scripts
lint:
	@echo "Running Ruff linting on Python scripts..."
	ruff check scripts/
