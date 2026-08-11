# Rhino Builder Contract

Use `scripts/rhino_site_builder.py` as the single geometry implementation for Rhino 8 Python and Grasshopper triggers.

## Inputs and execution

1. Run `python scripts/rhino_site_builder.py <manifest> --inspect` outside Rhino to validate the package.
2. Run the same file with Rhino 8 Python and call `build_site(manifest_path, output_3dm, diagnostic_path)`.
3. Set the active document to meters before adding objects.
4. Save the `.3dm` only after the build report is written successfully.

## Geometry policy

- Recenter all projected coordinates around the DEM grid center. Record the original easting/northing in the report.
- Keep `Site::Terrain`, hidden `Site::Terrain::DEM Reference`, `Site::Contours`, and separate OSM sublayers.
- Create a NURBS terrain through complete sampled grids; use a visible mesh fallback when NoData prevents a rectangular surface.
- Generate contours from the reference mesh at the manifest interval.
- Drape road centerlines and ribbon vertices with the same DEM sampler used by terrain.
- Use OSM `width` when available, otherwise the documented highway-class defaults in the builder.
- Keep buildings as footprints unless OSM provides `height` or `building:levels`. Do not invent mass heights.
- Preserve polygon holes as curves. Extrude only simple single-ring building polygons.

## Required diagnostics

Write `rhino_build_report.json` with units, CRS, local origin, terrain method, z range, sample stride, contour interval, output path, limitations, and actual object counts. Zero objects in a requested class must remain visible in the report.

Treat any of these as failure: non-meter document units, missing terrain, zero road objects when the source contains roads, non-overlapping bounds, empty diagnostic, unsaved `.3dm`, or a reported output path that does not exist.
