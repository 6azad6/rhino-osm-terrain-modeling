# Rhino OSM Terrain Modeling

> 一套从 OpenStreetMap 矢量数据 + DEM 高程数据自动生成 Rhino `.3dm` 场地模型的完整工作流。
>
> 零依赖 Heron，支持浏览器选点、无头（headless）生成、可重复执行。

---

## 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [系统要求](#系统要求)
- [安装与环境初始化](#安装与环境初始化)
- [完整工作流程](#完整工作流程)
  - [Step 0 — 环境检查](#step-0--环境检查)
  - [Step 1 — 地图选点](#step-1--地图选点)
  - [Step 2 — 数据采集](#step-2--数据采集)
  - [Step 3 — 数据预处理](#step-3--数据预处理)
  - [Step 4 — 生成 .3dm](#step-4--生成-3dm)
  - [Step 5 — 验证交付](#step-5--验证交付)
- [项目结构](#项目结构)
- [脚本说明](#脚本说明)
- [精度预设](#精度预设)
- [故障排除](#故障排除)
- [技术架构](#技术架构)

---

## 项目简介

**Rhino OSM Terrain Modeling** 是一个面向建筑师、景观设计师和城市分析人员的自动化工具链。它通过以下 pipeline 将真实世界的地理数据转化为可直接在 Rhino 中编辑的 3D 场地模型：

```
浏览器地图选点 → Python 数据采集 → GDAL/osmium 预处理 → rhino3dm 无头生成 → 验证交付
```

整个流程不依赖 Rhino 8 运行时（可选增强），也无需 Grasshopper 插件。所有操作均可通过 Python 脚本在普通环境中完成。

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **浏览器地图选点** | 内置 Leaflet 交互式地图，支持矩形/多边形绘制、GeoJSON 导入、地理编码搜索 |
| **多数据源支持** | OpenStreetMap（Overpass / Geofabrik PBF）、Google Earth Engine DEM、本地数据 |
| **无头生成** | 默认通过 `rhino3dm` Python 库直接输出 `.3dm`，无需打开 Rhino |
| **可选 Rhino 增强** | 保留 `rhino_site_builder.py` 作为 RhinoCommon 增强后端，支持 NURBS 曲面 |
| **自动 UTM 投影** | 根据选点范围自动计算当地 UTM 坐标系，确保米制精度 |
| **建筑高度解析** | 按 `height` → `building:levels` → 默认高度的优先级自动推断 |
| **地形贴合表面** | 道路、水体、用地边界均按 DEM 网格采样后三角化，贴合地形 |
| **可配置材质与可见性** | 前端配置颜色、透明度、图层显隐，直接写入 `.3dm` 材质系统 |
| **完整诊断报告** | 每次生成输出 `rhino_build_report.json`，记录对象数、范围、CRS、局限性 |

---

## 系统要求

### 必需

| 组件 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 脚本运行环境 |
| `rhino3dm` | 最新 | 无头 `.3dm` 生成 |
| `shapely` | 最新 | 多边形合并、三角化、道路缓冲 |
| GDAL (gdalwarp / gdal_translate / ogr2ogr) | 3.x | DEM 裁剪重投影、OSM 矢量提取 |

### 可选（根据数据来源选择）

| 组件 | 用途 |
|------|------|
| QGIS / OSGeo4W | Windows 上 GDAL 的便捷安装方式 |
| `osmium-tool` | 大体积 PBF 快速裁剪 |
| `earthengine-api` | Google Earth Engine DEM 下载 |
| Rhino 8 | 仅当你需要 NURBS 增强或视觉检查时 |

### 前端（地图选点界面）

前端为纯静态 HTML/JS，无需构建工具：
- Leaflet 1.9.4 + Leaflet Draw 1.0.4（地图绘制）
- topojson-client（世界地图轮廓）
- 现代浏览器即可运行

---

## 安装与环境初始化

### 1. 克隆仓库

```bash
git clone https://github.com/6azad6/rhino-osm-terrain-modeling.git
cd rhino-osm-terrain-modeling
```

### 2. 运行环境检查

```bash
python scripts/bootstrap_environment.py
```

脚本会自动检测以下组件：
- GDAL 工具链（gdalwarp / gdal_translate / ogr2ogr）
- osmium-tool
- Earth Engine API
- rhino3dm
- Shapely
- Rhino 8

如果缺少可自动安装的开源组件，脚本会提示你一键安装：

```bash
python scripts/bootstrap_environment.py --install
```

> **注意**：脚本不会自动安装 Rhino 8 或初始化 Earth Engine 认证，这两项需要手动完成。

---

## 完整工作流程

### Step 0 — 环境检查

```bash
python scripts/bootstrap_environment.py
```

确保 GDAL 和 rhino3dm 可用。如需安装缺失组件：

```bash
python scripts/bootstrap_environment.py --install
```

---

### Step 1 — 地图选点

启动本地地图服务器：

```bash
python scripts/launch_site_app.py --output-dir ./my-project/data --port 0
```

终端会输出一个本地 URL（如 `http://127.0.0.1:56789`）。在浏览器中打开：

**界面功能**：
- 🗺️ **地图操作**：平移、缩放、切换底图（OpenStreetMap / Satellite）
- 📐 **绘制边界**：矩形工具（推荐）或多边形工具
- 📁 **导入 GeoJSON**：支持直接上传已有的边界文件
- 🔍 **地理编码搜索**：输入地址快速定位
- ⚙️ **精度选择**：Draft / Standard / Fine 三档
- 🎨 **模型配置**（点击 Save and configure model 后）：
  - 建筑默认高度、层高、高度缩放系数
  - 图层颜色自定义
  - 图层可见性开关
  - 水体透明度
- 👁️ **OSM 预览**：加载 bounded Overpass 预览，检查建筑密度和道路网络

点击 **Save and configure model** → 配置完成后点击 **Save**，生成：
- `site_boundary.geojson` — WGS84 边界
- `site_selection.json` — 选点配置 + 模型设置

---

### Step 2 — 数据采集

```bash
python scripts/acquire_site_data.py ./my-project/data/site_selection.json --out-dir ./my-project/data
```

**默认 Dry Run**：先查看执行计划，确认边界和数据源。确认后加 `--run` 实际下载：

```bash
python scripts/acquire_site_data.py ./my-project/data/site_selection.json --out-dir ./my-project/data --run
```

**支持的数据来源**：

| 来源 | 适用场景 | 命令 |
|------|----------|------|
| Overpass API | 小范围（< 1km²）快速获取 | 默认 |
| Geofabrik PBF | 大范围或重复构建 | `--osm-local <pbf-path>` |
| Google Earth Engine | 全球 DEM（SRTM / ALOS 等） | `--authenticate` |
| 本地文件 | 已有 OSM / DEM 数据 | `--osm-local` / `--dem-local` |

输出：
- `acquisition_report.json` — 采集报告
- 原始 OSM / DEM 数据文件

---

### Step 3 — 数据预处理

```bash
python scripts/prepare_site_data.py \
  ./my-project/data/site_boundary.geojson \
  --osm ./my-project/data/site.osm.pbf \
  --dem ./my-project/data/site_dem.tif \
  --out-dir ./my-project/data/derived \
  --crs auto \
  --precision standard
```

**参数说明**：

| 参数 | 说明 |
|------|------|
| `--crs auto` | 自动根据边界中心计算本地 UTM EPSG 代码 |
| `--crs EPSG:32650` | 手动指定投影坐标系 |
| `--precision draft` | 粗模：30m 分辨率，快速预览 |
| `--precision standard` | 标准：10m 分辨率，常规工作 |
| `--precision fine` | 精细：3m 分辨率，注意不会超过 DEM 原始精度 |
| `--run` | 实际执行预处理命令（默认仅生成计划） |

**预处理内容**：
1. 用 osmium / ogr2ogr 裁剪 OSM 数据，按类别提取 GeoJSON：
   - `roads.geojson` — 道路中心线
   - `buildings.geojson` — 建筑轮廓
   - `water.geojson` — 水体
   - `landuse.geojson` — 用地
   - `places.geojson` — 地名点位
   - `waterways.geojson` — 水系线
2. 用 gdalwarp 裁剪并重投影 DEM 到目标 CRS
3. 用 gdal_translate 转换为 ESRI ASCII Grid（`.asc`）
4. 生成 `site_manifest.json` — 完整的项目元数据清单

---

### Step 4 — 生成 .3dm

**默认方式 — 无头生成（推荐）**：

```bash
python scripts/rhino3dm_site_builder.py ./my-project/data/derived/site_manifest.json
```

无需打开 Rhino，直接输出：
- `site_model.3dm` — 完整场地模型
- `rhino_build_report.json` — 构建诊断报告

**可选方式 — Rhino 8 增强**：

```bash
python scripts/make_rhino_launcher.py ./my-project/data/derived/site_manifest.json
```

生成 `build_site_in_rhino.py`，然后在 Rhino 8 中运行：

```python
# 在 Rhino 8 Python 编辑器中
exec(open("build_site_in_rhino.py").read())
```

这种方式支持 NURBS 曲面地形和更精细的几何控制。

---

### Step 5 — 验证交付

检查 `rhino_build_report.json` 确认以下项目：

| 检查项 | 预期结果 |
|--------|----------|
| `units` | `"Meters"` |
| `terrain_z_range_m` | 非零且合理 |
| `object_counts.terrain` | ≥ 1 |
| `object_counts.building_masses` | 与 OSM 数据匹配 |
| `output_bytes` | > 0 |
| `ok` | `true` |

在 Rhino 中打开 `.3dm` 后验证：
- 单位是否为米
- 图层颜色和材质是否正确
- 建筑高度是否合理（检查 `height_sources` 分布）
- 地形是否有起伏
- 道路/水体是否贴合地形

---

## 项目结构

```
rhino-osm-terrain-modeling/
├── SKILL.md                          # Codex Skill 定义
├── README.md                         # 本文件
├── agents/
│   └── openai.yaml                   # Sub-agent 定义
├── assets/
│   └── site-app/                     # 浏览器地图选点前端
│       ├── index.html                # 主页面
│       ├── styles.css                # 样式
│       ├── app.js                    # 交互逻辑
│       ├── DESIGN.md                 # 前端设计文档
│       └── vendor/                   # 第三方库
│           ├── leaflet.js / .css     # Leaflet 1.9.4
│           ├── leaflet.draw.js / .css # Leaflet Draw 1.0.4
│           ├── topojson-client.min.js # TopoJSON 解析
│           ├── countries-110m.json   # 世界地图数据
│           └── images/               # 地图图标（PNG 精灵图）
├── references/                       # 各模块合约文档
│   ├── workflow-contract.md          # 工作流边界
│   ├── map-selection-contract.md     # 地图选点规范
│   ├── data-provider-contract.md     # 数据提供规范
│   ├── precision-contract.md         # 精度定义
│   ├── qgis-data-contract.md         # QGIS/GDAL 处理规范
│   ├── frontend-contract.md          # 前端接口规范
│   └── rhino-builder-contract.md     # Rhino 构建规范
└── scripts/                          # 自动化脚本
    ├── bootstrap_environment.py      # 环境检查与安装
    ├── launch_site_app.py            # 启动地图选点服务器
    ├── acquire_site_data.py          # 数据获取编排
    ├── fetch_osm.py                  # OSM 数据下载
    ├── fetch_gee_dem.py              # GEE DEM 下载
    ├── prepare_site_data.py          # 数据预处理（GDAL/osmium）
    ├── validate_esri_ascii_dem.py    # DEM 验证
    ├── validate_osm_xml.py           # OSM 验证
    ├── rhino3dm_site_builder.py      # 无头 .3dm 生成（默认）
    ├── rhino_site_builder.py         # RhinoCommon 生成（可选）
    ├── make_rhino_launcher.py        # Rhino 启动器生成
    └── create_site_selector.py       # 选点工具（备用）
```

---

## 脚本说明

### 环境类

| 脚本 | 功能 |
|------|------|
| `bootstrap_environment.py` | 检测 GDAL、osmium、rhino3dm、Shapely 等依赖；支持一键安装缺失组件 |

### 选点类

| 脚本 | 功能 |
|------|------|
| `launch_site_app.py` | 启动本地 HTTP 服务器，提供浏览器地图界面；支持中英文切换、暗色模式 |

### 采集类

| 脚本 | 功能 |
|------|------|
| `acquire_site_data.py` | 根据 `site_selection.json` 编排 OSM 和 DEM 的获取计划，支持 dry-run |
| `fetch_osm.py` | 从 Overpass API 或本地 PBF 获取 OSM 数据 |
| `fetch_gee_dem.py` | 从 Google Earth Engine 导出 DEM |

### 预处理类

| 脚本 | 功能 |
|------|------|
| `prepare_site_data.py` | GDAL/osmium 预处理核心：裁剪、重投影、分类提取、生成 manifest |
| `validate_esri_ascii_dem.py` | 验证 `.asc` 文件格式和坐标范围 |
| `validate_osm_xml.py` | 验证 OSM XML 结构 |

### 构建类

| 脚本 | 功能 |
|------|------|
| `rhino3dm_site_builder.py` | **默认构建器**。纯 Python 生成带材质、图层、颜色的 `.3dm` |
| `rhino_site_builder.py` | 可选构建器。需在 Rhino 8 内运行，支持 NURBS 曲面 |
| `make_rhino_launcher.py` | 生成 Rhino 8 可直接执行的 Python 脚本 |

---

## 精度预设

| 预设 | DEM 分辨率 | 采样步距 | 等高距 | 用途 |
|------|-----------|---------|--------|------|
| **draft** | 30m | 30m | 20m | 快速预览、大范围区域 |
| **standard** | 10m | 10m | 10m | 常规设计工作 |
| **fine** | 3m | 3m | 5m | 精细建模（注意不超过 DEM 原始分辨率） |

> ⚠️ `fine` 模式只是增加了处理密度，不会创造超出原始 DEM 精度的地形细节。

---

## 故障排除

### 地图界面空白
- 检查 `assets/site-app/vendor/images/` 下是否有 6 个 PNG 图标文件
- 检查浏览器控制台是否有网络错误

### GDAL 找不到
- Windows：安装 QGIS LTR（通过 winget 或官网），脚本会自动发现 OSGeo4W 路径
- 或手动设置环境变量 `QGIS_ROOT` / `OSGEO4W_ROOT`

### Overpass 超时
- 缩小选点范围
- 或使用 Geofabrik PBF 本地数据源：`--osm-local <path>`

### rhino3dm 安装失败
- 运行 `bootstrap_environment.py --install`，脚本会自动下载匹配平台的官方 wheel
- 或手动：`pip install rhino3dm`

### Earth Engine 认证失败
- 运行 `earthengine authenticate` 手动完成 OAuth 流程
- 或使用本地 DEM：`--dem-local <path>`

### 生成后的道路太细/偏移
- 检查 `.3dm` 单位是否为米
- 检查 CRS 是否正确对齐
- 不要通过任意缩放系数补偿

---

## 技术架构

### 数据流

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Browser Map UI │────→│  site_boundary   │────→│  acquire_site   │
│  (Leaflet)      │     │  .geojson        │     │  _data.py       │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                              ┌───────────────────────────┼───────────┐
                              ▼                           ▼           ▼
                       ┌─────────────┐              ┌──────────┐  ┌──────────┐
                       │  OSM data   │              │  DEM     │  │  GEE     │
                       │  (.osm.pbf) │              │  (local) │  │  (API)   │
                       └──────┬──────┘              └────┬─────┘  └────┬─────┘
                              │                          │             │
                              └────────────┬─────────────┘             │
                                           ▼                           │
                                    ┌──────────────┐                   │
                                    │ prepare_site │◄──────────────────┘
                                    │ _data.py     │  (GDAL/osmium)
                                    │              │
                                    │  • clip      │
                                    │  • reproject │
                                    │  • classify  │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │ site_manifest│
                                    │ .json        │
                                    └──────┬───────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
            ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
            │ rhino3dm_    │      │ rhino_site_  │      │ make_rhino_  │
            │ site_builder │      │ builder.py   │      │ launcher.py  │
            │ (default)    │      │ (optional)   │      │ (optional)   │
            └──────┬───────┘      └──────────────┘      └──────────────┘
                   │
                   ▼
            ┌──────────────┐
            │ site_model   │
            │ .3dm         │
            └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐
            │ rhino_build  │
            │ _report.json │
            └──────────────┘
```

### 几何生成策略

| 要素 | 生成方式 |
|------|----------|
| **地形** | DEM 网格 → Mesh，坐标以 DEM 中心为原点重定位 |
| **等高线** | Marching Squares 算法，按配置间隔提取 |
| **道路中心线** | OSM 线串 → DEM 采样高程 → Polyline Curve |
| **道路表面** | 中心线缓冲 → 并集 → DEM 网格分割 → 三角化 Mesh |
| **建筑 footprint** | OSM 多边形 → DEM 采样高程 → Polyline Curve |
| **建筑体量** | footprint 点采样墙脚 + 平屋顶 → 封闭 Mesh |
| **水体/用地** | OSM 多边形 → 并集 → DEM 网格分割 → 三角化 Mesh |

### 材质与图层

生成的 `.3dm` 包含完整的图层层级和材质分配：

```
Site
├── Site::Terrain                 # 地形 Mesh（可见）
├── Site::Terrain::DEM Reference  # DEM 参考 Mesh（隐藏）
├── Site::Contours                # 等高线
├── Site::OSM
│   ├── Site::OSM::Road Centerlines   # 道路中心线
│   ├── Site::OSM::Road Surfaces      # 道路表面 Mesh
│   ├── Site::OSM::Building Footprints # 建筑底面
│   ├── Site::OSM::Building Masses    # 建筑体量 Mesh
│   ├── Site::OSM::Water              # 水体 Mesh（半透明）
│   ├── Site::OSM::Land Use           # 用地 Mesh
│   └── Site::OSM::Places             # 地名点位
```

每种材质的颜色、可见性、透明度均可通过前端界面配置，并持久化到 `site_selection.json` 中。

---

## License

本项目采用 MIT 许可证。第三方库（Leaflet、Leaflet Draw、TopoJSON）遵循其各自的许可证，详见 `assets/site-app/vendor/` 下的 `.LICENSE` 文件。

---

> 更多详细规范请参阅 `references/` 目录下的合约文档。
