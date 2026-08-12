#!/usr/bin/env python3
"""Plan or run reproducible OSM and DEM preprocessing for a Rhino site."""

from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import json
import os
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path


PRECISION = {
    "draft": {"target_dem_resolution_m": 30.0, "sample_step_m": 30.0, "contour_interval_m": 20.0, "curve_tolerance_m": 1.0},
    "standard": {"target_dem_resolution_m": 10.0, "sample_step_m": 10.0, "contour_interval_m": 10.0, "curve_tolerance_m": 0.25},
    "fine": {"target_dem_resolution_m": 3.0, "sample_step_m": 3.0, "contour_interval_m": 5.0, "curve_tolerance_m": 0.05},
}


def _windows_drives():
    if os.name != "nt":
        return []
    mask = ctypes.windll.kernel32.GetLogicalDrives()
    return [Path(f"{chr(65 + index)}:\\") for index in range(26) if mask & (1 << index)]


@lru_cache(maxsize=None)
def tool(name):
    found = shutil.which(name)
    if found or os.name != "nt":
        return found

    executable = name if Path(name).suffix else f"{name}.exe"
    roots = []
    for variable in ("QGIS_ROOT", "OSGEO4W_ROOT"):
        value = os.environ.get(variable)
        if value:
            roots.append(Path(value))

    for drive in _windows_drives():
        roots.extend((drive / "qgis", drive / "OSGeo4W", drive / "OSGeo4W64"))
        for program_dir in (drive / "Program Files", drive / "Program Files (x86)"):
            if program_dir.is_dir():
                roots.extend(program_dir.glob("QGIS*"))

    seen = set()
    for root in roots:
        key = str(root).lower()
        if key in seen:
            continue
        seen.add(key)
        candidate = root / "bin" / executable
        if candidate.is_file():
            return str(candidate)
    return None


def osgeo4w_root(executable):
    if not executable or os.name != "nt":
        return None
    path = Path(executable).resolve()
    root = path.parent.parent
    return root if (root / "bin" / "o4w_env.bat").is_file() else None


def command_environment(executable):
    root = osgeo4w_root(executable)
    if root is None:
        return None
    env = os.environ.copy()
    env.update({
        "OSGEO4W_ROOT": str(root),
        "GDAL_DATA": str(root / "apps" / "gdal" / "share" / "gdal"),
        "GDAL_DRIVER_PATH": str(root / "apps" / "gdal" / "lib" / "gdalplugins"),
        "PROJ_DATA": str(root / "share" / "proj"),
        "PROJ_LIB": str(root / "share" / "proj"),
        "PATH": str(root / "bin") + os.pathsep + env.get("PATH", ""),
    })
    return env


def _walk_coords(value, bbox):
    if not isinstance(value, (list, tuple)) or not value:
        return
    if isinstance(value[0], (int, float)):
        if len(value) >= 2:
            bbox[0] = min(bbox[0], float(value[0]))
            bbox[1] = min(bbox[1], float(value[1]))
            bbox[2] = max(bbox[2], float(value[0]))
            bbox[3] = max(bbox[3], float(value[1]))
        return
    for child in value:
        _walk_coords(child, bbox)


def boundary_bbox(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("type") == "FeatureCollection":
        features = payload.get("features") or []
    elif payload.get("type") == "Feature":
        features = [payload]
    else:
        features = [{"geometry": payload}]
    bbox = [float("inf"), float("inf"), float("-inf"), float("-inf")]
    for feature in features:
        _walk_coords((feature.get("geometry") or {}).get("coordinates"), bbox)
    if bbox[0] == float("inf"):
        raise ValueError("boundary contains no coordinates")
    return bbox


def automatic_utm(bbox):
    lon = (bbox[0] + bbox[2]) / 2.0
    lat = (bbox[1] + bbox[3]) / 2.0
    if not (-80.0 <= lat <= 84.0):
        raise ValueError("automatic UTM is unavailable outside 80S to 84N; pass --crs explicitly")
    zone = max(1, min(60, int((lon + 180.0) // 6.0) + 1))
    return f"EPSG:{32600 + zone if lat >= 0 else 32700 + zone}"


def run(command, log):
    log.append({"command": command, "status": "started"})
    if command[0] == "copy":
        Path(command[2]).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(command[1], command[2])
        log[-1].update({"status": "ok", "returncode": 0, "stdout": "", "stderr": ""})
        return
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env=command_environment(command[0]),
    )
    log[-1].update({
        "status": "ok" if result.returncode == 0 else "failed",
        "returncode": result.returncode,
        "stdout": result.stdout[-2000:],
        "stderr": result.stderr[-2000:],
    })
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}")


def vector_command(ogr2ogr, output, source, layer, where, boundary, crs):
    return [
        ogr2ogr,
        "-overwrite",
        "-skipfailures",
        "-f",
        "GeoJSON",
        str(output),
        str(source),
        layer,
        "-where",
        where,
        "-clipsrc",
        str(boundary),
        "-t_srs",
        crs,
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("boundary", type=Path, help="WGS84 site_boundary.geojson")
    parser.add_argument("--osm", type=Path, required=True, help="OSM XML or PBF source")
    parser.add_argument("--dem", type=Path, required=True, help="DEM GeoTIFF or ESRI ASCII grid")
    parser.add_argument("--out-dir", type=Path, default=Path("data/derived"))
    parser.add_argument("--crs", default="auto", help="projected metric CRS, or auto for local UTM")
    parser.add_argument("--precision", choices=tuple(PRECISION), default="standard")
    parser.add_argument("--selection", type=Path, help="site_selection.json with model preview settings")
    parser.add_argument("--run", action="store_true", help="execute the planned commands")
    args = parser.parse_args()

    for path in (args.boundary, args.osm, args.dem):
        if not path.exists():
            raise SystemExit(f"missing input: {path}")

    bbox = boundary_bbox(args.boundary)
    target_crs = automatic_utm(bbox) if args.crs.lower() == "auto" else args.crs
    if not target_crs.upper().startswith("EPSG:"):
        raise SystemExit("--crs must be an EPSG code or auto")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    vector_dir = args.out_dir / "osm"
    vector_dir.mkdir(parents=True, exist_ok=True)
    precision = dict(PRECISION[args.precision])
    commands, logs, warnings = [], [], []
    gdalwarp = tool("gdalwarp")
    gdal_translate = tool("gdal_translate")
    ogr2ogr = tool("ogr2ogr")
    osmium = tool("osmium")
    qgis_root = osgeo4w_root(gdalwarp or gdal_translate or ogr2ogr)

    clipped_osm = args.out_dir / "site.osm.pbf"
    vector_source = args.osm
    if osmium:
        commands.append([osmium, "extract", "--overwrite", "-p", str(args.boundary), "-o", str(clipped_osm), str(args.osm)])
        vector_source = clipped_osm
    else:
        warnings.append("osmium is unavailable; ogr2ogr will read the source extract directly.")

    vector_paths = {
        "roads": vector_dir / "roads.geojson",
        "waterways": vector_dir / "waterways.geojson",
        "buildings": vector_dir / "buildings.geojson",
        "water": vector_dir / "water.geojson",
        "landuse": vector_dir / "landuse.geojson",
        "places": vector_dir / "places.geojson",
    }
    if ogr2ogr:
        specs = [
            ("roads", "lines", "highway IS NOT NULL"),
            ("waterways", "lines", "waterway IS NOT NULL"),
            ("buildings", "multipolygons", "building IS NOT NULL"),
            ("water", "multipolygons", "natural = 'water' OR waterway IS NOT NULL"),
            ("landuse", "multipolygons", "landuse IS NOT NULL"),
            ("places", "points", "place IS NOT NULL"),
        ]
        for key, layer, where in specs:
            commands.append(vector_command(ogr2ogr, vector_paths[key], vector_source, layer, where, args.boundary, target_crs))
    else:
        warnings.append("ogr2ogr is unavailable; install GDAL or use QGIS to create the normalized GeoJSON layers.")

    derived_dem_tif = args.out_dir / "site_dem.tif"
    derived_dem_asc = args.out_dir / "site_dem.asc"
    if gdalwarp and gdal_translate:
        resolution = precision["target_dem_resolution_m"]
        commands.append([
            gdalwarp,
            "-overwrite",
            "-cutline",
            str(args.boundary),
            "-crop_to_cutline",
            "-dstnodata",
            "-9999",
            "-r",
            "bilinear",
            "-t_srs",
            target_crs,
            "-tr",
            str(resolution),
            str(resolution),
            str(args.dem),
            str(derived_dem_tif),
        ])
        commands.append([gdal_translate, "-of", "AAIGrid", str(derived_dem_tif), str(derived_dem_asc)])
    elif args.dem.suffix.lower() == ".asc" and args.crs.lower() != "auto":
        commands.append(["copy", str(args.dem), str(derived_dem_asc)])
        warnings.append("GDAL is unavailable; copied ASCII DEM without reprojection. Verify it already uses the target CRS.")
    else:
        warnings.append("GDAL is unavailable; DEM reprojection and ASCII export were not planned.")

    if args.precision == "fine":
        warnings.append("Fine mode may interpolate below the native DEM resolution; it does not create new survey accuracy.")

    selection_path = args.selection
    if selection_path is None:
        candidate = args.boundary.parent / "site_selection.json"
        selection_path = candidate if candidate.is_file() else None
    selection = {}
    if selection_path:
        try:
            selection = json.loads(selection_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"invalid site selection file: {error}") from error

    if args.run:
        for command in commands:
            run(command, logs)

    manifest = {
        "schema": "rhino-osm-terrain/site-manifest-v2",
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "boundary_wgs84": str(args.boundary.resolve()),
        "bbox_wgs84": bbox,
        "osm_source": str(args.osm.resolve()),
        "dem_source": str(args.dem.resolve()),
        "derived_osm": str(clipped_osm.resolve()),
        "derived_vectors": {key: str(path.resolve()) for key, path in vector_paths.items()},
        "derived_dem_tif": str(derived_dem_tif.resolve()),
        "derived_dem_asc": str(derived_dem_asc.resolve()),
        "horizontal_crs": target_crs,
        "vertical_units": "meters; verify source metadata",
        "local_origin": "DEM grid center; applied by rhino_site_builder.py",
        "precision_preset": args.precision,
        "precision": precision,
        "selection": str(selection_path.resolve()) if selection_path else None,
        "model_settings": selection.get("model_settings") or {},
        "tools": {
            name: bool(value)
            for name, value in (("gdalwarp", gdalwarp), ("gdal_translate", gdal_translate), ("ogr2ogr", ogr2ogr), ("osmium", osmium))
        },
        "tool_paths": {
            name: value
            for name, value in (("gdalwarp", gdalwarp), ("gdal_translate", gdal_translate), ("ogr2ogr", ogr2ogr), ("osmium", osmium))
        },
        "osgeo4w_root": str(qgis_root) if qgis_root else None,
        "planned_commands": commands,
        "executed": bool(args.run),
        "command_log": logs,
        "warnings": warnings,
    }
    manifest_path = args.out_dir / "site_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "manifest": str(manifest_path.resolve()), "crs": target_crs, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
