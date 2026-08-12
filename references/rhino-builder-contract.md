# Rhino Builder Contract

Use `scripts/rhino3dm_site_builder.py` as the default ordinary-Python `.3dm` builder. Keep `scripts/rhino_site_builder.py` as the optional Rhino 8/RhinoCommon enhancement backend.

## Inputs and execution

1. Run `python scripts/rhino_site_builder.py <manifest> --inspect` to validate the package.
2. Run `python scripts/rhino3dm_site_builder.py <manifest>` in ordinary Python.
3. Set the file model units to meters before adding objects.
4. Write the `.3dm`, then write a diagnostic that confirms the file exists and is nonempty.
5. Use the RhinoCommon launcher only for requested NURBS enhancement or Rhino visual review.

## Geometry policy

- Recenter all projected coordinates around the DEM grid center. Record the original easting/northing in the report.
- Keep `Site::Terrain`, hidden `Site::Terrain::DEM Reference`, `Site::Contours`, and separate OSM sublayers. Write the configured layer colors and object materials into the `.3dm`; do not rely on display defaults.
- Create a terrain mesh for the headless deliverable. The optional RhinoCommon backend may create a NURBS terrain through complete sampled grids.
- Generate contours at the manifest interval. Record that headless contours are unjoined marching-squares segments.
- Densify road centerlines, buffer them in projected 2D, union connected road surfaces, split them against the DEM grid, and triangulate one continuous terrain-projected road mesh. Preserve source centerlines as curves.
- Use OSM `width` when available, otherwise the documented highway-class defaults in the builder.
- Resolve building height from OSM `height`, then `building:levels * floor_height_m`, then the configured default height. Apply `height_scale` last and report every height source.
- Build each mass with DEM-sampled wall feet and a level roof. Preserve polygon holes in roof triangulation and footprint curves.
- Union water and land-use polygons by category, split them against the DEM grid, and triangulate each category into one terrain-projected mesh object where data exists.
- Respect `model_settings.visible_layers`. Keep layer visibility and material colors consistent with the Studio; use material transparency for water.

## Required diagnostics

Write `rhino_build_report.json` with units, CRS, local origin, terrain method, z range, sample stride, projection step, contour interval, model settings, material assignments, height sources, surface object/face counts, output path, limitations, and actual object counts. Zero objects in a requested class must remain visible in the report.

Treat any of these as failure: non-meter file units, missing terrain, zero road objects when the source contains roads, non-overlapping bounds, empty diagnostic, unsaved `.3dm`, or a reported output path that does not exist.
