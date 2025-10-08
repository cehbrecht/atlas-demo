#!/usr/bin/env python3
"""
Generate a nested STAC catalog from metadata JSONs in atlas/metadata.
Folder hierarchy (e.g., v02/CMIP6/historical) is preserved as nested subcatalogs.
Each folder becomes its own catalog.json with relative links.
Includes HTTP, S3, DataLad, and check file assets.
Compatible with DataLad and pystac 1.x.
"""

from pathlib import Path
import json
import datetime
import pystac

# --- Configuration ----------------------------------------------------------

META_DIR = Path("atlas/metadata")
CATALOG_DIR = Path("catalogs/stac")
CATALOG_DIR.mkdir(parents=True, exist_ok=True)

HTTP_PREFIX = "https://data.mips.climate.copernicus.eu/thredds/fileServer/esg_c3s-cica-atlas"
S3_PREFIX = "s3://datalad-demo"
CHECKS_PREFIX = "https://raw.githubusercontent.com/cehbrecht/atlas-demo/refs/heads/main/atlas/checks"

# --- Root catalog -----------------------------------------------------------

root_catalog = pystac.Catalog(
    id="atlas-demo",
    title="Atlas Demo",
    description="Atlas Demo STAC Catalog (recursive hierarchy)"
)

# Cache of created subcatalogs
catalog_cache = {"": root_catalog}


# --- Helpers ---------------------------------------------------------------

def load_metadata(meta_file: Path) -> dict:
    with open(meta_file) as f:
        return json.load(f)


def create_geometry(bbox):
    if not bbox:
        return None
    return {
        "type": "Polygon",
        "coordinates": [[
            [bbox[0], bbox[1]],
            [bbox[0], bbox[3]],
            [bbox[2], bbox[3]],
            [bbox[2], bbox[1]],
            [bbox[0], bbox[1]]
        ]]
    }


def create_item(meta: dict, datalad_href: str) -> pystac.Item:
    bbox = meta.get("bbox")
    geometry = create_geometry(bbox)

    time_range = meta.get("time_range")
    start_time = datetime.datetime.fromisoformat(time_range[0]) if time_range else datetime.datetime.utcnow()
    end_time = datetime.datetime.fromisoformat(time_range[1]) if time_range else start_time

    item = pystac.Item(
        id=meta["title"],
        geometry=geometry,
        bbox=bbox,
        datetime=start_time,
        properties={}
    )

    props = {**meta.get("attributes", {})}
    props.update({
        "title": meta["title"],
        "variables": meta.get("variables", []),
        "dimensions": meta.get("dimensions", {}),
        "datetime": {"start": start_time.isoformat(), "end": end_time.isoformat()},
    })
    item.properties.update(props)

    add_assets(item, datalad_href)
    return item


def add_assets(item: pystac.Item, datalad_href: str):
    # DataLad asset
    item.add_asset(
        "datalad",
        pystac.Asset(
            href=datalad_href,
            media_type="application/netcdf",
            roles=["data"],
            title="DataLad reference",
        )
    )

    # Derive relative path for other assets
    path_relative = Path(datalad_href)
    try:
        rel_path = path_relative.relative_to("atlas/data")
    except ValueError:
        rel_path = path_relative

    # HTTP asset
    item.add_asset(
        "download",
        pystac.Asset(
            href=f"{HTTP_PREFIX}/{rel_path.as_posix()}",
            media_type="application/netcdf",
            roles=["data"],
            title="HTTP download",
        )
    )

    # S3 asset
    item.add_asset(
        "s3",
        pystac.Asset(
            href=f"{S3_PREFIX}/{rel_path.as_posix()}",
            media_type="application/netcdf",
            roles=["data"],
            title="S3 download",
        )
    )

    # Check asset
    check_href = f"{CHECKS_PREFIX}/{rel_path.with_name(rel_path.stem + '_check.txt').as_posix()}"
    item.add_asset(
        "check",
        pystac.Asset(
            href=check_href,
            media_type="text/plain",
            roles=["metadata"],
            title="CF/IOOS compliance check",
        )
    )


def get_or_create_subcatalog(rel_folder: Path) -> pystac.Catalog:
    """Recursively create (or fetch) subcatalogs for a folder path."""
    # Base case: root level
    if not rel_folder or str(rel_folder) in (".", ""):
        return root_catalog

    rel_str = str(rel_folder)
    if rel_str in catalog_cache:
        return catalog_cache[rel_str]

    # Ensure parent is created first
    parent = get_or_create_subcatalog(rel_folder.parent)

    cat_id = rel_folder.name
    cat_desc = f"Subcatalog for {rel_folder}"

    subcatalog_path = CATALOG_DIR / rel_folder
    subcatalog_path.mkdir(parents=True, exist_ok=True)

    subcatalog = pystac.Catalog(
        id=cat_id,
        title=cat_id,
        description=cat_desc,
        href=str(subcatalog_path / "catalog.json")
    )
    parent.add_child(subcatalog)
    catalog_cache[rel_str] = subcatalog
    return subcatalog



# --- Main loop --------------------------------------------------------------

def build_catalog():
    for meta_file in META_DIR.rglob("*.stac.json"):
        meta = load_metadata(meta_file)
        datalad_href = meta["assets"]["datalad"]

        rel_folder = meta_file.parent.relative_to(META_DIR)
        subcatalog = get_or_create_subcatalog(rel_folder)

        item = create_item(meta, datalad_href)
        item_path = CATALOG_DIR / rel_folder / f"{item.id}.json"
        item.set_self_href(str(item_path))
        subcatalog.add_item(item)
        item.save_object()


# --- Run -------------------------------------------------------------------

if __name__ == "__main__":
    build_catalog()
    root_catalog.normalize_and_save(root_href=str(CATALOG_DIR), catalog_type=pystac.CatalogType.SELF_CONTAINED)
    print(f"✅ STAC catalog saved under {CATALOG_DIR}/catalog.json")
