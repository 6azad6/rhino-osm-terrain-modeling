# Rhino OSM Terrain Modeling

A Kimi / Codex skill for building or repairing reusable, Heron-free Rhino 8 and Grasshopper site models from OpenStreetMap vectors and Google Earth Engine (or local) DEM data.

The pipeline covers browser-based site selection, data acquisition, preprocessing, and Rhino geometry generation — all managed through a reproducible set of Python scripts and documented contracts.

## Repository Contents

| Component | Description |
|-----------|-------------|
| `SKILL.md` | Skill manifest and operating rules for Codex |
| `scripts/` | Python automation scripts (bootstrap, data acquisition, preprocessing, Rhino launcher generation, validation) |
| `agents/` | Sub-agent definitions |
| `assets/` | Frontend and documentation assets |
| `references/` | Workflow, map-selection, data-provider, precision, QGIS, and Rhino builder contracts |

## Binary Assets

The following **6 PNG image files** are required by the built-in web map application (`assets/site-app/`) but **could not be uploaded via text-based MCP tools**. They are standard vendor assets from official Leaflet and Leaflet Draw releases:

| File Path | Source Package | Description |
|-----------|----------------|-------------|
| `assets/site-app/vendor/images/layers.png` | Leaflet 1.9.4 | Default layer control icon |
| `assets/site-app/vendor/images/layers-2x.png` | Leaflet 1.9.4 | Retina layer control icon |
| `assets/site-app/vendor/images/marker-icon.png` | Leaflet 1.9.4 | Default map marker icon |
| `assets/site-app/vendor/images/marker-shadow.png` | Leaflet 1.9.4 | Marker shadow image |
| `assets/site-app/vendor/images/spritesheet.png` | Leaflet Draw 1.0.4 | Toolbar spritesheet |
| `assets/site-app/vendor/images/spritesheet-2x.png` | Leaflet Draw 1.0.4 | Retina toolbar spritesheet |

### How to Obtain These Files

Choose **one** of the following methods and place the files in the paths listed above:

#### Option A — Download from Official GitHub Releases
1. **Leaflet 1.9.4** — Download from [https://github.com/Leaflet/Leaflet/releases/tag/v1.9.4](https://github.com/Leaflet/Leaflet/releases/tag/v1.9.4)
   - Extract `dist/images/layers.png`
   - Extract `dist/images/layers-2x.png`
   - Extract `dist/images/marker-icon.png`
   - Extract `dist/images/marker-shadow.png`
2. **Leaflet Draw 1.0.4** — Download from [https://github.com/Leaflet/Leaflet.draw/releases/tag/v1.0.4](https://github.com/Leaflet/Leaflet.draw/releases/tag/v1.0.4)
   - Extract `dist/images/spritesheet.png`
   - Extract `dist/images/spritesheet-2x.png`

#### Option B — Install via NPM
```bash
npm install leaflet@1.9.4
npm install leaflet-draw@1.0.4
```
Then copy the images from:
- `node_modules/leaflet/dist/images/`
- `node_modules/leaflet-draw/dist/images/`

#### Option C — CDN / Direct Links
You may also source the exact same files from any reputable CDN serving the official releases (e.g., unpkg, cdnjs, jsDelivr) using the version-pinned URLs for Leaflet `1.9.4` and Leaflet Draw `1.0.4`.

> **Note:** These assets are unchanged, unmodified vendor files. Do not rename them — the application expects the exact filenames shown above.

---

*For full usage instructions, see `SKILL.md` and the contract documents in `references/`.*
