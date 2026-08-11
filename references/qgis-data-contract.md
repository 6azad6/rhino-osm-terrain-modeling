# QGIS and GDAL Data Contract

Prepare a normalized local package before Rhino. Use QGIS manually when the equivalent command-line tools are unavailable.

## Project output

```text
project/
  data/
    site_boundary.geojson
    site_selection.json
    acquisition_report.json
    source_osm.*
    source_dem.*
    derived/
      site.osm.pbf
      site_dem.tif
      site_dem.asc
      site_manifest.json
      osm/
        roads.geojson
        waterways.geojson
        buildings.geojson
        water.geojson
        landuse.geojson
        places.geojson
```

## Processing rules

1. Use `scripts/prepare_site_data.py`. Its default is an auditable plan; add `--run` after reviewing the CRS and output paths.
   On Windows it searches `PATH`, `QGIS_ROOT`, `OSGEO4W_ROOT`, and common QGIS/OSGeo4W folders on local drive roots. A custom-drive QGIS installation does not need a permanent PATH change.
2. Use a projected metric CRS. `--crs auto` chooses the local UTM zone for sites between 80S and 84N.
3. Clip OSM and DEM to the same WGS84 boundary.
4. Use `osmium` for source extraction and GDAL's OSM driver for multipolygon-aware vector conversion. Do not assemble OSM relations with ad hoc string or ring logic.
5. Use bilinear resampling for continuous elevation and export ESRI ASCII for the Rhino builder.
6. Preserve raw inputs. Write only derived files below `data/derived`.

## Acceptance checks

- `site_manifest.json` names the target CRS, raw sources, derived outputs, precision, detected tool paths, and planned commands.
- DEM and vector bounds overlap the boundary.
- GeoJSON coordinates are projected meters, not longitude/latitude.
- ESRI ASCII dimensions and value counts pass `validate_esri_ascii_dem.py`.
- OSM source structure passes `validate_osm_xml.py` when XML is used.
- Missing feature classes produce empty or absent layers and a diagnostic count of zero, not invented geometry.
