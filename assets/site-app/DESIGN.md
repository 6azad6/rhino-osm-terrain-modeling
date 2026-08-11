# Rhino Site Studio Design

## Mode

Operate. Prioritize boundary selection, provider settings, visible state, and a short handoff to the local data pipeline.

## System

- Use a full-height map and a 370 px right control rail on desktop.
- Stack map above controls below 720 px.
- Use off-white and charcoal surfaces with one cobalt accent.
- Use 6 px corners, quiet hairlines, and soft depth only for transient overlays.
- Use Segoe UI/system sans for interface text and monospace only for coordinates.
- Keep the saved boundary, primary save action, and request-plan actions at the top of the rail.
- Keep the EN/中文 selector beside the theme control. Translate static labels, runtime states, map tooltips, and the extent canvas together, and remember the language locally.

## States

Provide explicit empty, ready, saving, saved, error, tile-offline, and disabled states. Keep local world boundaries and GeoJSON loading available when raster tiles fail.

## Integrity

Never display invented terrain. Before a DEM is acquired, preview only the selected extent and label it `EXTENT ONLY`. Keep credentials and data processing outside browser JavaScript.
