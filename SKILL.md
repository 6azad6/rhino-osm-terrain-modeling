---
name: rhino-osm-terrain-modeling
description: Build or repair reusable Heron-free Rhino 8 and Grasshopper site models from OpenStreetMap vectors and Google Earth Engine or local DEM data. Use for Codex world-map site selection, GeoJSON cropping, OSM/Overpass/Geofabrik acquisition, GEE DEM export, QGIS/GDAL preprocessing, adjustable terrain precision, roads/buildings/water/land-use draping, RhinoCommon geometry generation, diagnostics, and verified .3dm delivery.
---

# Rhino OSM Terrain Modeling

Create a repeatable site package through one pipeline:

```text
Codex map UI -> local Python acquisition -> GDAL/osmium normalization -> RhinoCommon build -> diagnostic
```

Do not require Heron. Keep browser selection, data acquisition, preprocessing, and Rhino geometry in separate layers. Read [workflow-contract.md](references/workflow-contract.md) before changing the workflow boundary.

## Operating Rules

- Prefer existing local OSM, PBF, GeoJSON, GeoTIFF, ASC, XYZ, or contour data. Do not request fresh network data when suitable local sources exist.
- Require a confirmed WGS84 boundary before any network request.
- Run acquisition dry first. Add `--run` only after the user confirms the boundary and providers.
- Use the user's local Earth Engine authorization. Never request or store passwords, tokens, or service-account JSON.
- Use a projected metric CRS for Rhino. Set the Rhino document to meters before adding geometry.
- Treat precision as processing density. Never describe interpolation below native DEM resolution as increased accuracy.
- Use `osmium` and GDAL's OSM driver for clipping and multipolygon assembly. Do not hand-roll relation rings.
- Preserve raw inputs. Write normalized files and manifests below the project data folder.
- Build all OSM z values from the same DEM sampler as the terrain.
- Finish with actual object counts, bounds, units, limitations, a saved `.3dm`, and a nonempty diagnostic JSON.

## Workflow

### 0. Run the first-use check

At the first invocation on a machine, run:

```powershell
python scripts/bootstrap_environment.py
```

If `reminder_needed` is true, summarize the detected tools and offer one action: install all missing open-source components. Use the command-execution approval prompt as the one-click action instead of asking the user to copy commands. Do not install until that approval is granted. Run `python scripts/bootstrap_environment.py --install` after approval; if the user declines, run it with `--acknowledge` so the reminder is not repeated. Never auto-install Rhino or initiate GEE authentication. Continue without optional `osmium` for small OSM XML sites.

### 1. Inspect inputs

Locate the project folder, existing boundary, OSM/DEM files, Rhino version, QGIS/GDAL/osmium tools, and Earth Engine environment. If local OSM and DEM are available, skip to preprocessing.

### 2. Select the site

Read [map-selection-contract.md](references/map-selection-contract.md) and [frontend-contract.md](references/frontend-contract.md) when the user wants selection inside Codex.

```powershell
python scripts/launch_site_app.py --output-dir <project>\data --port 0
```

Open the printed URL in the Codex in-app Browser when available. Let the user draw or load one boundary, choose providers and precision, then save. Verify `site_boundary.geojson` and `site_selection.json` before continuing.

### 3. Acquire data

Read [data-provider-contract.md](references/data-provider-contract.md). Create plans first:

```powershell
python scripts/acquire_site_data.py <project>\data\site_selection.json --out-dir <project>\data
```

Review the plan and add `--run` for a confirmed fresh download. Use `--authenticate` only when the user approves a local GEE authorization flow. Use `--osm-local` or `--dem-local` for existing files.

For individual providers, run `fetch_osm.py --dry-run` or `fetch_gee_dem.py --dry-run` before the real command. Use Overpass only for small selections; prefer local or Geofabrik PBF for large or repeated builds.

### 4. Normalize the package

Read [precision-contract.md](references/precision-contract.md) and [qgis-data-contract.md](references/qgis-data-contract.md).

```powershell
python scripts/prepare_site_data.py <boundary> --osm <source-osm> --dem <source-dem> --out-dir <project>\data\derived --crs auto --precision standard
```

Inspect `site_manifest.json` and its planned commands. Add `--run` after confirming the UTM/EPSG target and output paths. If command-line GDAL is unavailable, execute the equivalent steps in QGIS and retain the same filenames and manifest fields.

Validate the inputs:

```powershell
python scripts/validate_esri_ascii_dem.py <project>\data\derived\site_dem.asc
python scripts/validate_osm_xml.py <source-osm.osm>
python scripts/rhino_site_builder.py <project>\data\derived\site_manifest.json --inspect
```

Skip the XML validator for PBF-only sources. Do not proceed when DEM dimensions, CRS, or extents are implausible.

### 5. Build in Rhino 8

Read [rhino-builder-contract.md](references/rhino-builder-contract.md). Generate a project-local launcher:

```powershell
python scripts/make_rhino_launcher.py <project>\data\derived\site_manifest.json
```

Run the printed `build_site_in_rhino.py` with Rhino 8 `RunPythonScript`. Keep a Grasshopper Python component thin: expose paths, precision, `Run`, and `Bake`, then call the same `build_site` function rather than reimplementing geometry.

### 6. Verify delivery

Check all of the following:

- Rhino units are meters.
- Terrain and hidden DEM reference contain geometry.
- Terrain z range is nonzero and plausible.
- Contours use the recorded interval.
- Road, building, water, and land-use counts match source availability.
- OSM and DEM bounds overlap after the documented transform.
- Buildings without source height remain footprints.
- The local origin and source CRS are recorded.
- `rhino_build_report.json` is nonempty and references an existing saved `.3dm`.
- `latest_build_error.txt` is absent or empty.

## Failure Routing

- If the map is blank, accept local GeoJSON or explicit coordinates; do not change the site silently.
- If Overpass times out, reduce the boundary or use a PBF extract.
- If GEE rejects initialization, stop and request local authorization or the registered project ID, never the credential itself.
- If GDAL is not on `PATH`, let `prepare_site_data.py` discover a local QGIS/OSGeo4W installation before reporting it missing. If GDAL or osmium is still unavailable, use QGIS or install the missing tool before normalization.
- If terrain creation fails, retain the reference mesh, record the mesh fallback, and do not claim a NURBS surface.
- If roads are tiny or offset, fix document units or CRS/origin alignment and rebuild. Do not compensate with arbitrary scale factors.
- If fine mode looks falsely detailed, compare requested and native resolution and label interpolation.

## Deliverables

Return the confirmed boundary, selection settings, acquisition report and source sidecars, normalized manifest, Rhino launcher or Grasshopper trigger, saved `.3dm`, build diagnostic, units, CRS, local origin, terrain method, precision, object counts, attribution, and source limitations.
