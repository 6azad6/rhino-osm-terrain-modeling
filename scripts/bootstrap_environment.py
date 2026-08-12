#!/usr/bin/env python3
"""Check the Rhino terrain toolchain and optionally install missing open tools."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

from prepare_site_data import _windows_drives, command_environment, osgeo4w_root, tool


def state_path():
    return Path(__file__).resolve().parent.parent / ".runtime" / "bootstrap.json"


def managed_python_path():
    return Path(__file__).resolve().parent.parent / ".runtime" / "python"


def python_module_available(name):
    if importlib.util.find_spec(name) is not None:
        return True
    managed = managed_python_path()
    return (managed / name).exists() or any(managed.glob(f"{name}-*.dist-info"))


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
    if not status["components"]["rhino3dm"]["installed"]:
        commands["rhino3dm"] = [
            sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(managed_python_path()), "rhino3dm"
        ]
    if not status["components"]["shapely"]["installed"]:
        commands["shapely"] = [sys.executable, "-m", "pip", "install", "--upgrade", "shapely"]
    return commands


def inspect_environment():
    gdalwarp = tool("gdalwarp")
    gdal_translate = tool("gdal_translate")
    ogr2ogr = tool("ogr2ogr")
    qgis_root = osgeo4w_root(gdalwarp or gdal_translate or ogr2ogr)
    osmium = tool("osmium")
    rhino = find_rhino()
    earth_engine = python_module_available("ee")
    rhino3dm = python_module_available("rhino3dm")
    shapely = python_module_available("shapely")
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
        "rhino3dm": {
            "installed": rhino3dm,
            "path": str(managed_python_path()) if rhino3dm else None,
            "version": None,
            "required_when": "default headless .3dm generation",
        },
        "shapely": {
            "installed": shapely,
            "path": sys.executable if shapely else None,
            "version": None,
            "required_when": "continuous roads and projected polygon surfaces",
        },
        "rhino_8": {
            "installed": bool(rhino),
            "path": rhino,
            "version": None,
            "required_when": "optional RhinoCommon enhancement and visual review",
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


def install_rhino3dm_fallback():
    """Install the official compatible wheel without invoking pip's unpacker."""
    api_url = "https://pypi.org/pypi/rhino3dm/json"
    with urllib.request.urlopen(api_url, timeout=60) as response:
        payload = json.load(response)
    cp_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
    if os.name == "nt":
        platform_tags = ("win_amd64", "win32", "win_arm64")
    elif sys.platform == "darwin":
        platform_tags = ("macosx",)
    else:
        platform_tags = ("manylinux", "musllinux", "linux")
    candidates = []
    for item in payload.get("urls", []):
        filename = item.get("filename", "")
        if filename.endswith(".whl") and cp_tag in filename and any(tag in filename for tag in platform_tags):
            candidates.append(item)
    if not candidates:
        raise RuntimeError(f"No rhino3dm wheel matches {cp_tag} on {sys.platform}")
    item = candidates[0]
    target = managed_python_path()
    target.mkdir(parents=True, exist_ok=True)
    temp_root = managed_python_path().parent / "downloads"
    temp_root.mkdir(parents=True, exist_ok=True)
    wheel_path = temp_root / item["filename"]
    urllib.request.urlretrieve(item["url"], wheel_path)
    expected_sha256 = (item.get("digests") or {}).get("sha256")
    if expected_sha256:
        actual_sha256 = hashlib.sha256(wheel_path.read_bytes()).hexdigest()
        if actual_sha256 != expected_sha256:
            raise RuntimeError(f"rhino3dm wheel checksum mismatch: {wheel_path.name}")
    target_root = target.resolve()
    with zipfile.ZipFile(wheel_path) as archive:
        for member in archive.infolist():
            destination = (target / member.filename).resolve()
            if destination != target_root and target_root not in destination.parents:
                raise RuntimeError(f"Unsafe wheel member: {member.filename}")
        archive.extractall(target)
    return {
        "component": "rhino3dm",
        "method": "official-wheel-extract",
        "wheel": str(wheel_path),
        "target": str(target),
    }


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
        env = os.environ.copy()
        temp_dir = managed_python_path().parent / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        env["TEMP"] = str(temp_dir)
        env["TMP"] = str(temp_dir)
        result = subprocess.run(command, capture_output=True, text=True, check=False, env=env)
        log = {
            "component": component,
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-2000:],
        }
        if component == "rhino3dm" and result.returncode != 0:
            try:
                log["fallback"] = install_rhino3dm_fallback()
                log["returncode"] = 0
            except Exception as error:
                log["fallback_error"] = str(error)
        logs.append(log)
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
