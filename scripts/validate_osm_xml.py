#!/usr/bin/env python3
"""Summarize a local OSM XML file and optionally check a site radius."""

from __future__ import annotations

import argparse
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path


def local_xy(lat, lon, origin_lat, origin_lon):
    x = (lon - origin_lon) * 111320.0 * math.cos(math.radians(origin_lat))
    y = (lat - origin_lat) * 110540.0
    return x, y


def summarize(path: Path, origin_lat=None, origin_lon=None, radius_m=None):
    root = ET.parse(str(path)).getroot()
    nodes = {}
    tagged_nodes = 0
    node_tags = {}
    for node in root.findall("node"):
        node_id = node.attrib.get("id")
        lat = float(node.attrib["lat"])
        lon = float(node.attrib["lon"])
        nodes[node_id] = (lat, lon)
        tags = {tag.attrib.get("k"): tag.attrib.get("v", "") for tag in node.findall("tag")}
        if tags:
            tagged_nodes += 1
            for key in tags:
                node_tags[key] = node_tags.get(key, 0) + 1

    ways = 0
    tagged_ways = 0
    categories = {}
    in_radius_ways = 0
    bbox = [float("inf"), float("inf"), float("-inf"), float("-inf")]

    def inside(lat, lon):
        if origin_lat is None or origin_lon is None or radius_m is None:
            return True
        x, y = local_xy(lat, lon, origin_lat, origin_lon)
        return x * x + y * y <= radius_m * radius_m

    for way in root.findall("way"):
        ways += 1
        tags = {tag.attrib.get("k"): tag.attrib.get("v", "") for tag in way.findall("tag")}
        if tags:
            tagged_ways += 1
        category = "other"
        if "highway" in tags:
            category = "highway"
        elif "building" in tags:
            category = "building"
        elif "waterway" in tags or tags.get("natural") == "water":
            category = "water"
        elif "landuse" in tags:
            category = "landuse"
        categories[category] = categories.get(category, 0) + 1

        coords = [nodes[nd.attrib["ref"]] for nd in way.findall("nd") if nd.attrib.get("ref") in nodes]
        if coords:
            for lat, lon in coords:
                bbox[0] = min(bbox[0], lon)
                bbox[1] = min(bbox[1], lat)
                bbox[2] = max(bbox[2], lon)
                bbox[3] = max(bbox[3], lat)
            if any(inside(lat, lon) for lat, lon in coords):
                in_radius_ways += 1

    result = {
        "path": str(path.resolve()),
        "node_count": len(nodes),
        "tagged_node_count": tagged_nodes,
        "way_count": ways,
        "tagged_way_count": tagged_ways,
        "way_categories": categories,
        "bbox_lon_lat": bbox if ways else None,
    }
    if radius_m is not None:
        result["center_lat"] = origin_lat
        result["center_lon"] = origin_lon
        result["radius_m"] = radius_m
        result["ways_with_any_point_inside_radius"] = in_radius_ways
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("osm", type=Path, help="local OSM XML path")
    parser.add_argument("--lat", type=float)
    parser.add_argument("--lon", type=float)
    parser.add_argument("--radius-m", type=float)
    args = parser.parse_args()
    if (args.lat is None or args.lon is None) != (args.radius_m is None):
        parser.error("provide --lat, --lon, and --radius-m together")
    report = summarize(args.osm, args.lat, args.lon, args.radius_m)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
