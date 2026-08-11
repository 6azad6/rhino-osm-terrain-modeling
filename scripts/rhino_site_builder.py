#!/usr/bin/env python3
"""Build a metric Rhino site model from a prepared site manifest.

Run this file with Rhino 8 Python for geometry creation. Standard Python can
run ``--inspect`` to validate the manifest and ASCII DEM before Rhino opens.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


HEADER_KEYS = {"ncols", "nrows", "xllcorner", "xllcenter", "yllcorner", "yllcenter", "cellsize", "nodata_value"}
ROAD_WIDTHS = {
    "motorway": 14.0,
    "trunk": 12.0,
    "primary": 10.0,
    "secondary": 8.0,
    "tertiary": 7.0,
    "residential": 6.0,
    "service": 4.0,
    "footway": 2.0,
    "path": 1.5,
    "cycleway": 2.5,
}


class AsciiGrid:
    def __init__(self, path):
        self.path = Path(path)
        self.header, self.values = self._read()
        self.ncols = int(self.header["ncols"])
        self.nrows = int(self.header["nrows"])
        self.cell = float(self.header["cellsize"])
        self.nodata = self.header.get("nodata_value")
        self.x0 = float(self.header.get("xllcenter", self.header.get("xllcorner", 0.0)))
        self.y0 = float(self.header.get("yllcenter", self.header.get("yllcorner", 0.0)))
        self.x_center0 = self.x0 if "xllcenter" in self.header else self.x0 + self.cell * 0.5
        self.y_center0 = self.y0 if "yllcenter" in self.header else self.y0 + self.cell * 0.5
        self.origin_x = self.x_center0 + (self.ncols - 1) * self.cell * 0.5
        self.origin_y = self.y_center0 + (self.nrows - 1) * self.cell * 0.5
        valid = [value for row in self.values for value in row if self.is_valid(value)]
        if not valid:
            raise ValueError("DEM contains no valid elevations")
        self.zmin, self.zmax = min(valid), max(valid)

    def _read(self):
        lines = self.path.read_text(encoding="utf-8", errors="replace").splitlines()
        header, data_lines = {}, []
        reading_data = False
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            parts = line.split()
            key = parts[0].lower()
            if not reading_data and key in HEADER_KEYS and len(parts) >= 2:
                header[key] = float(parts[1])
            else:
                reading_data = True
                data_lines.append(line)
        if "ncols" not in header or "nrows" not in header or "cellsize" not in header:
            raise ValueError("DEM is missing ncols, nrows, or cellsize")
        ncols, nrows = int(header["ncols"]), int(header["nrows"])
        values = [[float(token) for token in line.split()] for line in data_lines]
        if len(values) != nrows or any(len(row) != ncols for row in values):
            raise ValueError(f"DEM dimensions do not match header: expected {nrows} x {ncols}")
        return header, values

    def is_valid(self, value):
        return math.isfinite(value) and (self.nodata is None or abs(value - self.nodata) > 1e-9)

    def xy(self, row, col):
        x = self.x_center0 + col * self.cell
        y = self.y_center0 + (self.nrows - 1 - row) * self.cell
        return x, y

    def sample(self, x, y):
        col = int(round((x - self.x_center0) / self.cell))
        row_from_south = int(round((y - self.y_center0) / self.cell))
        row = self.nrows - 1 - row_from_south
        if row < 0 or row >= self.nrows or col < 0 or col >= self.ncols:
            return None
        value = self.values[row][col]
        return value if self.is_valid(value) else None

    def index_lists(self, sample_step):
        stride = max(1, int(round(float(sample_step) / self.cell)))
        rows = list(range(0, self.nrows, stride))
        cols = list(range(0, self.ncols, stride))
        if rows[-1] != self.nrows - 1:
            rows.append(self.nrows - 1)
        if cols[-1] != self.ncols - 1:
            cols.append(self.ncols - 1)
        return rows, cols, stride


def load_manifest(path):
    path = Path(path).resolve()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not str(payload.get("schema", "")).startswith("rhino-osm-terrain/site-manifest-"):
        raise ValueError("unsupported site manifest schema")
    return path, payload


def inspect_manifest(path):
    manifest_path, manifest = load_manifest(path)
    dem_path = Path(manifest["derived_dem_asc"])
    grid = AsciiGrid(dem_path)
    vectors = manifest.get("derived_vectors") or {}
    precision = manifest.get("precision") or {}
    rows, cols, stride = grid.index_lists(precision.get("sample_step_m", grid.cell))
    return {
        "ok": True,
        "manifest": str(manifest_path),
        "crs": manifest.get("horizontal_crs"),
        "dem": {
            "path": str(dem_path),
            "ncols": grid.ncols,
            "nrows": grid.nrows,
            "cellsize": grid.cell,
            "zmin": grid.zmin,
            "zmax": grid.zmax,
            "sample_stride": stride,
            "sampled_grid": [len(rows), len(cols)],
        },
        "vectors": {key: {"path": value, "exists": Path(value).exists()} for key, value in vectors.items()},
        "warnings": manifest.get("warnings") or [],
    }


def _tag(properties, key, default=None):
    value = properties.get(key)
    if value not in (None, ""):
        return value
    other = str(properties.get("other_tags") or properties.get("all_tags") or "")
    match = re.search(rf'"{re.escape(key)}"=>"([^"]*)"', other)
    return match.group(1) if match else default


def _number(value):
    if value in (None, ""):
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value))
    return float(match.group(0)) if match else None


def _features(path):
    if not path:
        return []
    path = Path(path)
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("features") or []


def _line_parts(geometry):
    kind, coords = geometry.get("type"), geometry.get("coordinates") or []
    if kind == "LineString":
        return [coords]
    if kind == "MultiLineString":
        return coords
    return []


def _polygon_parts(geometry):
    kind, coords = geometry.get("type"), geometry.get("coordinates") or []
    if kind == "Polygon":
        return [coords]
    if kind == "MultiPolygon":
        return coords
    return []


def build_site(manifest_path, output_3dm=None, diagnostic_path=None, doc=None):
    try:
        import Rhino
        import scriptcontext
        from System.Drawing import Color
    except ImportError as error:  # pragma: no cover - requires Rhino
        raise RuntimeError("Run geometry creation with Rhino 8 Python, or use --inspect in standard Python") from error

    manifest_path, manifest = load_manifest(manifest_path)
    grid = AsciiGrid(manifest["derived_dem_asc"])
    doc = doc or scriptcontext.doc
    doc.ModelUnitSystem = Rhino.UnitSystem.Meters
    precision = manifest.get("precision") or {}
    sample_step = float(precision.get("sample_step_m", grid.cell))
    contour_interval = float(precision.get("contour_interval_m", 10.0))
    tolerance = float(precision.get("curve_tolerance_m", 0.25))
    counts = {}

    colors = {
        "Site": Color.FromArgb(70, 78, 90),
        "Site::Terrain": Color.FromArgb(105, 126, 97),
        "Site::Terrain::DEM Reference": Color.FromArgb(120, 128, 138),
        "Site::Contours": Color.FromArgb(92, 110, 83),
        "Site::OSM": Color.FromArgb(75, 91, 112),
        "Site::OSM::Road Centerlines": Color.FromArgb(206, 132, 72),
        "Site::OSM::Road Surfaces": Color.FromArgb(155, 142, 124),
        "Site::OSM::Building Footprints": Color.FromArgb(92, 101, 117),
        "Site::OSM::Building Masses": Color.FromArgb(184, 192, 202),
        "Site::OSM::Water": Color.FromArgb(73, 132, 176),
        "Site::OSM::Land Use": Color.FromArgb(113, 144, 100),
        "Site::OSM::Places": Color.FromArgb(61, 84, 158),
    }

    def layer_index(path):
        parent_id = Rhino.DocObjects.Layer.UnsetLayerId
        parts, full = path.split("::"), []
        index = -1
        for part in parts:
            full.append(part)
            full_path = "::".join(full)
            index = doc.Layers.FindByFullPath(full_path, True)
            if index < 0:
                layer = Rhino.DocObjects.Layer()
                layer.Name = part
                layer.Color = colors.get(full_path, Color.Gray)
                if parent_id != Rhino.DocObjects.Layer.UnsetLayerId:
                    layer.ParentLayerId = parent_id
                index = doc.Layers.Add(layer)
            parent_id = doc.Layers[index].Id
        return index

    layer_ids = {name: layer_index(name) for name in colors}
    attrs = Rhino.DocObjects.ObjectAttributes

    def add_geometry(geometry, layer):
        attributes = attrs()
        attributes.LayerIndex = layer_ids[layer]
        if isinstance(geometry, Rhino.Geometry.Brep):
            return doc.Objects.AddBrep(geometry, attributes)
        if isinstance(geometry, Rhino.Geometry.Extrusion):
            return doc.Objects.AddExtrusion(geometry, attributes)
        if isinstance(geometry, Rhino.Geometry.Mesh):
            return doc.Objects.AddMesh(geometry, attributes)
        if isinstance(geometry, Rhino.Geometry.Curve):
            return doc.Objects.AddCurve(geometry, attributes)
        if isinstance(geometry, Rhino.Geometry.Point3d):
            return doc.Objects.AddPoint(geometry, attributes)
        return None

    rows, cols, stride = grid.index_lists(sample_step)
    mesh = Rhino.Geometry.Mesh()
    vertex = {}
    for row_pos, row in enumerate(rows):
        for col_pos, col in enumerate(cols):
            z = grid.values[row][col]
            if not grid.is_valid(z):
                continue
            x, y = grid.xy(row, col)
            vertex[(row_pos, col_pos)] = mesh.Vertices.Add(x - grid.origin_x, y - grid.origin_y, z)
    for row_pos in range(len(rows) - 1):
        for col_pos in range(len(cols) - 1):
            keys = [(row_pos, col_pos), (row_pos, col_pos + 1), (row_pos + 1, col_pos + 1), (row_pos + 1, col_pos)]
            if all(key in vertex for key in keys):
                mesh.Faces.AddFace(*(vertex[key] for key in keys))
    mesh.Normals.ComputeNormals()
    mesh.Compact()
    add_geometry(mesh.DuplicateMesh(), "Site::Terrain::DEM Reference")
    reference_layer = doc.Layers[layer_ids["Site::Terrain::DEM Reference"]]
    reference_layer.IsVisible = False
    reference_layer.CommitChanges()

    terrain_method = "mesh"
    complete_grid = len(vertex) == len(rows) * len(cols) and len(rows) >= 4 and len(cols) >= 4
    if complete_grid:
        points = []
        for row in rows:
            for col in cols:
                x, y = grid.xy(row, col)
                points.append(Rhino.Geometry.Point3d(x - grid.origin_x, y - grid.origin_y, grid.values[row][col]))
        try:
            surface = Rhino.Geometry.NurbsSurface.CreateThroughPoints(
                points, len(cols), len(rows), min(3, len(cols) - 1), min(3, len(rows) - 1), False, False
            )
            if surface:
                add_geometry(surface.ToBrep(), "Site::Terrain")
                terrain_method = "nurbs-through-points"
        except Exception:
            surface = None
    if terrain_method == "mesh":
        add_geometry(mesh.DuplicateMesh(), "Site::Terrain")
    counts["terrain"] = 1
    counts["dem_reference"] = 1

    contour_count = 0
    try:
        start = Rhino.Geometry.Point3d(0, 0, math.floor(grid.zmin / contour_interval) * contour_interval)
        end = Rhino.Geometry.Point3d(0, 0, math.ceil(grid.zmax / contour_interval) * contour_interval)
        curves = Rhino.Geometry.Mesh.CreateContourCurves(mesh, start, end, contour_interval, tolerance)
        for curve in curves or []:
            add_geometry(curve, "Site::Contours")
            contour_count += 1
    except Exception:
        pass
    counts["contours"] = contour_count

    def point3(coord, lift=0.0):
        if not isinstance(coord, (list, tuple)) or len(coord) < 2:
            return None
        x, y = float(coord[0]), float(coord[1])
        z = grid.sample(x, y)
        if z is None:
            return None
        return Rhino.Geometry.Point3d(x - grid.origin_x, y - grid.origin_y, z + lift)

    def curve_from_coords(coords, lift=0.0, close=False, flat_z=None):
        points = []
        for coord in coords:
            point = point3(coord, lift)
            if point is None:
                continue
            if flat_z is not None:
                point.Z = flat_z
            points.append(point)
        if close and points and points[0].DistanceTo(points[-1]) > tolerance:
            points.append(points[0])
        return Rhino.Geometry.PolylineCurve(points) if len(points) >= (4 if close else 2) else None

    def road_mesh(coords, width):
        center = [point3(coord, 0.18) for coord in coords]
        center = [point for point in center if point is not None]
        if len(center) < 2:
            return None
        result = Rhino.Geometry.Mesh()
        half = width * 0.5
        for index, point in enumerate(center):
            before = center[max(0, index - 1)]
            after = center[min(len(center) - 1, index + 1)]
            dx, dy = after.X - before.X, after.Y - before.Y
            length = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / length * half, dx / length * half
            result.Vertices.Add(point.X + nx, point.Y + ny, point.Z)
            result.Vertices.Add(point.X - nx, point.Y - ny, point.Z)
        for index in range(len(center) - 1):
            result.Faces.AddFace(index * 2, index * 2 + 1, index * 2 + 3, index * 2 + 2)
        result.Normals.ComputeNormals()
        return result

    vectors = manifest.get("derived_vectors") or {}
    road_centerlines = road_surfaces = 0
    for feature in _features(vectors.get("roads", "")):
        properties = feature.get("properties") or {}
        road_class = str(_tag(properties, "highway", "road"))
        width = _number(_tag(properties, "width")) or ROAD_WIDTHS.get(road_class, 5.0)
        for coords in _line_parts(feature.get("geometry") or {}):
            curve = curve_from_coords(coords, 0.2)
            if curve:
                add_geometry(curve, "Site::OSM::Road Centerlines")
                road_centerlines += 1
            ribbon = road_mesh(coords, width)
            if ribbon:
                add_geometry(ribbon, "Site::OSM::Road Surfaces")
                road_surfaces += 1
    counts["road_centerlines"] = road_centerlines
    counts["road_surfaces"] = road_surfaces

    footprints = masses = 0
    for feature in _features(vectors.get("buildings", "")):
        properties = feature.get("properties") or {}
        height = _number(_tag(properties, "height"))
        if height is None:
            levels = _number(_tag(properties, "building:levels"))
            height = levels * 3.0 if levels else None
        for polygon in _polygon_parts(feature.get("geometry") or {}):
            if not polygon:
                continue
            outer = curve_from_coords(polygon[0], 0.1, close=True)
            if outer:
                add_geometry(outer, "Site::OSM::Building Footprints")
                footprints += 1
            for hole in polygon[1:]:
                hole_curve = curve_from_coords(hole, 0.1, close=True)
                if hole_curve:
                    add_geometry(hole_curve, "Site::OSM::Building Footprints")
                    footprints += 1
            if height and len(polygon) == 1:
                samples = [point3(coord) for coord in polygon[0]]
                samples = [point for point in samples if point is not None]
                base_z = sum(point.Z for point in samples) / len(samples) if samples else None
                base = curve_from_coords(polygon[0], close=True, flat_z=base_z) if base_z is not None else None
                extrusion = Rhino.Geometry.Extrusion.Create(base, height, True) if base else None
                if extrusion:
                    add_geometry(extrusion, "Site::OSM::Building Masses")
                    masses += 1
    counts["building_footprints"] = footprints
    counts["building_masses"] = masses

    for key, layer in (("water", "Site::OSM::Water"), ("landuse", "Site::OSM::Land Use")):
        count = 0
        for feature in _features(vectors.get(key, "")):
            for polygon in _polygon_parts(feature.get("geometry") or {}):
                for ring in polygon:
                    curve = curve_from_coords(ring, 0.12, close=True)
                    if curve:
                        add_geometry(curve, layer)
                        count += 1
        counts[key] = count

    place_count = 0
    for feature in _features(vectors.get("places", "")):
        geometry = feature.get("geometry") or {}
        if geometry.get("type") == "Point":
            point = point3(geometry.get("coordinates") or [])
            if point:
                add_geometry(point, "Site::OSM::Places")
                place_count += 1
    counts["places"] = place_count

    output_3dm = Path(output_3dm or manifest_path.with_name("site_model.3dm")).resolve()
    diagnostic_path = Path(diagnostic_path or manifest_path.with_name("rhino_build_report.json")).resolve()
    output_3dm.parent.mkdir(parents=True, exist_ok=True)
    options = Rhino.FileIO.FileWriteOptions()
    options.WriteSelectedObjectsOnly = False
    saved = doc.WriteFile(str(output_3dm), options)
    report = {
        "ok": bool(saved),
        "schema": "rhino-osm-terrain/build-report-v2",
        "manifest": str(manifest_path),
        "output_3dm": str(output_3dm),
        "units": str(doc.ModelUnitSystem),
        "crs": manifest.get("horizontal_crs"),
        "local_origin_projected": [grid.origin_x, grid.origin_y],
        "terrain_method": terrain_method,
        "terrain_z_range_m": [grid.zmin, grid.zmax],
        "sample_stride": stride,
        "contour_interval_m": contour_interval,
        "object_counts": counts,
        "limitations": [
            "Road widths use OSM width when present, otherwise a documented class default.",
            "Buildings without OSM height or levels remain footprints.",
            "The DEM native resolution limits real terrain accuracy.",
        ],
    }
    diagnostic_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    doc.Views.Redraw()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--diagnostic", type=Path)
    parser.add_argument("--inspect", action="store_true", help="validate inputs without importing Rhino")
    args = parser.parse_args()
    report = inspect_manifest(args.manifest) if args.inspect else build_site(args.manifest, args.output, args.diagnostic)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
