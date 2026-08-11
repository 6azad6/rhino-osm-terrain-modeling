# Data Provider Contract

Keep source acquisition separate from preprocessing and Rhino generation.

| Need | Default | Fallback |
|---|---|---|
| Roads, buildings, water, land use | Overpass for a small site | Geofabrik or local PBF plus `osmium` |
| Regional DEM | GEE Copernicus GLO-30 | SRTM, NASADEM, or local GeoTIFF/ASC |
| Survey detail | User-provided survey or LiDAR DEM | Do not substitute a resampled global DEM |

Known GEE bands are `COPERNICUS/DEM/GLO30: DEM`, `USGS/SRTMGL1_003: elevation`, and `NASA/NASADEM_HGT/001: elevation`. Require `--band` for another dataset.

## Authentication and network rules

- Public Overpass and Nominatim reads normally require no login. Respect rate limits and cache results.
- GEE normally requires the user's existing Earth Engine authorization and may require a Cloud project ID.
- Never request or store a password, refresh token, or service-account JSON.
- Run `scripts/acquire_site_data.py <selection> --out-dir <data>` first. It is dry-run by default.
- Add `--run` only after the boundary and providers are confirmed. Add `--authenticate` only when the user approves a local GEE auth flow.
- Reuse existing source files and sidecars instead of repeating network requests.

## Source integrity

- Keep WGS84 selection, raw OSM/PBF, raw DEM, and provider sidecars unchanged.
- Record endpoint, dataset, band, requested scale, time, output, and attribution.
- A requested scale below native DEM resolution is interpolation, not new accuracy.
- Do not obtain OSM through GEE. Join sources only after both are transformed into the same metric CRS.
- Record explicit conversion before combining GCJ-02 or BD-09 data with OSM WGS84.
