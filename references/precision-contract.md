# Terrain Precision Contract

Precision controls processing density. It does not override source accuracy.

| Preset | DEM/sample target | Contours | Curve tolerance | Use |
|---|---:|---:|---:|---|
| `draft` | 30 m | 20 m | 1.00 m | fast massing and large extents |
| `standard` | 10 m | 10 m | 0.25 m | normal design context |
| `fine` | 3 m | 5 m | 0.05 m | small sites with fine source data |

Pass one preset through acquisition, GDAL resampling, mesh stride, contours, and Rhino diagnostics. Record native and requested resolution when known.

Warn when:

- requested spacing is smaller than the native DEM cell size;
- the sampled grid is too large for interactive Rhino work;
- vertical units or source CRS are missing;
- a fine model uses only a 30 m global DEM.

Keep the source DEM mesh as a hidden reference. A smooth NURBS surface is a presentation surface, not additional elevation evidence.
