#!/usr/bin/env python3
"""Acquire or plan OSM and GEE data from a saved site selection."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path


SCALE = {"draft": 30.0, "standard": 10.0, "fine": 3.0}


def execute(command):
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {"stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    return {"command": command, "returncode": result.returncode, "result": payload}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("selection", type=Path, nargs="?", default=Path("data/site_selection.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("data"))
    parser.add_argument("--osm-local", type=Path, help="local OSM XML or PBF for local/geofabrik mode")
    parser.add_argument("--dem-local", type=Path, help="local GeoTIFF or ASCII DEM for local mode")
    parser.add_argument("--dem-mode", choices=("direct", "drive"), default="direct")
    parser.add_argument("--authenticate", action="store_true", help="allow the Earth Engine client to open its local auth flow")
    parser.add_argument("--run", action="store_true", help="perform network requests; otherwise print dry-run plans")
    args = parser.parse_args()

    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    boundary = Path(selection["boundary_path"])
    if not boundary.exists():
        raise SystemExit(f"missing boundary: {boundary}")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir = Path(__file__).resolve().parent
    reports, warnings = [], []

    osm_provider = selection.get("osm_provider", "overpass")
    osm_output = args.out_dir / "source_osm.osm"
    if osm_provider == "overpass":
        command = [sys.executable, str(scripts_dir / "fetch_osm.py"), str(boundary), "--output", str(osm_output)]
        if not args.run:
            command.append("--dry-run")
        reports.append({"kind": "osm", **execute(command)})
    elif args.osm_local:
        if not args.osm_local.exists():
            raise SystemExit(f"missing local OSM source: {args.osm_local}")
        osm_output = args.osm_local.resolve()
        reports.append({"kind": "osm", "returncode": 0, "result": {"provider": osm_provider, "source": str(osm_output)}})
    else:
        warnings.append(f"OSM provider is {osm_provider}; pass --osm-local with an existing extract.")

    dataset = selection.get("dem_dataset", "COPERNICUS/DEM/GLO30")
    dem_output = args.out_dir / "source_dem.tif"
    if dataset == "local":
        if args.dem_local and args.dem_local.exists():
            dem_output = args.dem_local.resolve()
            reports.append({"kind": "dem", "returncode": 0, "result": {"provider": "local", "source": str(dem_output)}})
        else:
            warnings.append("DEM provider is local; pass --dem-local with a GeoTIFF or ASCII grid.")
    else:
        precision = selection.get("precision_preset", "standard")
        command = [
            sys.executable,
            str(scripts_dir / "fetch_gee_dem.py"),
            str(boundary),
            "--output",
            str(dem_output),
            "--dataset",
            dataset,
            "--scale",
            str(SCALE.get(precision, 10.0)),
            "--mode",
            args.dem_mode,
        ]
        project = selection.get("gee_project")
        if project:
            command.extend(["--project", project])
        if args.authenticate and args.run:
            command.append("--authenticate")
        if not args.run:
            command.append("--dry-run")
        reports.append({"kind": "dem", **execute(command)})

    report = {
        "schema": "rhino-osm-terrain/acquisition-report-v2",
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "selection": str(args.selection.resolve()),
        "executed": bool(args.run),
        "osm_path": str(osm_output),
        "dem_path": str(dem_output),
        "reports": reports,
        "warnings": warnings,
    }
    output = args.out_dir / "acquisition_report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": all(item.get("returncode", 0) == 0 for item in reports), "report": str(output.resolve()), "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0 if all(item.get("returncode", 0) == 0 for item in reports) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
