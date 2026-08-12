# Rhino Site Studio Design

## Mode

Operate. Prioritize boundary selection, a trustworthy OSM massing preview, explicit model settings, and a short handoff to the local data pipeline.

## System

- Use two focused views: full-height site selection, then model preview/configuration after a boundary is saved.
- Use a 370 px selection rail and a 340 px model-settings rail on desktop. Stack the model before its settings below 720 px.
- Use off-white and charcoal surfaces with one cobalt accent.
- Use 6 px corners, quiet hairlines, and soft depth only for transient overlays.
- Use Segoe UI/system sans for interface text and monospace only for coordinates.
- Keep the saved boundary, primary save/configure action, and request-plan actions at the top of the selection rail.
- Let the model dominate stage two. Put height rules, visibility, native color swatches, statistics, and the settings save action in its rail.
- Keep the EN/中文 selector beside the theme control. Translate static labels, runtime states, map tooltips, and the extent canvas together, and remember the language locally.

## States

Provide explicit empty, ready, saving, saved, loading-preview, preview-ready, error, tile-offline, and disabled states. Lock the model view until a boundary exists. Keep local world boundaries and GeoJSON loading available when raster tiles fail.

## Integrity

Never display invented terrain. Before DEM acquisition, show the selected extent as a planar base and label the OSM view as planar; state that final geometry is projected onto the DEM. Preview real OSM features only after an explicit request. Keep credentials, bulk acquisition, GIS processing, and `.3dm` generation outside browser JavaScript.
