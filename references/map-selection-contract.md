# Map Selection Contract

Use the localhost site app as the normal Codex selection surface. It is a boundary and settings editor, not a Rhino geometry engine.

## Start and hand off

1. Run `python scripts/launch_site_app.py --output-dir <project>/data --port 0`.
2. Open the printed `SITE_APP_URL` in the Codex in-app Browser when available.
3. Search or pan to a place, draw one rectangle or polygon, choose providers and precision, then save.
4. Confirm these files exist before any acquisition:

```text
data/site_boundary.geojson
data/site_selection.json
```

`site_boundary.geojson` is WGS84 longitude/latitude. `site_selection.json` records the bounds, providers, optional GEE project ID, and precision. It never stores passwords, OAuth tokens, or service-account JSON.

## Rules

- Treat the basemap as orientation only, never as elevation data.
- Keep one active boundary. Do not merge accidental drawings.
- Do not silently change the boundary after a tile, search, or network failure.
- Use a small boundary for Overpass. Use local or Geofabrik PBF for larger or repeated sites.
- Use the Preview tab only for extent orientation. It is not the downloaded DEM.
- If browser control is unavailable, accept a user-provided GeoJSON, explicit coordinates, or local data paths.

The app exposes `/api/status`, `/api/selection`, `/api/geocode`, and `/api/plan`. The plan endpoint is dry-run only; execute acquisition from Codex with `scripts/acquire_site_data.py --run` after confirmation.
