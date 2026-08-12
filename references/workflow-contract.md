# Workflow Contract

Use one project folder and move through these states in order:

```text
selection + model configuration -> acquisition -> preprocessing -> headless .3dm build -> validation
```

Before entering the project workflow, run `scripts/bootstrap_environment.py`. On first use, offer the user its single confirmed install action for missing open-source tools. Keep environment acknowledgement outside the project folder and never install Rhino or authorize GEE automatically.

Each state writes a durable artifact before the next starts:

| State | Required artifact |
|---|---|
| Selection/configuration | `site_boundary.geojson`, `site_selection.json` with `model_settings`, optional matching `osm_preview.json` |
| Acquisition | raw OSM/DEM plus `acquisition_report.json` |
| Preprocessing | normalized vectors, ASCII DEM, `site_manifest.json` |
| Headless build | `.3dm`, `rhino_build_report.json` |
| Validation | object counts, bounds, units, source limitations |

Never let browser preview data become the normalized modeling source or let a Grasshopper/Rhino script become a second acquisition implementation. The browser saves intent and an optional bounded preview cache, Python performs formal acquisition and preparation, and rhino3dm creates the default deliverable. RhinoCommon is an optional enhancement backend.

Stop at the current state when a required user choice, credential authorization, source file, or installed tool is missing. Report the exact missing input and preserve all completed artifacts.
