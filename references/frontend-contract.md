# Frontend Contract

The bundled `assets/site-app` is an Operate-mode local GIS workbench.

## Interface

- Use two stages: site selection first, then OSM model preview/configuration after the boundary is saved.
- Keep the map full-height on desktop and first on mobile. In stage two, keep the model first and stack settings below it on mobile.
- Keep search, provider choices, GEE project, precision, boundary extent, and primary actions in one compact rail.
- Support rectangle and polygon drawing, GeoJSON loading, place search, an honest planar preview before DEM acquisition, loading, empty, offline, error, and saved states.
- Let the user explicitly request an OSM preview for Overpass selections. Cap preview requests at 100 km2, cache `osm_preview.json` beside the selection, and reuse it only when `bbox_wgs84` exactly matches.
- Preview building massing, roads, water, and land use. Provide default height, floor height, height multiplier, layer visibility, and color controls. Persist them under `site_selection.json.model_settings`.
- Height preview order is OSM `height`, then `building:levels * floor_height_m`, then `default_building_height_m`; apply `height_scale` last.
- The preview is planar until DEM acquisition. Never imply that the Canvas geometry is already terrain-draped.
- Use one cobalt accent, a 6 px radius system, restrained motion, keyboard focus, and light/dark tokens.
- Provide an EN/中文 selector beside the theme control. Apply the selected language to static copy, runtime states, Leaflet Draw labels, and preview-canvas text, and persist only the language preference locally.
- Do not turn the tool into a landing page, card grid, or multi-step wizard.

## Service boundary

`scripts/launch_site_app.py` serves only localhost static assets and these APIs:

- `GET /api/status`: saved selection and local source presence.
- `GET /api/geocode?q=`: cached Nominatim proxy.
- `POST /api/selection`: validate and save boundary/settings.
- `POST /api/plan`: write OSM or DEM dry-run request plans.
- `POST /api/osm-preview`: request and cache compact OSM preview features for a confirmed small boundary.

Do not place credentials, GEE auth flows, large downloads, GDAL processing, or Rhino generation in browser JavaScript. Leaflet, Leaflet Draw, TopoJSON Client, and a world-atlas 110 m boundary are vendored for offline use. OSM raster tiles remain optional network context; when they fail, keep the local world boundaries and GeoJSON drawing workflow available.
