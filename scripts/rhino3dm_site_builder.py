#!/usr/bin/env python3
"""Build a colored, terrain-draped .3dm site model with ordinary Python."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from rhino_site_builder import (
    AsciiGrid,
    ROAD_WIDTHS,
    _features,
    _line_parts,
    _number,
    _polygon_parts,
    _tag,
    load_manifest,
)


RUNTIME = Path(__file__).resolve().parent.parent / ".runtime" / "python"
if RUNTIME.is_dir() and str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))


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


def require_geometry_libraries():
    try:
        import rhino3dm  # type: ignore
    except ImportError as error:
        raise RuntimeError(
            "rhino3dm is missing. Run scripts/bootstrap_environment.py --install first."
        ) from error
    try:
        from shapely.geometry import LineString, Polygon, box
        from shapely.ops import triangulate, unary_union
    except ImportError as error:
        raise RuntimeError(
            "Shapely is required for continuous projected surfaces. Install shapely in the selected Python environment."
        ) from error
    return rhino3dm, LineString, Polygon, box, triangulate, unary_union


def _hex_color(value):
    value = str(value or "").lstrip("#")
    if len(value) != 6:
        value = "808080"
    try:
        return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4)) + (255,)
    except ValueError:
        return 128, 128, 128, 255


def model_settings(manifest):
    source = manifest.get("model_settings") or {}
    settings = {
        "default_building_height_m": float(
            source.get("default_building_height_m", DEFAULT_MODEL_SETTINGS["default_building_height_m"])
        ),
        "floor_height_m": float(source.get("floor_height_m", DEFAULT_MODEL_SETTINGS["floor_height_m"])),
        "height_scale": float(source.get("height_scale", DEFAULT_MODEL_SETTINGS["height_scale"])),
        "colors": dict(DEFAULT_MODEL_SETTINGS["colors"]),
        "visible_layers": dict(DEFAULT_MODEL_SETTINGS["visible_layers"]),
    }
    settings["colors"].update(source.get("colors") or {})
    settings["visible_layers"].update(source.get("visible_layers") or {})
    settings["default_building_height_m"] = min(max(settings["default_building_height_m"], 1.0), 300.0)
    settings["floor_height_m"] = min(max(settings["floor_height_m"], 2.0), 8.0)
    settings["height_scale"] = min(max(settings["height_scale"], 0.2), 3.0)
    return settings


def layer_definitions(settings):
    colors = settings["colors"]
    visible = settings["visible_layers"]
    return {
        "Site": ("#464e5a", True, 0.0),
        "Site::Terrain": (colors["terrain"], visible["terrain"], 0.0),
        "Site::Terrain::DEM Reference": ("#78808a", False, 0.0),
        "Site::Contours": (colors["contours"], visible["contours"], 0.0),
        "Site::OSM": ("#4b5b70", True, 0.0),
        "Site::OSM::Road Centerlines": (colors["roads"], visible["roads"], 0.0),
        "Site::OSM::Road Surfaces": (colors["roads"], visible["roads"], 0.0),
        "Site::OSM::Building Footprints": (colors["buildings"], visible["buildings"], 0.0),
        "Site::OSM::Building Masses": (colors["buildings"], visible["buildings"], 0.0),
        "Site::OSM::Water": (colors["water"], visible["water"], 0.15),
        "Site::OSM::Land Use": (colors["landuse"], visible["landuse"], 0.0),
        "Site::OSM::Places": ("#3d549e", True, 0.0),
    }


def create_layers_and_materials(r3d, model, settings):
    indices = {}
    material_indices = {}
    for path, (color_value, visible, transparency) in layer_definitions(settings).items():
        color = _hex_color(color_value)
        material = r3d.Material()
        material.Name = f"{path} material"
        material.DiffuseColor = color
        material.AmbientColor = color
        material.Transparency = transparency
        material_index = model.Materials.Add(material)
        material_indices[path] = material_index

        parent_path, _, name = path.rpartition("::")
        layer = r3d.Layer()
        layer.Name = name or path
        layer.Color = color
        layer.Visible = bool(visible)
        layer.RenderMaterialIndex = material_index
        if parent_path:
            layer.ParentLayerId = model.Layers.FindIndex(indices[parent_path]).Id
        indices[path] = model.Layers.Add(layer)
    return indices, material_indices


def attributes(r3d, layer_indices, material_indices, layer, name=None):
    attrs = r3d.ObjectAttributes()
    attrs.LayerIndex = layer_indices[layer]
    attrs.MaterialIndex = material_indices[layer]
    attrs.MaterialSource = r3d.ObjectMaterialSource.MaterialFromObject
    attrs.ColorSource = r3d.ObjectColorSource.ColorFromLayer
    if name:
        attrs.Name = name
    return attrs


def terrain_mesh(r3d, grid, rows, cols):
    mesh = r3d.Mesh()
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
            keys = (
                (row_pos, col_pos),
                (row_pos, col_pos + 1),
                (row_pos + 1, col_pos + 1),
                (row_pos + 1, col_pos),
            )
            if all(key in vertex for key in keys):
                mesh.Faces.AddFace(*(vertex[key] for key in keys))
    mesh.Normals.ComputeNormals()
    mesh.Compact()
    return mesh, vertex


def _interpolate(level, first, second):
    x1, y1, z1 = first
    x2, y2, z2 = second
    ratio = 0.5 if abs(z2 - z1) < 1e-12 else (level - z1) / (z2 - z1)
    return x1 + (x2 - x1) * ratio, y1 + (y2 - y1) * ratio, level


def contour_segments(grid, rows, cols, interval):
    levels = []
    level = math.ceil(grid.zmin / interval) * interval
    while level <= grid.zmax + 1e-9:
        levels.append(level)
        level += interval
    segments = []
    edge_pairs = ((0, 1), (1, 2), (2, 3), (3, 0))
    for row_pos in range(len(rows) - 1):
        for col_pos in range(len(cols) - 1):
            cells = (
                (rows[row_pos], cols[col_pos]),
                (rows[row_pos], cols[col_pos + 1]),
                (rows[row_pos + 1], cols[col_pos + 1]),
                (rows[row_pos + 1], cols[col_pos]),
            )
            points = []
            for row, col in cells:
                z = grid.values[row][col]
                if not grid.is_valid(z):
                    points = []
                    break
                x, y = grid.xy(row, col)
                points.append((x - grid.origin_x, y - grid.origin_y, z))
            if not points:
                continue
            for current_level in levels:
                hits = []
                for first_index, second_index in edge_pairs:
                    first, second = points[first_index], points[second_index]
                    if (first[2] <= current_level < second[2]) or (second[2] <= current_level < first[2]):
                        hits.append(_interpolate(current_level, first, second))
                if len(hits) == 2:
                    segments.append(hits)
                elif len(hits) == 4:
                    segments.extend((hits[:2], hits[2:]))
    return segments


def _polygon_geometries(geometry):
    if geometry is None or geometry.is_empty:
        return []
    if geometry.geom_type == "Polygon":
        return [geometry]
    if geometry.geom_type == "MultiPolygon":
        return list(geometry.geoms)
    if geometry.geom_type == "GeometryCollection":
        return [item for item in geometry.geoms if item.geom_type == "Polygon"]
    return []


def _append_triangle(r3d, mesh, grid, coords, lift=0.0, flat_z=None):
    points = []
    for x, y in coords[:3]:
        z = flat_z if flat_z is not None else grid.sample(float(x), float(y))
        if z is None:
            return False
        points.append((float(x) - grid.origin_x, float(y) - grid.origin_y, float(z) + lift))
    start = len(mesh.Vertices)
    for point in points:
        mesh.Vertices.Add(*point)
    mesh.Faces.AddFace(start, start + 1, start + 2)
    return True


def projected_surface_mesh(r3d, geometry, grid, box, triangulate, step, lift=0.0, flat_z=None):
    """Split a polygon by the DEM grid, triangulate it, and return one joined mesh."""
    mesh = r3d.Mesh()
    geometry = geometry.buffer(0) if geometry and not geometry.is_valid else geometry
    if geometry is None or geometry.is_empty:
        return mesh, 0
    min_x, min_y, max_x, max_y = geometry.bounds
    start_x = math.floor(min_x / step) * step
    start_y = math.floor(min_y / step) * step
    face_count = 0
    x = start_x
    while x < max_x:
        y = start_y
        while y < max_y:
            clipped = geometry.intersection(box(x, y, x + step, y + step))
            for polygon in _polygon_geometries(clipped):
                for triangle in triangulate(polygon):
                    if not polygon.covers(triangle.representative_point()):
                        continue
                    if _append_triangle(
                        r3d,
                        mesh,
                        grid,
                        list(triangle.exterior.coords),
                        lift=lift,
                        flat_z=flat_z,
                    ):
                        face_count += 1
            y += step
        x += step
    if face_count:
        mesh.Normals.ComputeNormals()
        mesh.Compact()
    return mesh, face_count


def densify_line(coords, maximum_step):
    result = []
    for index in range(len(coords) - 1):
        first, second = coords[index], coords[index + 1]
        x1, y1 = float(first[0]), float(first[1])
        x2, y2 = float(second[0]), float(second[1])
        distance = math.hypot(x2 - x1, y2 - y1)
        pieces = max(1, int(math.ceil(distance / maximum_step)))
        for part in range(pieces):
            ratio = part / pieces
            point = (x1 + (x2 - x1) * ratio, y1 + (y2 - y1) * ratio)
            if not result or point != result[-1]:
                result.append(point)
    if coords:
        result.append((float(coords[-1][0]), float(coords[-1][1])))
    return result


def draped_polyline(r3d, grid, coords, maximum_step, lift):
    points = []
    for x, y in densify_line(coords, maximum_step):
        z = grid.sample(x, y)
        if z is not None:
            points.append(r3d.Point3d(x - grid.origin_x, y - grid.origin_y, z + lift))
    if len(points) < 2:
        return None
    return r3d.Polyline(points).ToPolylineCurve()


def polygon_from_parts(Polygon, polygon):
    if not polygon or len(polygon[0]) < 4:
        return None
    try:
        geometry = Polygon(polygon[0], polygon[1:])
        return geometry.buffer(0) if not geometry.is_valid else geometry
    except Exception:
        return None


def building_height(properties, settings):
    height = _number(_tag(properties, "height"))
    if height and height > 0:
        return height * settings["height_scale"], "height"
    levels = _number(_tag(properties, "building:levels"))
    if levels and levels > 0:
        return levels * settings["floor_height_m"] * settings["height_scale"], "levels"
    return settings["default_building_height_m"] * settings["height_scale"], "default"


def building_mass_mesh(r3d, geometry, grid, box, triangulate, height, projection_step):
    mesh = r3d.Mesh()
    base_points = []
    ring = densify_line(list(geometry.exterior.coords), projection_step)
    for x, y in ring[:-1]:
        z = grid.sample(x, y)
        if z is not None:
            base_points.append((x - grid.origin_x, y - grid.origin_y, z))
    if len(base_points) < 3:
        return mesh, 0
    top_z = max(point[2] for point in base_points) + height
    for index in range(len(base_points)):
        first = base_points[index]
        second = base_points[(index + 1) % len(base_points)]
        start = len(mesh.Vertices)
        for point in (
            first,
            second,
            (second[0], second[1], top_z),
            (first[0], first[1], top_z),
        ):
            mesh.Vertices.Add(*point)
        mesh.Faces.AddFace(start, start + 1, start + 2, start + 3)
    roof, roof_faces = projected_surface_mesh(
        r3d, geometry, grid, box, triangulate, projection_step, flat_z=top_z
    )
    if roof_faces:
        mesh.Append(roof)
    mesh.Normals.ComputeNormals()
    mesh.Compact()
    return mesh, len(mesh.Faces)


def build_site(manifest_path, output_3dm=None, diagnostic_path=None):
    r3d, LineString, Polygon, box, triangulate, unary_union = require_geometry_libraries()
    manifest_path, manifest = load_manifest(manifest_path)
    grid = AsciiGrid(manifest["derived_dem_asc"])
    precision = manifest.get("precision") or {}
    sample_step = float(precision.get("sample_step_m", grid.cell))
    contour_interval = float(precision.get("contour_interval_m", 10.0))
    projection_step = max(1.0, min(grid.cell, sample_step))
    rows, cols, stride = grid.index_lists(sample_step)
    settings = model_settings(manifest)

    model = r3d.File3dm()
    model.ApplicationName = "rhino-osm-terrain-modeling"
    model.ApplicationDetails = "Colored terrain-draped site model generated with rhino3dm"
    model.Settings.ModelUnitSystem = r3d.UnitSystem.Meters
    layer_indices, material_indices = create_layers_and_materials(r3d, model, settings)
    counts = {}

    def attrs(layer, name=None):
        return attributes(r3d, layer_indices, material_indices, layer, name)

    terrain, vertex = terrain_mesh(r3d, grid, rows, cols)
    if not vertex or len(terrain.Faces) == 0:
        raise RuntimeError("DEM sampling produced no terrain faces")
    model.Objects.AddMesh(terrain, attrs("Site::Terrain", "Terrain mesh"))
    model.Objects.AddMesh(terrain.Duplicate(), attrs("Site::Terrain::DEM Reference", "DEM reference mesh"))
    counts["terrain"] = 1
    counts["dem_reference"] = 1

    contours = 0
    for segment in contour_segments(grid, rows, cols, contour_interval):
        curve = r3d.Polyline([r3d.Point3d(*point) for point in segment]).ToPolylineCurve()
        model.Objects.AddCurve(curve, attrs("Site::Contours"))
        contours += 1
    counts["contours"] = contours

    vectors = manifest.get("derived_vectors") or {}
    road_centerlines = 0
    road_areas = []
    for feature in _features(vectors.get("roads", "")):
        properties = feature.get("properties") or {}
        road_class = str(_tag(properties, "highway", "road"))
        width = _number(_tag(properties, "width")) or ROAD_WIDTHS.get(road_class, 5.0)
        for coords in _line_parts(feature.get("geometry") or {}):
            line_coords = [(float(point[0]), float(point[1])) for point in coords if len(point) >= 2]
            if len(line_coords) < 2:
                continue
            curve = draped_polyline(r3d, grid, line_coords, projection_step, 0.16)
            if curve:
                model.Objects.AddCurve(curve, attrs("Site::OSM::Road Centerlines"))
                road_centerlines += 1
            try:
                road_areas.append(LineString(line_coords).buffer(width * 0.5, cap_style=2, join_style=2))
            except Exception:
                continue
    road_surfaces = 0
    road_faces = 0
    if road_areas:
        road_geometry = unary_union(road_areas)
        road_mesh, road_faces = projected_surface_mesh(
            r3d, road_geometry, grid, box, triangulate, projection_step, lift=0.12
        )
        if road_faces:
            model.Objects.AddMesh(road_mesh, attrs("Site::OSM::Road Surfaces", "Continuous road surface"))
            road_surfaces = 1
    counts["road_centerlines"] = road_centerlines
    counts["road_surfaces"] = road_surfaces
    counts["road_surface_faces"] = road_faces

    footprints = masses = 0
    height_sources = {"height": 0, "levels": 0, "default": 0}
    for feature in _features(vectors.get("buildings", "")):
        properties = feature.get("properties") or {}
        height, height_source = building_height(properties, settings)
        for polygon in _polygon_parts(feature.get("geometry") or {}):
            geometry = polygon_from_parts(Polygon, polygon)
            if geometry is None or geometry.is_empty:
                continue
            for part in _polygon_geometries(geometry):
                curve = draped_polyline(
                    r3d, grid, list(part.exterior.coords), projection_step, 0.08
                )
                if curve:
                    model.Objects.AddCurve(curve, attrs("Site::OSM::Building Footprints"))
                    footprints += 1
                mass, face_count = building_mass_mesh(
                    r3d, part, grid, box, triangulate, height, projection_step
                )
                if face_count:
                    model.Objects.AddMesh(mass, attrs("Site::OSM::Building Masses"))
                    masses += 1
                    height_sources[height_source] += 1
    counts["building_footprints"] = footprints
    counts["building_masses"] = masses
    counts["building_height_sources"] = height_sources

    for key, layer, lift in (
        ("water", "Site::OSM::Water", 0.10),
        ("landuse", "Site::OSM::Land Use", 0.06),
    ):
        geometries = []
        source_features = 0
        for feature in _features(vectors.get(key, "")):
            for polygon in _polygon_parts(feature.get("geometry") or {}):
                geometry = polygon_from_parts(Polygon, polygon)
                if geometry is not None and not geometry.is_empty:
                    geometries.append(geometry)
                    source_features += 1
        surface_objects = surface_faces = 0
        if geometries:
            merged = unary_union(geometries)
            surface, surface_faces = projected_surface_mesh(
                r3d, merged, grid, box, triangulate, projection_step, lift=lift
            )
            if surface_faces:
                model.Objects.AddMesh(surface, attrs(layer, f"{key.title()} projected surface"))
                surface_objects = 1
        counts[key] = source_features
        counts[f"{key}_surface_objects"] = surface_objects
        counts[f"{key}_surface_faces"] = surface_faces

    place_count = 0
    for feature in _features(vectors.get("places", "")):
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates") or []
        if geometry.get("type") == "Point" and len(coordinates) >= 2:
            x, y = float(coordinates[0]), float(coordinates[1])
            z = grid.sample(x, y)
            if z is not None:
                model.Objects.AddPoint(
                    r3d.Point3d(x - grid.origin_x, y - grid.origin_y, z),
                    attrs("Site::OSM::Places"),
                )
                place_count += 1
    counts["places"] = place_count

    output_3dm = Path(output_3dm or manifest_path.with_name("site_model.3dm")).resolve()
    diagnostic_path = Path(diagnostic_path or manifest_path.with_name("rhino_build_report.json")).resolve()
    output_3dm.parent.mkdir(parents=True, exist_ok=True)
    saved = model.Write(str(output_3dm), 8)
    report = {
        "ok": bool(saved and output_3dm.is_file() and output_3dm.stat().st_size > 0),
        "schema": "rhino-osm-terrain/build-report-v4",
        "backend": "rhino3dm-headless",
        "rhino3dm_version": getattr(r3d, "__version__", None),
        "manifest": str(manifest_path),
        "output_3dm": str(output_3dm),
        "output_bytes": output_3dm.stat().st_size if output_3dm.is_file() else 0,
        "units": "Meters",
        "crs": manifest.get("horizontal_crs"),
        "local_origin_projected": [grid.origin_x, grid.origin_y],
        "terrain_method": "mesh",
        "terrain_z_range_m": [grid.zmin, grid.zmax],
        "sample_stride": stride,
        "projection_step_m": projection_step,
        "contour_interval_m": contour_interval,
        "model_settings": settings,
        "materials": {
            path: {"color": value[0], "visible": value[1], "transparency": value[2]}
            for path, value in layer_definitions(settings).items()
        },
        "object_counts": counts,
        "limitations": [
            "Headless output uses terrain and projected feature meshes; use RhinoCommon for NURBS-only workflows.",
            "Contours are marching-squares line segments and are not joined automatically.",
            "Road surfaces are buffered and unioned before DEM-grid projection; source centerlines remain separate curves.",
            "Building height uses OSM height, then building:levels, then the configured default height.",
            "The DEM native resolution limits real terrain accuracy.",
        ],
    }
    diagnostic_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if not report["ok"]:
        raise RuntimeError(f"Failed to write .3dm: {output_3dm}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--diagnostic", type=Path)
    args = parser.parse_args()
    report = build_site(args.manifest, args.output, args.diagnostic)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
