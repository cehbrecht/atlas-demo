# Atlas Demo Makefile
PYTHON := python

# Directories
DATA_DIR := atlas/data
META_DIR := atlas/metadata
CHECKS_DIR := atlas/checks
CATALOGS_DIR := catalogs/stac

.PHONY: all help addurls metadata checks catalog status diff save info push clean lint

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
	@echo "  make diff       - Show DataLad diff"
	@echo "  make info       - Show DataLad info"
	@echo "  make save       - Save all changes to DataLad"
	@echo "  make push       - Push to all remotes"
	@echo "  make clean      - Remove generated metadata, CF reports, catalogs"

# Initialize real data from URLs (download)
addurls:
	@echo "Adding URLs to DataLad dataset (download)..."
	datalad addurls -d . --key sha256 atlas/atlas_urls.csv '{url}' '{path}'

# Initialize real data from URLs (fast)
addurls_fast:
	@echo "Adding URLs to DataLad dataset (fast)..."
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

# Show DataLad diff
diff:
	@ds="$(shell git -C . rev-parse --show-toplevel)"; \
	echo "Dataset: $$ds"; \
	echo "==== datalad diff ===="; \
	datalad diff --dataset "$$ds"

# Save all changes to DataLad
save:
	@echo "Saving all changes to DataLad..."
	datalad save -m "Save all generated files"

# info target for DataLad datasets
info:
	@ds="$(shell git -C . rev-parse --show-toplevel)"; \
	echo "Dataset: $$ds"; \
	echo "==== git annex info ===="; \
	git -C "$$ds" annex info;

# push to all remotes
push:
	@ds="$(shell git -C . rev-parse --show-toplevel)"; \
	echo "Dataset: $$ds"; \
	echo "==== git push ===="; \
	git -C "$$ds" push --all; \
	git -C "$$ds" push --tags; \
	echo "==== git annex sync (including remotes) ===="; \
	# git -C "$$ds" annex sync --content --all
	git -C "$$ds" annex sync --all

# Clean generated files (metadata, CF reports, catalogs)
clean:
	@echo "Cleaning generated metadata, CF reports, and catalogs ..."
	rm -rf $(META_DIR)/*.json $(CHECKS_DIR)/*.txt $(CATALOGS_DIR)/*

# Lint Python scripts
lint:
	@echo "Running Ruff linting on Python scripts..."
	ruff check scripts/
