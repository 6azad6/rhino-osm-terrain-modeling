#!/usr/bin/env python3
"""Serve the lightweight Rhino site selector and persist its local state."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


PRECISION_SCALE = {"draft": 30.0, "standard": 10.0, "fine": 3.0}
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
