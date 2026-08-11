#!/usr/bin/env python3
"""Create and optionally serve a Codex-friendly map selector.

The selector writes a user-drawn Polygon/MultiPolygon as GeoJSON.  The HTTP
mode is intentionally bound to localhost so a browser panel can post the
selection back to the same machine without exposing a public service.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


HTML_TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rhino terrain site selector</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
  <style>
    html, body, #map { height: 100%; margin: 0; }
    #panel { position: absolute; z-index: 1000; top: 12px; left: 52px;
      padding: 10px 12px; background: white; border-radius: 4px;
      box-shadow: 0 1px 6px #777; font: 14px sans-serif; }
    #status { margin-top: 6px; color: #444; max-width: 420px; }
    label { display: inline-block; margin: 0 8px 7px 0; }
    select, input { margin-left: 4px; }
    button { cursor: pointer; padding: 5px 10px; }
  </style>
</head>
<body>
  <div id="map"></div>
  <div id="panel">
    <div>
      <label>OSM <select id="osm"><option value="overpass">Overpass</option><option value="local">Local file</option></select></label>
      <label>Precision <select id="precision"><option value="draft">Draft</option><option value="standard" selected>Standard</option><option value="fine">Fine</option></select></label>
    </div>
    <div>
      <label>DEM <select id="dem"><option value="COPERNICUS/DEM/GLO30" selected>Copernicus GLO-30</option><option value="USGS/SRTMGL1_003">SRTM 30 m</option><option value="NASA/NASADEM_HGT/001">NASADEM</option><option value="local">Local file</option></select></label>
      <label>GEE project <input id="project" size="16" placeholder="optional project ID" /></label>
    </div>
    <button id="save">Confirm selection</button>
    <button id="clear">Clear</button>
    <div id="status">Draw a rectangle or polygon, then confirm.</div>
  </div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
  <script>
    const map = L.map('map').setView([__LAT__, __LON__], __ZOOM__);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    const drawn = new L.FeatureGroup().addTo(map);
    map.addControl(new L.Control.Draw({
      edit: { featureGroup: drawn },
      draw: { polyline: false, circle: false, circlemarker: false, marker: false }
    }));
    map.on(L.Draw.Event.CREATED, e => {
      drawn.clearLayers();
      drawn.addLayer(e.layer);
      document.getElementById('status').textContent = 'Selection ready.';
    });
    document.getElementById('clear').onclick = () => {
      drawn.clearLayers();
      document.getElementById('status').textContent = 'Draw a rectangle or polygon, then confirm.';
    };
    document.getElementById('save').onclick = async () => {
      const features = [];
      drawn.eachLayer(layer => features.push(layer.toGeoJSON()));
      if (!features.length) { alert('Draw a selection first.'); return; }
      const body = {
        boundary: { type: 'FeatureCollection', features: features },
        osm_provider: document.getElementById('osm').value,
        dem_dataset: document.getElementById('dem').value,
        gee_project: document.getElementById('project').value.trim() || null,
        precision_preset: document.getElementById('precision').value
      };
      try {
        const response = await fetch('/selection', {
          method: 'POST', headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(body)
        });
        const result = await response.json();
        document.getElementById('status').textContent = result.message || 'Saved.';
      } catch (error) {
        document.getElementById('status').textContent = 'Save failed: ' + error;
      }
    };
  </script>
</body>
</html>
'''


def _bbox_coords(coords, bbox):
    if isinstance(coords, (list, tuple)) and coords:
        if isinstance(coords[0], (int, float)):
            if len(coords) >= 2:
                bbox[0] = min(bbox[0], float(coords[0]))
                bbox[1] = min(bbox[1], float(coords[1]))
                bbox[2] = max(bbox[2], float(coords[0]))
                bbox[3] = max(bbox[3], float(coords[1]))
            return
        for child in coords:
            _bbox_coords(child, bbox)


def normalize_selection(payload):
    if payload.get("type") != "FeatureCollection":
        raise ValueError("selection must be a GeoJSON FeatureCollection")
    features = payload.get("features") or []
    if not features:
        raise ValueError("selection contains no features")
    kept = []
    bbox = [float("inf"), float("inf"), float("-inf"), float("-inf")]
    for feature in features:
        geometry = feature.get("geometry") or {}
        if geometry.get("type") not in ("Polygon", "MultiPolygon"):
            continue
        _bbox_coords(geometry.get("coordinates"), bbox)
        kept.append({"type": "Feature", "properties": feature.get("properties") or {}, "geometry": geometry})
    if not kept or bbox[0] == float("inf"):
        raise ValueError("draw a Polygon or MultiPolygon")
    return {"type": "FeatureCollection", "features": kept}, bbox


def make_html(lat, lon, zoom):
    return HTML_TEMPLATE.replace("__LAT__", str(lat)).replace("__LON__", str(lon)).replace("__ZOOM__", str(zoom))


def write_selector(output_dir: Path, lat: float, lon: float, zoom: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "site_selector.html"
    path.write_text(make_html(lat, lon, zoom), encoding="utf-8")
    return path


def serve(output_dir: Path, host: str, port: int):
    html = (output_dir / "site_selector.html").read_bytes()
    boundary_path = output_dir / "site_boundary.geojson"
    selection_path = output_dir / "site_selection.json"

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            route = urlparse(self.path).path
            if route in ("/", "/site_selector.html"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html)
                return
            if route == "/status":
                body = json.dumps({"selected": boundary_path.exists()}, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_error(404)

        def do_POST(self):  # noqa: N802
            if urlparse(self.path).path != "/selection":
                self.send_error(404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                normalized, bbox = normalize_selection(payload.get("boundary", payload))
                precision = payload.get("precision_preset", "standard")
                if precision not in ("draft", "standard", "fine"):
                    raise ValueError("precision_preset must be draft, standard, or fine")
                boundary_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
                selection_path.write_text(json.dumps({
                    "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "boundary_path": str(boundary_path.resolve()),
                    "bbox_wgs84": bbox,
                    "feature_count": len(normalized["features"]),
                    "osm_provider": payload.get("osm_provider", "overpass"),
                    "dem_dataset": payload.get("dem_dataset", "COPERNICUS/DEM/GLO30"),
                    "gee_project": payload.get("gee_project"),
                    "precision_preset": precision,
                }, ensure_ascii=False, indent=2), encoding="utf-8")
                body = json.dumps({"ok": True, "message": "Selection saved; you can return to Codex."}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)
            except Exception as error:  # pragma: no cover - exercised via browser
                body = json.dumps({"ok": False, "message": str(error)}).encode("utf-8")
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)

        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"SITE_SELECTOR_URL=http://{host}:{server.server_port}/", flush=True)
    print(f"BOUNDARY_PATH={boundary_path.resolve()}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    parser.add_argument("--lat", type=float, default=20.0)
    parser.add_argument("--lon", type=float, default=0.0)
    parser.add_argument("--zoom", type=int, default=2)
    parser.add_argument("--serve", action="store_true", help="serve the selector on localhost")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    path = write_selector(args.output_dir, args.lat, args.lon, args.zoom)
    print(f"SELECTOR_HTML={path.resolve()}")
    if args.serve:
        serve(args.output_dir, args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
