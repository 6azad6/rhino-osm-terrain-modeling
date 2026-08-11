#!/usr/bin/env python3
"""Fetch a clipped-area OSM XML extract from a public Overpass endpoint.

The script deliberately uses a bounding-box query and leaves the final
geometric clipping to the local preparation stage. It does not require an
OSM account, but callers must respect the selected endpoint's fair-use limits.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


def _walk_coords(value, bbox):
    if isinstance(value, (list, tuple)) and value:
        if isinstance(value[0], (int, float)):
            if len(value) >= 2:
                bbox[0] = min(bbox[0], float(value[0]))
                bbox[1] = min(bbox[1], float(value[1]))
                bbox[2] = max(bbox[2], float(value[0]))
                bbox[3] = max(bbox[3], float(value[1]))
            return
        for child in value:
            _walk_coords(child, bbox)


def boundary_bbox(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    bbox = [float("inf"), float("inf"), float("-inf"), float("-inf")]
    if payload.get("type") == "FeatureCollection":
        features = payload.get("features") or []
    elif payload.get("type") == "Feature":
        features = [payload]
    else:
        features = [{"geometry": payload}]
    for feature in features:
        geometry = feature.get("geometry", feature)
        _walk_coords(geometry.get("coordinates"), bbox)
    if bbox[0] == float("inf"):
        raise ValueError("boundary GeoJSON contains no coordinates")
    return bbox


def build_query(bbox, timeout_s=180):
    west, south, east, north = bbox
    box = f"{south:.8f},{west:.8f},{north:.8f},{east:.8f}"
    return f'''[out:xml][timeout:{int(timeout_s)}];
(
  way["highway"]({box});
  way["building"]({box});
  relation["building"]({box});
  way["waterway"]({box});
  way["natural"="water"]({box});
  relation["natural"="water"]({box});
  way["landuse"]({box});
  relation["landuse"]({box});
  node["place"]({box});
);
(._;>;);
out body;
'''


def fetch(endpoint, query, timeout_s, user_agent):
    body = urllib.parse.urlencode({"data": query}).encode("utf-8")
    request = urllib.request.Request(endpoint, data=body, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    request.add_header("User-Agent", user_agent)
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        return response.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("boundary", type=Path, help="WGS84 GeoJSON boundary")
    parser.add_argument("--output", type=Path, default=Path("data/source_osm.osm"))
    parser.add_argument("--endpoint", action="append", help="Overpass endpoint; repeat for fallback")
    parser.add_argument("--timeout-s", type=int, default=180)
    parser.add_argument("--request-timeout-s", type=int, default=240)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--user-agent", default="codex-rhino-osm-terrain/1.0")
    parser.add_argument("--dry-run", action="store_true", help="print query metadata without network access")
    args = parser.parse_args()

    bbox = boundary_bbox(args.boundary)
    query = build_query(bbox, args.timeout_s)
    endpoints = args.endpoint or DEFAULT_ENDPOINTS
    width_km = abs(bbox[2] - bbox[0]) * 111.32
    height_km = abs(bbox[3] - bbox[1]) * 110.54
    report = {
        "provider": "overpass",
        "endpoints": endpoints,
        "bbox_wgs84": bbox,
        "approx_area_km2": width_km * height_km,
        "boundary_path": str(args.boundary.resolve()),
        "query": query,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    if report["approx_area_km2"] > 2500:
        report["warning"] = "Large area: use a Geofabrik PBF extract instead of Overpass when possible."
    if args.dry_run:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    data = None
    used_endpoint = None
    for endpoint in endpoints:
        for attempt in range(max(1, args.retries + 1)):
            try:
                data = fetch(endpoint, query, args.request_timeout_s, args.user_agent)
                used_endpoint = endpoint
                break
            except Exception as error:  # pragma: no cover - endpoint dependent
                errors.append({"endpoint": endpoint, "attempt": attempt + 1, "error": str(error)})
                if attempt < args.retries:
                    time.sleep(2 ** attempt)
        if data is not None:
            break
    if data is None:
        report["ok"] = False
        report["errors"] = errors
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    if b"<osm" not in data[:1000]:
        report["ok"] = False
        report["error"] = "Overpass returned a non-OSM response"
        report["response_preview"] = data[:300].decode("utf-8", errors="replace")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    args.output.write_bytes(data)
    report.update({
        "ok": True,
        "endpoint_used": used_endpoint,
        "output": str(args.output.resolve()),
        "bytes": len(data),
    })
    metadata_path = args.output.with_suffix(args.output.suffix + ".json")
    metadata_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
