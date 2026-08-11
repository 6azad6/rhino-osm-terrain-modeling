#!/usr/bin/env python3
"""Check the Rhino terrain toolchain and optionally install missing open tools."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from prepare_site_data import _windows_drives, command_environment, osgeo4w_root, tool


def state_path():
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
    return base / "Codex" / "rhino-osm-terrain-modeling" / "bootstrap.json"


def find_rhino():
    candidates = []
    if os.name == "nt":
        for drive in _windows_drives():
            candidates.extend((
                drive / "Program Files" / "Rhino 8" / "System" / "Rhino.exe",
                drive / "Rhino 8" / "System" / "Rhino.exe",
            ))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return shutil.which("Rhino") or shutil.which("Rhino.exe")


def command_version(command, env=None):
    if not command:
        return None
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, env=env, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (result.stdout or result.stderr).strip().splitlines()
    return text[0] if result.returncode == 0 and text else None


def install_commands(status):
    commands = {}
    if not status["components"]["qgis_gdal"]["installed"] and shutil.which("winget"):
        commands["qgis_gdal"] = [
            "winget", "install", "--id", "OSGeo.QGIS_LTR", "--exact", "--silent",
            "--accept-package-agreements", "--accept-source-agreements",
        ]
    if not status["components"]["osmium"]["installed"] and shutil.which("conda"):
        commands["osmium"] = ["conda", "install", "--yes", "--channel", "conda-forge", "osmium-tool"]
    if not status["components"]["earth_engine"]["installed"]:
        commands["earth_engine"] = [sys.executable, "-m", "pip", "install", "--upgrade", "earthengine-api"]
    return commands


def inspect_environment():
    gdalwarp = tool("gdalwarp")
    gdal_translate = tool("gdal_translate")
    ogr2ogr = tool("ogr2ogr")
    qgis_root = osgeo4w_root(gdalwarp or gdal_translate or ogr2ogr)
    osmium = tool("osmium")
    rhino = find_rhino()
    earth_engine = importlib.util.find_spec("ee") is not None
    components = {
        "qgis_gdal": {
            "installed": all((gdalwarp, gdal_translate, ogr2ogr)),
            "path": str(qgis_root) if qgis_root else gdalwarp,
            "version": command_version([gdalwarp, "--version"], command_environment(gdalwarp)) if gdalwarp else None,
            "required_when": "OSM and DEM preprocessing",
        },
        "osmium": {
            "installed": bool(osmium),
            "path": osmium,
            "version": command_version([osmium, "--version"]) if osmium else None,
            "required_when": "large PBF clipping; optional for small OSM XML sites",
        },
        "earth_engine": {
            "installed": earth_engine,
            "path": sys.executable if earth_engine else None,
            "version": None,
            "required_when": "Google Earth Engine DEM acquisition",
        },
        "rhino_8": {
            "installed": bool(rhino),
            "path": rhino,
            "version": None,
            "required_when": "final .3dm generation; manual license installation",
        },
    }
    status = {
        "ok": True,
        "first_run": not state_path().exists(),
        "state_path": str(state_path()),
        "components": components,
    }
    commands = install_commands(status)
    status["missing"] = [name for name, item in components.items() if not item["installed"]]
    status["installable_missing"] = list(commands)
    status["manual_missing"] = [name for name in status["missing"] if name not in commands]
    status["install_plan"] = commands
    status["reminder_needed"] = status["first_run"] and bool(commands)
    return status


def write_state(action, status, logs=None):
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "rhino-osm-terrain/bootstrap-v1",
        "updated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "action": action,
        "missing": status.get("missing", []),
        "logs": logs or [],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def install_missing():
    before = inspect_environment()
    logs = []
    for component, command in before["install_plan"].items():
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        logs.append({
            "component": component,
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-2000:],
        })
    tool.cache_clear()
    after = inspect_environment()
    write_state("install", after, logs)
    payload = {"ok": all(log["returncode"] == 0 for log in logs), "before": before, "after": after, "logs": logs}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--install", action="store_true", help="install all missing open-source components")
    action.add_argument("--acknowledge", action="store_true", help="record that the first-run reminder was shown")
    args = parser.parse_args()

    if args.install:
        return install_missing()
    status = inspect_environment()
    if args.acknowledge:
        write_state("acknowledge", status)
        status["first_run"] = False
        status["reminder_needed"] = False
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
