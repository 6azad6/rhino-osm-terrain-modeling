#!/usr/bin/env python3
"""Download a DEM from Google Earth Engine for a GeoJSON site boundary.

The Earth Engine Python API is optional at install time. Run with ``--dry-run``
to inspect the request without importing Earth Engine or opening a login flow.
Interactive authentication is only attempted when ``--authenticate`` is given.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import urllib.request
from pathlib import Path


DEFAULT_DATASET = "COPERNICUS/DEM/GLO30"
KNOWN_DATASETS = {
    "COPERNICUS/DEM/GLO30": {"band": "DEM", "native_resolution_m": 30.0},
    "USGS/SRTMGL1_003": {"band": "elevation", "native_resolution_m": 30.0},
    "NASA/NASADEM_HGT/001": {"band": "elevation", "native_resolution_m": 30.0},
}


def read_geometry(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("type") == "FeatureCollection":
        features = payload.get("features") or []
        if len(features) != 1:
            raise ValueError("Earth Engine export expects one Polygon or MultiPolygon feature")
        payload = features[0]
    if payload.get("type") == "Feature":
        payload = payload.get("geometry") or {}
    if payload.get("type") not in ("Polygon", "MultiPolygon"):
        raise ValueError("boundary must be a Polygon or MultiPolygon GeoJSON")
    return payload


def request_report(args, geometry):
    return {
        "provider": "google-earth-engine",
        "dataset": args.dataset,
        "band": args.band,
        "scale_m": args.scale,
        "native_resolution_m": (KNOWN_DATASETS.get(args.dataset) or {}).get("native_resolution_m"),
        "output_crs": args.crs,
        "boundary_path": str(args.boundary.resolve()),
        "mode": args.mode,
        "project": args.project,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "geometry_type": geometry["type"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("boundary", type=Path, help="WGS84 Polygon/MultiPolygon GeoJSON")
    parser.add_argument("--output", type=Path, default=Path("data/site_dem.tif"))
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--band", help="elevation band; inferred for bundled dataset choices")
    parser.add_argument("--scale", type=float, default=30.0, help="requested output pixel size in metres")
    parser.add_argument("--crs", default="EPSG:4326", help="export CRS; reproject locally before Rhino")
    parser.add_argument("--project", help="Google Cloud project registered for Earth Engine")
    parser.add_argument("--mode", choices=("direct", "drive"), default="direct")
    parser.add_argument("--drive-folder", default="codex-terrain")
    parser.add_argument("--authenticate", action="store_true", help="run ee.Authenticate() if needed")
    parser.add_argument("--dry-run", action="store_true", help="print configuration without network or auth")
    args = parser.parse_args()
    if not args.band:
        known = KNOWN_DATASETS.get(args.dataset)
        if not known:
            parser.error("--band is required for an unknown Earth Engine dataset")
        args.band = known["band"]

    try:
        geometry = read_geometry(args.boundary)
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    report = request_report(args, geometry)
    if args.dry_run:
        report["ok"] = True
        report["note"] = "No Earth Engine request was made."
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    try:
        import ee  # type: ignore
    except ImportError:
        report.update({"ok": False, "error": "Missing earthengine-api; install it in the selected Python environment."})
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    try:
        try:
            ee.Initialize(project=args.project) if args.project else ee.Initialize()
        except Exception:
            if not args.authenticate:
                raise RuntimeError("Earth Engine is not authenticated. Re-run with --authenticate, then provide --project if required.")
            ee.Authenticate()
            ee.Initialize(project=args.project) if args.project else ee.Initialize()

        ee_geometry = ee.Geometry(geometry)
        image = ee.Image(args.dataset).select(args.band).clip(ee_geometry)
        if args.mode == "drive":
            description = "codex_terrain_" + dt.datetime.now().strftime("%Y%m%d_%H%M%S")
            task = ee.batch.Export.image.toDrive(
                image=image,
                description=description,
                folder=args.drive_folder,
                fileNamePrefix=description,
                region=geometry,
                scale=args.scale,
                crs=args.crs,
                maxPixels=1e13,
                fileFormat="GeoTIFF",
            )
            task.start()
            report.update({"ok": True, "task_id": task.id, "task_description": description,
                           "note": "Drive export started; download the GeoTIFF before Rhino preprocessing."})
        else:
            params = {
                "region": geometry,
                "scale": args.scale,
                "crs": args.crs,
                "format": "GEO_TIFF",
                "maxPixels": 1e13,
            }
            url = image.getDownloadURL(params)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(url, timeout=300) as response:
                args.output.write_bytes(response.read())
            report.update({"ok": True, "output": str(args.output.resolve()), "bytes": args.output.stat().st_size})
    except Exception as error:  # pragma: no cover - depends on user account and network
        report.update({"ok": False, "error": str(error)})

    metadata_path = args.output.with_suffix(args.output.suffix + ".json")
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
