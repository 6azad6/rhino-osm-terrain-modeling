#!/usr/bin/env python3
"""Serve the lightweight Rhino site selector and persist its local state."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import subprocess
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


PRECISION_SCALE = {"draft": 30.0, "standard": 10.0, "fine": 3.0}
DEFAULT_MODEL_SETTINGS = {
    "default_building_height_m": 10.0,
    "floor_height_m": 3.0,
    "height_scale": 1.0,
    "colors": {
        "terrain": "#697e61",
        "contours": "#5c6e53",
        "roads": "#9b8e7c",
        "buildings": "#b8c0ca",
        "water": "#4984b0",
        "landuse": "#719064",
    },
    "visible_layers": {
        "terrain": True,
        "contours": True,
        "roads": True,
        "buildings": True,
        "water": True,
        "landuse": True,
    },
}
PREVIEW_ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
ALLOWED_STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/vendor/leaflet.css": ("vendor/leaflet.css", "text/css; charset=utf-8"),
    "/vendor/leaflet.js": ("vendor/leaflet.js", "text/javascript; charset=utf-8"),
    "/vendor/leaflet.draw.css": ("vendor/leaflet.draw.css", "text/css; charset=utf-8"),
    "/vendor/leaflet.draw.js": ("vendor/leaflet.draw.js", "text/javascript; charset=utf-8"),
    "/vendor/topojson-client.min.js": ("vendor/topojson-client.min.js", "text/javascript; charset=utf-8"),
    "/vendor/countries-110m.json": ("vendor/countries-110m.json", "application/json; charset=utf-8"),
    "/vendor/images/layers.png": ("vendor/images/layers.png", "image/png"),
    "/vendor/images/layers-2x.png": ("vendor/images/layers-2x.png", "image/png"),
    "/vendor/images/marker-icon.png": ("vendor/images/marker-icon.png", "image/png"),
    "/vendor/images/marker-shadow.png": ("vendor/images/marker-shadow.png", "image/png"),
    "/vendor/images/spritesheet.png": ("vendor/images/spritesheet.png", "image/png"),
    "/vendor/images/spritesheet-2x.png": ("vendor/images/spritesheet-2x.png", "image/png"),
    "/vendor/images/spritesheet.svg": ("vendor/images/spritesheet.svg", "image/svg+xml"),
}


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


def normalize_boundary(payload):
    if payload.get("type") == "Feature":
        payload = {"type": "FeatureCollection", "features": [payload]}
    if payload.get("type") != "FeatureCollection":
        raise ValueError("boundary must be a GeoJSON FeatureCollection")
    bbox = [float("inf"), float("inf"), float("-inf"), float("-inf")]
    features = []
    for feature in payload.get("features") or []:
        geometry = feature.get("geometry") or {}
        if geometry.get("type") not in ("Polygon", "MultiPolygon"):
            continue
        _walk_coords(geometry.get("coordinates"), bbox)
        features.append({
            "type": "Feature",
            "properties": feature.get("properties") or {},
            "geometry": geometry,
        })
    if not features or bbox[0] == float("inf"):
        raise ValueError("draw or load one Polygon or MultiPolygon")
    return {"type": "FeatureCollection", "features": features}, bbox


def read_json(path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _clamp_number(value, fallback, minimum, maximum):
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = fallback
    return min(max(number, minimum), maximum)


def normalize_model_settings(payload):
    source = payload if isinstance(payload, dict) else {}
    colors = source.get("colors") if isinstance(source.get("colors"), dict) else {}
    visible = source.get("visible_layers") if isinstance(source.get("visible_layers"), dict) else {}
    result = {
        "default_building_height_m": _clamp_number(
            source.get("default_building_height_m"), 10.0, 1.0, 300.0
        ),
        "floor_height_m": _clamp_number(source.get("floor_height_m"), 3.0, 2.0, 8.0),
        "height_scale": _clamp_number(source.get("height_scale"), 1.0, 0.2, 3.0),
        "colors": {},
        "visible_layers": {},
    }
    for key, fallback in DEFAULT_MODEL_SETTINGS["colors"].items():
        value = str(colors.get(key, fallback)).lower()
        result["colors"][key] = value if re.fullmatch(r"#[0-9a-f]{6}", value) else fallback
    for key, fallback in DEFAULT_MODEL_SETTINGS["visible_layers"].items():
        result["visible_layers"][key] = bool(visible.get(key, fallback))
    return result


def _preview_query(bbox):
    west, south, east, north = bbox
    box = f"{south:.8f},{west:.8f},{north:.8f},{east:.8f}"
    return f"""[out:json][timeout:90];
(
  way["building"]({box});
  relation["building"]["type"="multipolygon"]({box});
  way["highway"]["area"!="yes"]({box});
  way["natural"="water"]({box});
  way["waterway"]({box});
  relation["natural"="water"]["type"="multipolygon"]({box});
  way["landuse"]({box});
  relation["landuse"]["type"="multipolygon"]({box});
);
out tags geom;
"""


def _preview_ring(geometry):
    points = [[float(point["lon"]), float(point["lat"])] for point in geometry or [] if "lon" in point and "lat" in point]
    if len(points) >= 3 and points[0] != points[-1]:
        points.append(points[0])
    return points


def compact_preview(payload, max_features=2500):
    features = []
    counts = {"buildings": 0, "roads": 0, "water": 0, "landuse": 0}
    for element in payload.get("elements") or []:
        tags = element.get("tags") or {}
        kind = None
        if tags.get("building"):
            kind = "buildings"
        elif tags.get("highway"):
            kind = "roads"
        elif tags.get("natural") == "water" or tags.get("waterway"):
            kind = "water"
        elif tags.get("landuse"):
            kind = "landuse"
        if not kind:
            continue
        geometries = []
        if element.get("type") == "way":
            ring = _preview_ring(element.get("geometry"))
            if len(ring) >= (4 if kind != "roads" else 2):
                geometries.append(ring)
        else:
            for member in element.get("members") or []:
                if member.get("type") == "way" and member.get("role") in ("outer", ""):
                    ring = _preview_ring(member.get("geometry"))
                    if len(ring) >= (4 if kind != "roads" else 2):
                        geometries.append(ring)
        for geometry in geometries:
            features.append({
                "kind": kind,
                "coordinates": geometry,
                "height": tags.get("height"),
                "levels": tags.get("building:levels"),
                "width": tags.get("width"),
                "highway": tags.get("highway"),
            })
            counts[kind] += 1
            if len(features) >= max_features:
                return {"features": features, "counts": counts, "truncated": True}
    return {"features": features, "counts": counts, "truncated": False}


def fetch_osm_preview(bbox, cache_path=None):
    width_km = abs(bbox[2] - bbox[0]) * 111.32 * math.cos(math.radians((bbox[1] + bbox[3]) / 2))
    height_km = abs(bbox[3] - bbox[1]) * 110.54
    area_km2 = abs(width_km * height_km)
    if area_km2 > 100:
        raise ValueError("OSM preview is limited to 100 km2. Reduce the boundary or use the formal local PBF workflow.")
    cached = read_json(cache_path) if cache_path else None
    cached_bbox = cached.get("bbox_wgs84") if cached else None
    same_bbox = (
        isinstance(cached_bbox, list)
        and len(cached_bbox) == 4
        and all(abs(float(cached_bbox[index]) - bbox[index]) < 1e-8 for index in range(4))
    )
    if cached and cached.get("features") and same_bbox:
        result = dict(cached)
        result.update({"ok": True, "area_km2": area_km2, "source": "local-preview-cache"})
        return result
    body = urllib.parse.urlencode({"data": _preview_query(bbox)}).encode("utf-8")
    errors = []
    for endpoint in PREVIEW_ENDPOINTS:
        try:
            request = urllib.request.Request(
                endpoint,
                data=body,
                method="POST",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "codex-rhino-site-studio/3.0",
                },
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                result = compact_preview(json.loads(response.read().decode("utf-8")))
            result.update({"ok": True, "area_km2": area_km2, "source": endpoint})
            result["bbox_wgs84"] = bbox
            if cache_path:
                write_json(cache_path, result)
            return result
        except Exception as error:
            errors.append(f"{endpoint}: {error}")
    raise RuntimeError("OSM preview failed: " + " | ".join(errors))


def selection_record(payload, boundary, bbox, boundary_path):
    precision = payload.get("precision_preset", "standard")
    if precision not in PRECISION_SCALE:
        raise ValueError("precision_preset must be draft, standard, or fine")
    osm_provider = payload.get("osm_provider", "overpass")
    if osm_provider not in ("overpass", "local", "geofabrik"):
        raise ValueError("unsupported OSM provider")
    return {
        "schema": "rhino-osm-terrain/site-selection-v2",
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "boundary_path": str(boundary_path.resolve()),
        "bbox_wgs84": bbox,
        "feature_count": len(boundary["features"]),
        "osm_provider": osm_provider,
        "dem_dataset": payload.get("dem_dataset", "COPERNICUS/DEM/GLO30"),
        "gee_project": payload.get("gee_project") or None,
        "precision_preset": precision,
        "requested_scale_m": PRECISION_SCALE[precision],
        "model_settings": normalize_model_settings(payload.get("model_settings")),
    }


def geocode(query, cache_path):
    cache = read_json(cache_path, {}) or {}
    key = query.casefold().strip()
    if key in cache:
        return cache[key]
    params = urllib.parse.urlencode({"q": query, "format": "jsonv2", "limit": 5, "addressdetails": 0})
    request = urllib.request.Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": "codex-rhino-site-studio/2.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        results = json.loads(response.read().decode("utf-8"))
    cache[key] = results
    write_json(cache_path, cache)
    return results


def run_plan(kind, data_dir, scripts_dir, settings):
    boundary_path = data_dir / "site_boundary.geojson"
    if not boundary_path.exists():
        raise ValueError("save a boundary before preparing a request")
    if kind == "osm":
        provider = settings.get("osm_provider", "overpass")
        if provider != "overpass":
            guidance = (
                "Provide an existing OSM XML or PBF path with --osm-local."
                if provider == "local"
                else "Download the matching Geofabrik PBF, then pass it with --osm-local."
            )
            result = {
                "ok": True,
                "provider": provider,
                "network_request": False,
                "requires_local_path": True,
                "message": guidance,
            }
            output_path = data_dir / "osm_request_plan.json"
            write_json(output_path, result)
            return result, output_path
        command = [
            sys.executable,
            str(scripts_dir / "fetch_osm.py"),
            str(boundary_path),
            "--output",
            str(data_dir / "source_osm.osm"),
            "--dry-run",
        ]
        output_path = data_dir / "osm_request_plan.json"
    elif kind == "dem":
        dataset = settings.get("dem_dataset", "COPERNICUS/DEM/GLO30")
        if dataset == "local":
            result = {
                "ok": True,
                "provider": "local",
                "message": "Use a local GeoTIFF or ESRI ASCII grid; no DEM network plan is needed.",
            }
            output_path = data_dir / "dem_request_plan.json"
            write_json(output_path, result)
            return result, output_path
        precision = settings.get("precision_preset", "standard")
        command = [
            sys.executable,
            str(scripts_dir / "fetch_gee_dem.py"),
            str(boundary_path),
            "--dataset",
            dataset,
            "--scale",
            str(PRECISION_SCALE.get(precision, 10.0)),
            "--output",
            str(data_dir / "source_dem.tif"),
            "--dry-run",
        ]
        if settings.get("gee_project"):
            command.extend(["--project", settings["gee_project"]])
        output_path = data_dir / "dem_request_plan.json"
    else:
        raise ValueError("kind must be osm or dem")
    completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=30)
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "request plan failed")
    result = json.loads(completed.stdout)
    result["command"] = command
    write_json(output_path, result)
    return result, output_path


def make_handler(app_dir, data_dir, scripts_dir):
    boundary_path = data_dir / "site_boundary.geojson"
    selection_path = data_dir / "site_selection.json"
    geocode_cache = data_dir / "geocode_cache.json"
    osm_preview_cache = data_dir / "osm_preview.json"

    class Handler(BaseHTTPRequestHandler):
        server_version = "RhinoSiteStudio/2.0"

        def _json(self, status, payload):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _payload(self):
            length = int(self.headers.get("Content-Length", "0"))
            if length > 4_000_000:
                raise ValueError("request body is too large")
            return json.loads(self.rfile.read(length).decode("utf-8"))

        def do_GET(self):  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path in ALLOWED_STATIC:
                name, content_type = ALLOWED_STATIC[parsed.path]
                body = (app_dir / name).read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == "/api/status":
                selection = read_json(selection_path)
                if selection and boundary_path.exists():
                    selection = dict(selection)
                    selection["boundary"] = read_json(boundary_path)
                self._json(200, {
                    "ok": True,
                    "selection": selection,
                    "files": {
                        "boundary": boundary_path.exists(),
                        "osm": (data_dir / "source_osm.osm").exists(),
                        "dem": (data_dir / "source_dem.tif").exists(),
                    },
                })
                return
            if parsed.path == "/api/geocode":
                query = urllib.parse.parse_qs(parsed.query).get("q", [""])[0].strip()
                if not query:
                    self._json(400, {"ok": False, "message": "enter a place name"})
                    return
                try:
                    self._json(200, {"ok": True, "results": geocode(query, geocode_cache)})
                except Exception as error:  # pragma: no cover - remote provider
                    self._json(502, {"ok": False, "message": f"Geocoding failed: {error}"})
                return
            self.send_error(404)

        def do_POST(self):  # noqa: N802
            route = urllib.parse.urlparse(self.path).path
            try:
                payload = self._payload()
                if route == "/api/selection":
                    boundary, bbox = normalize_boundary(payload.get("boundary") or payload)
                    record = selection_record(payload, boundary, bbox, boundary_path)
                    write_json(boundary_path, boundary)
                    write_json(selection_path, record)
                    self._json(200, {
                        "ok": True,
                        "message": "Boundary and settings saved.",
                        "boundary_path": str(boundary_path.resolve()),
                        "selection_path": str(selection_path.resolve()),
                    })
                    return
                if route == "/api/plan":
                    settings = read_json(selection_path, {}) or {}
                    settings.update(payload)
                    result, output_path = run_plan(payload.get("kind"), data_dir, scripts_dir, settings)
                    self._json(200, {
                        "ok": True,
                        "message": f"{payload.get('kind', 'request').upper()} request plan saved.",
                        "plan_path": str(output_path.resolve()),
                        "plan": result,
                    })
                    return
                if route == "/api/osm-preview":
                    boundary, bbox = normalize_boundary(payload.get("boundary") or read_json(boundary_path, {}))
                    result = fetch_osm_preview(bbox, osm_preview_cache)
                    result["model_settings"] = normalize_model_settings(payload.get("model_settings"))
                    self._json(200, result)
                    return
                self.send_error(404)
            except json.JSONDecodeError:
                self._json(400, {"ok": False, "message": "invalid JSON request"})
            except Exception as error:
                self._json(400, {"ok": False, "message": str(error)})

        def log_message(self, *_args):
            return

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="open the selector in the default browser")
    args = parser.parse_args()
    skill_dir = Path(__file__).resolve().parents[1]
    app_dir = skill_dir / "assets" / "site-app"
    if not (app_dir / "index.html").exists():
        raise SystemExit(f"missing site app: {app_dir}")
    data_dir = args.output_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(app_dir, data_dir, skill_dir / "scripts"))
    url = f"http://{args.host}:{server.server_port}/"
    print(f"SITE_APP_URL={url}", flush=True)
    print(f"DATA_DIR={data_dir}", flush=True)
    if args.open:
        threading.Timer(0.2, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
