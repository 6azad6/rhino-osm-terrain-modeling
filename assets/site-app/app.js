(() => {
  "use strict";

  const messages = {
    en: {
      documentTitle: "Rhino Site Studio",
      languageLabel: "Language",
      languageEnglish: "English",
      languageChinese: "Chinese",
      brandSubtitle: "OSM + GEE terrain workbench",
      darkMode: "Dark mode",
      lightMode: "Light mode",
      localService: "Local service",
      selectionSaved: "Selection saved",
      offlineMode: "Offline mode",
      mapWorkspace: "Site map workspace",
      mapActions: "Map actions",
      siteControls: "Site controls",
      workspaceView: "Workspace view",
      mapUnavailable: "Map tiles are unavailable",
      mapUnavailableHelp: "Draw or load a GeoJSON boundary from the controls.",
      invalidBoundaryType: "Use a Polygon or MultiPolygon GeoJSON file.",
      noPolygon: "The GeoJSON contains no Polygon or MultiPolygon.",
      noBoundaryCoords: "The GeoJSON boundary has no coordinates.",
      drawPolygon: "Draw a polygon",
      drawRectangle: "Draw a rectangle",
      editLayers: "Edit layers",
      deleteLayers: "Delete layers",
      zoomIn: "Zoom in",
      zoomOut: "Zoom out",
      drawStartPolygon: "Click to start drawing a polygon.",
      drawStartRectangle: "Click and drag to draw a rectangle.",
      drawContinue: "Click to continue drawing the shape.",
      drawFinish: "Click the first point to close this shape.",
      drawCancel: "Cancel drawing",
      editSave: "Save changes",
      editCancel: "Cancel editing",
      editClearAll: "Clear all layers",
      editEdit: "Edit layers",
      editRemove: "Delete layers",
      editDisabled: "No layers to edit",
      removeDisabled: "No layers to delete",
      editTooltip: "Drag handles to edit the boundary.",
      removeTooltip: "Click a boundary to delete it.",
      findView: "Find my view",
      loadGeoJson: "Load GeoJSON",
      tileState: "OSM tiles unavailable. Offline boundaries active.",
      attribution: "OpenStreetMap contributors / Natural Earth",
      selectSite: "Select a working site",
      selectSiteHelp: "Choose a boundary first. Network requests stay local to this service.",
      boundary: "Boundary",
      notSelected: "Not selected",
      readyToSave: "Ready to save",
      west: "West",
      south: "South",
      east: "East",
      north: "North",
      drawBoundaryHelp: "Draw a rectangle or polygon on the map.",
      featureSingle: "{count} feature; approx {width} x {height} km.",
      featurePlural: "{count} features; approx {width} x {height} km.",
      saveBoundary: "Save boundary",
      saveAndConfigure: "Save and configure model",
      planOsm: "Plan OSM",
      planDem: "Plan DEM",
      findPlace: "Find a place",
      placePlaceholder: "City, address, or landmark",
      search: "Search",
      osmSource: "OSM source",
      osmOverpass: "Overpass, small areas",
      osmLocal: "Local OSM or PBF",
      osmGeofabrik: "Geofabrik PBF extract",
      osmHelp: "Overpass needs no login. Large sites should use a local PBF.",
      terrainSource: "Terrain source",
      demCopernicus: "Copernicus GLO-30",
      demSrtm: "USGS SRTM 30 m",
      demNasadem: "NASADEM 30 m",
      demLocal: "Local GeoTIFF or ASCII grid",
      geeHelp: "GEE uses your local Earth Engine session and project.",
      geeProject: "GEE project ID",
      optional: "optional",
      terrainPrecision: "Terrain precision",
      draft: "Draft",
      standard: "Standard",
      fine: "Fine",
      draftNote: "30 m sampling target. Fast preview for large extents.",
      standardNote: "10 m sampling target. Source resolution remains the accuracy limit.",
      fineNote: "3 m sampling target. Interpolation is labelled when source data is coarser.",
      contours: "Contours: {value}.",
      credentialsTitle: "Credentials stay outside the skill",
      credentialsHelp: "OSM is public. GEE may ask you to authorize locally and provide a project ID. Tokens are never saved here.",
      map: "Map",
      extent: "Extent",
      model: "Model",
      readyForBoundary: "Ready for a boundary.",
      boundaryReady: "Boundary ready. Review settings, then save.",
      savingBoundary: "Saving boundary and settings...",
      boundarySaved: "Boundary and settings saved.",
      selectionToast: "Site selection saved to the local data folder.",
      preparingRequest: "Preparing {kind} request...",
      planReady: "{kind} plan ready.",
      planToast: "{kind} plan written to the data folder.",
      searching: "Searching...",
      noPlace: "No place found.",
      placeFound: "Place found.",
      workingExtent: "Working extent",
      extentHelp: "This plane shows only the selected bounds. Terrain appears after DEM acquisition and the Rhino build.",
      backToMap: "Back to map",
      extentPreview: "Selected site extent preview",
      previewEmpty: "Draw a boundary to see the working extent.",
      extentOnly: "EXTENT ONLY",
      demNotLoaded: "DEM not loaded",
      offlineWorld: "Offline world boundaries could not be loaded.",
      tilesUnavailableActivity: "OSM tiles are unavailable. Offline boundaries and local GeoJSON still work.",
      boundaryCleared: "Boundary cleared.",
      geojsonLoaded: "GeoJSON boundary loaded.",
      locationUnavailable: "Location is not available in this browser.",
      locationDenied: "Location permission was not granted.",
      offlineActivity: "Local service is unavailable. You can still draw and export a GeoJSON file.",
      requestFailed: "Request failed: {message}"
      ,
      modelPreview: "OSM model preview",
      modelPreviewHelp: "Inspect massing and layer styling before data preparation.",
      modelPreviewCanvas: "Interactive OSM model preview",
      modelControls: "Model preview controls",
      loadOsmPreview: "Load OSM preview",
      resetView: "Reset view",
      extentMode: "Extent mode",
      osmPreviewReady: "OSM preview ready",
      previewEmptyTitle: "Select and save a site first",
      previewEmptyHelp: "The model preview becomes available after the boundary is saved.",
      loadingPreview: "Loading OSM preview...",
      previewControls: "Drag to rotate · Wheel to zoom",
      planarPreview: "Planar OSM preview; final geometry is projected to the DEM.",
      buildingRules: "Building height rules",
      buildingRulesHelp: "OSM height wins, then levels × floor height, then the default.",
      defaultHeight: "Default height",
      floorHeight: "Floor height",
      heightScale: "Height scale",
      modelLayers: "Model layers and colors",
      modelLayersHelp: "The same visibility and material colors are written into the Rhino file.",
      layerTerrain: "Terrain",
      layerContours: "Contours",
      layerRoads: "Roads",
      layerBuildings: "Buildings",
      layerWater: "Water",
      layerLanduse: "Land use",
      previewStats: "Preview statistics",
      previewTruncated: "Limited",
      osmHeights: "OSM heights",
      defaultHeights: "Default heights",
      saveModelSettings: "Save model settings",
      settingsFollowSelection: "Settings are stored with the site selection.",
      modelSettingsSaved: "Model settings saved.",
      previewRequiresOverpass: "OSM preview is available for Overpass selections. Use the formal pipeline for local PBF data.",
      previewFailed: "Preview failed: {message}",
      previewSummary: "Preview contains {buildings} buildings, {roads} roads, {water} water areas, and {landuse} land-use areas. Use arrow keys to rotate and plus or minus to zoom.",
      layerColor: "{layer} color"
    },
    zh: {
      documentTitle: "Rhino 场地工作台",
      languageLabel: "语言",
      languageEnglish: "英文",
      languageChinese: "中文",
      brandSubtitle: "OSM + GEE 地形工作台",
      darkMode: "深色模式",
      lightMode: "浅色模式",
      localService: "本地服务",
      selectionSaved: "选址已保存",
      offlineMode: "离线模式",
      mapWorkspace: "场地地图工作区",
      mapActions: "地图操作",
      siteControls: "场地控制",
      workspaceView: "工作区视图",
      mapUnavailable: "地图瓦片不可用",
      mapUnavailableHelp: "请从控制栏绘制或载入 GeoJSON 边界。",
      invalidBoundaryType: "请选择 Polygon 或 MultiPolygon 类型的 GeoJSON 文件。",
      noPolygon: "GeoJSON 中没有 Polygon 或 MultiPolygon。",
      noBoundaryCoords: "GeoJSON 边界没有坐标。",
      drawPolygon: "绘制多边形",
      drawRectangle: "绘制矩形",
      editLayers: "编辑图层",
      deleteLayers: "删除图层",
      zoomIn: "放大",
      zoomOut: "缩小",
      drawStartPolygon: "点击开始绘制多边形。",
      drawStartRectangle: "点击并拖动绘制矩形。",
      drawContinue: "点击继续绘制形状。",
      drawFinish: "点击起点闭合形状。",
      drawCancel: "取消绘制",
      editSave: "保存修改",
      editCancel: "取消编辑",
      editClearAll: "清除全部图层",
      editEdit: "编辑图层",
      editRemove: "删除图层",
      editDisabled: "没有可编辑的图层",
      removeDisabled: "没有可删除的图层",
      editTooltip: "拖动控制点编辑边界。",
      removeTooltip: "点击边界将其删除。",
      findView: "定位我的视图",
      loadGeoJson: "载入 GeoJSON",
      tileState: "OSM 瓦片不可用，离线边界仍可使用。",
      attribution: "OpenStreetMap 贡献者 / Natural Earth",
      selectSite: "选择工作场地",
      selectSiteHelp: "请先选择边界。网络请求只会发送到本地服务。",
      boundary: "边界",
      notSelected: "未选择",
      readyToSave: "可以保存",
      west: "西",
      south: "南",
      east: "东",
      north: "北",
      drawBoundaryHelp: "请在地图上绘制矩形或多边形。",
      featureSingle: "{count} 个要素，约 {width} x {height} km。",
      featurePlural: "{count} 个要素，约 {width} x {height} km。",
      saveBoundary: "保存边界",
      saveAndConfigure: "保存并配置模型",
      planOsm: "规划 OSM",
      planDem: "规划 DEM",
      findPlace: "查找地点",
      placePlaceholder: "城市、地址或地标",
      search: "搜索",
      osmSource: "OSM 来源",
      osmOverpass: "Overpass，小范围",
      osmLocal: "本地 OSM 或 PBF",
      osmGeofabrik: "Geofabrik PBF 提取",
      osmHelp: "Overpass 无需登录。大范围场地建议使用本地 PBF。",
      terrainSource: "地形来源",
      demCopernicus: "Copernicus GLO-30",
      demSrtm: "USGS SRTM 30 m",
      demNasadem: "NASADEM 30 m",
      demLocal: "本地 GeoTIFF 或 ASCII 网格",
      geeHelp: "GEE 使用本机 Earth Engine 会话和项目。",
      geeProject: "GEE 项目 ID",
      optional: "可选",
      terrainPrecision: "地形精度",
      draft: "草稿",
      standard: "标准",
      fine: "精细",
      draftNote: "目标采样 30 m，适合大范围快速预览。",
      standardNote: "目标采样 10 m，实际精度受源数据分辨率限制。",
      fineNote: "目标采样 3 m，源数据较粗时会明确标注插值。",
      contours: "等高线：{value}。",
      credentialsTitle: "凭据不进入 skill",
      credentialsHelp: "OSM 是公开数据。GEE 可能要求在本机授权并提供项目 ID。这里不会保存 token。",
      map: "地图",
      extent: "范围",
      model: "模型",
      readyForBoundary: "等待选择边界。",
      boundaryReady: "边界已就绪。请检查设置后保存。",
      savingBoundary: "正在保存边界和设置...",
      boundarySaved: "边界和设置已保存。",
      selectionToast: "选址已保存到本地数据目录。",
      preparingRequest: "正在准备 {kind} 请求...",
      planReady: "{kind} 计划已就绪。",
      planToast: "{kind} 计划已写入数据目录。",
      searching: "正在搜索...",
      noPlace: "没有找到地点。",
      placeFound: "已找到地点。",
      workingExtent: "工作范围",
      extentHelp: "此平面只显示选定范围。获取 DEM 并完成 Rhino 构建后才会出现地形。",
      backToMap: "返回地图",
      extentPreview: "选定场地范围预览",
      previewEmpty: "绘制边界后查看工作范围。",
      extentOnly: "仅显示范围",
      demNotLoaded: "DEM 尚未载入",
      offlineWorld: "离线世界边界载入失败。",
      tilesUnavailableActivity: "OSM 瓦片不可用，但离线边界和本地 GeoJSON 仍可使用。",
      boundaryCleared: "边界已清除。",
      geojsonLoaded: "GeoJSON 边界已载入。",
      locationUnavailable: "当前浏览器不支持定位。",
      locationDenied: "定位权限未获允许。",
      offlineActivity: "本地服务不可用。仍可绘制并导出 GeoJSON 文件。",
      requestFailed: "请求失败：{message}"
      ,
      modelPreview: "OSM 模型预览",
      modelPreviewHelp: "在数据预处理前检查体量、图层和材质配置。",
      modelPreviewCanvas: "可交互 OSM 模型预览",
      modelControls: "模型预览控制",
      loadOsmPreview: "加载 OSM 预览",
      resetView: "重置视图",
      extentMode: "范围模式",
      osmPreviewReady: "OSM 预览已就绪",
      previewEmptyTitle: "请先选择并保存场地",
      previewEmptyHelp: "保存边界后即可进行模型预览与配置。",
      loadingPreview: "正在加载 OSM 预览...",
      previewControls: "拖动旋转 · 滚轮缩放",
      planarPreview: "此处为平面 OSM 预览；最终几何会投影贴合 DEM。",
      buildingRules: "建筑高度规则",
      buildingRulesHelp: "优先使用 OSM height，其次为层数 × 层高，最后使用默认高度。",
      defaultHeight: "默认高度",
      floorHeight: "单层高度",
      heightScale: "高度倍率",
      modelLayers: "模型图层与颜色",
      modelLayersHelp: "相同的可见性与材质颜色会写入 Rhino 文件。",
      layerTerrain: "地形",
      layerContours: "等高线",
      layerRoads: "道路",
      layerBuildings: "建筑",
      layerWater: "水体",
      layerLanduse: "土地利用",
      previewStats: "预览统计",
      previewTruncated: "已限量",
      osmHeights: "OSM 高度",
      defaultHeights: "默认高度",
      saveModelSettings: "保存模型设置",
      settingsFollowSelection: "设置会与场地选择一起保存。",
      modelSettingsSaved: "模型设置已保存。",
      previewRequiresOverpass: "OSM 预览适用于 Overpass 选区。本地 PBF 请使用正式数据流程。",
      previewFailed: "预览失败：{message}",
      previewSummary: "预览包含 {buildings} 栋建筑、{roads} 条道路、{water} 处水体和 {landuse} 处土地利用。可用方向键旋转，加号或减号缩放。",
      layerColor: "{layer}颜色"
    }
  };
  const precisionInfo = {
    draft: { sample: "30 m", contour: "20 m", noteKey: "draftNote" },
    standard: { sample: "10 m", contour: "10 m", noteKey: "standardNote" },
    fine: { sample: "3 m", contour: "5 m", noteKey: "fineNote" }
  };
  const state = {
    map: null, drawn: null, boundary: null, bbox: null, theme: "auto", saving: false,
    language: "en", activity: { key: "readyForBoundary", kind: "", params: {} },
    connection: "localService", searchMessage: null, osmPreview: null,
    previewView: { yaw: -0.72, pitch: 0.48, zoom: 1, dragging: false, x: 0, y: 0 }
  };
  const el = (id) => document.getElementById(id);

  function t(key, params = {}) {
    const template = messages[state.language]?.[key] ?? messages.en[key] ?? key;
    return Object.entries(params).reduce((text, [name, value]) => text.replaceAll(`{${name}}`, String(value)), template);
  }

  function setActivity(key, kind = "", params = {}) {
    state.activity = { key, kind, params };
    const node = el("activity-message");
    node.textContent = t(key, params);
    node.className = `activity-message${kind ? ` is-${kind}` : ""}`;
  }

  function setConnection(key) {
    state.connection = key;
    el("connection-state").textContent = t(key);
  }

  function setSearchMessage(key, params = {}) {
    state.searchMessage = { key, params };
    el("search-message").textContent = t(key, params);
  }

  function toast(key, params = {}) {
    const node = el("toast");
    node.textContent = t(key, params);
    node.hidden = false;
    window.clearTimeout(toast.timer);
    toast.timer = window.setTimeout(() => { node.hidden = true; }, 3800);
  }

  function formatCoord(value) {
    return Number.isFinite(value) ? value.toFixed(5) : "-";
  }

  function boundsFromGeometry(geometry) {
    const bbox = [Infinity, Infinity, -Infinity, -Infinity];
    const visit = (value) => {
      if (!Array.isArray(value) || !value.length) return;
      if (typeof value[0] === "number") {
        bbox[0] = Math.min(bbox[0], value[0]);
        bbox[1] = Math.min(bbox[1], value[1]);
        bbox[2] = Math.max(bbox[2], value[0]);
        bbox[3] = Math.max(bbox[3], value[1]);
        return;
      }
      value.forEach(visit);
    };
    visit(geometry.coordinates);
    return bbox.every(Number.isFinite) ? bbox : null;
  }

  function normalizeBoundary(payload) {
    const source = payload.type === "FeatureCollection"
      ? payload
      : payload.type === "Feature" ? { type: "FeatureCollection", features: [payload] } : null;
    if (!source || !Array.isArray(source.features)) throw new Error("invalidBoundaryType");
    const features = source.features.filter((feature) => ["Polygon", "MultiPolygon"].includes(feature?.geometry?.type));
    if (!features.length) throw new Error("noPolygon");
    const bbox = [Infinity, Infinity, -Infinity, -Infinity];
    features.forEach((feature) => {
      const next = boundsFromGeometry(feature.geometry);
      if (!next) return;
      bbox[0] = Math.min(bbox[0], next[0]); bbox[1] = Math.min(bbox[1], next[1]);
      bbox[2] = Math.max(bbox[2], next[2]); bbox[3] = Math.max(bbox[3], next[3]);
    });
    if (!bbox.every(Number.isFinite)) throw new Error("noBoundaryCoords");
    return { type: "FeatureCollection", features, bbox };
  }

  function boundaryToLayer(featureCollection) {
    if (!state.map || !window.L) return;
    if (state.drawn) state.drawn.clearLayers();
    if (!state.drawn) state.drawn = new L.FeatureGroup().addTo(state.map);
    L.geoJSON(featureCollection, { style: { color: "#3d64d8", weight: 2, fillColor: "#3d64d8", fillOpacity: 0.12 } }).eachLayer((layer) => state.drawn.addLayer(layer));
    const bounds = state.drawn.getBounds();
    if (bounds.isValid()) state.map.fitBounds(bounds.pad(0.2));
  }

  function setBoundary(featureCollection) {
    const normalized = normalizeBoundary(featureCollection);
    state.boundary = { type: "FeatureCollection", features: normalized.features };
    state.bbox = normalized.bbox;
    state.osmPreview = null;
    updateBoundaryReadout();
    ["save-selection", "plan-osm", "plan-dem", "preview-tab", "save-model-settings"].forEach((id) => { el(id).disabled = false; });
    boundaryToLayer(state.boundary);
    drawPreview();
    setActivity("boundaryReady", "success");
  }

  function updateBoundaryReadout() {
    ["west", "south", "east", "north"].forEach((key, index) => {
      el(`bbox-${key}`).textContent = state.bbox ? formatCoord(state.bbox[index]) : "-";
    });
    if (!state.bbox) {
      el("boundary-state").textContent = t("notSelected");
      el("boundary-state").classList.remove("is-ready");
      el("area-readout").textContent = t("drawBoundaryHelp");
      return;
    }
    const width = Math.abs(state.bbox[2] - state.bbox[0]) * 111.32;
    const height = Math.abs(state.bbox[3] - state.bbox[1]) * 110.54;
    const key = state.boundary.features.length === 1 ? "featureSingle" : "featurePlural";
    el("boundary-state").textContent = t("readyToSave");
    el("boundary-state").classList.add("is-ready");
    el("area-readout").textContent = t(key, { count: state.boundary.features.length, width: width.toFixed(1), height: height.toFixed(1) });
  }

  function updatePrecisionNote() {
    const precision = document.querySelector('input[name="precision"]:checked')?.value || "standard";
    const info = precisionInfo[precision];
    el("precision-note").textContent = `${t(info.noteKey)} ${t("contours", { value: info.contour })}`;
  }

  function getSettings() {
    const precision = document.querySelector('input[name="precision"]:checked')?.value || "standard";
    return {
      osm_provider: el("osm-provider").value,
      dem_dataset: el("dem-dataset").value,
      gee_project: el("gee-project").value.trim() || null,
      precision_preset: precision,
      sample_step_m: precisionInfo[precision].sample,
      contour_interval_m: precisionInfo[precision].contour,
      model_settings: getModelSettings()
    };
  }

  function getModelSettings() {
    const colors = {};
    const visibleLayers = {};
    document.querySelectorAll("[data-layer-color]").forEach((input) => { colors[input.dataset.layerColor] = input.value; });
    document.querySelectorAll("[data-layer-visible]").forEach((input) => { visibleLayers[input.dataset.layerVisible] = input.checked; });
    return {
      default_building_height_m: clampInput("default-building-height", 10),
      floor_height_m: clampInput("floor-height", 3),
      height_scale: clampInput("height-scale", 1),
      colors,
      visible_layers: visibleLayers
    };
  }

  function clampInput(id, fallback) {
    const input = el(id);
    const minimum = Number(input.min);
    const maximum = Number(input.max);
    const parsed = Number(input.value);
    const value = Number.isFinite(parsed) ? Math.min(Math.max(parsed, minimum), maximum) : fallback;
    input.value = String(value);
    return value;
  }

  function applyModelSettings(settings = {}) {
    if (settings.default_building_height_m != null) el("default-building-height").value = settings.default_building_height_m;
    if (settings.floor_height_m != null) el("floor-height").value = settings.floor_height_m;
    if (settings.height_scale != null) el("height-scale").value = settings.height_scale;
    Object.entries(settings.colors || {}).forEach(([key, value]) => {
      const input = document.querySelector(`[data-layer-color="${key}"]`);
      if (input) input.value = value;
    });
    Object.entries(settings.visible_layers || {}).forEach(([key, value]) => {
      const input = document.querySelector(`[data-layer-visible="${key}"]`);
      if (input) input.checked = Boolean(value);
    });
    updateModelControls();
  }

  function updateModelControls() {
    el("height-scale-value").value = `${Number(el("height-scale").value).toFixed(1)}×`;
    const colors = getModelSettings().colors;
    document.querySelectorAll("[data-legend]").forEach((swatch) => {
      swatch.style.backgroundColor = colors[swatch.dataset.legend] || "#808080";
    });
    drawPreview();
  }

  function updateColorLabels() {
    document.querySelectorAll("[data-layer-color]").forEach((input) => {
      input.setAttribute("aria-label", t("layerColor", { layer: t(`layer${input.dataset.layerColor[0].toUpperCase()}${input.dataset.layerColor.slice(1)}`) }));
    });
  }

  async function postJson(path, body) {
    const response = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.message || result.error || `Request failed (${response.status})`);
    return result;
  }

  async function saveSelection(openModel = false) {
    if (!state.boundary || state.saving) return;
    state.saving = true;
    el("save-selection").disabled = true;
    setActivity("savingBoundary");
    try {
      const result = await postJson("/api/selection", { boundary: state.boundary, ...getSettings() });
      setActivity("boundarySaved", "success");
      toast("selectionToast");
      setConnection("selectionSaved");
      if (openModel) showPreview(true);
      return result;
    } catch (error) {
      setActivity("requestFailed", "error", { message: error.message });
      toast("requestFailed", { message: error.message });
      return null;
    } finally {
      state.saving = false;
      el("save-selection").disabled = false;
    }
  }

  async function saveModelSettings() {
    if (!state.boundary || state.saving) return;
    const result = await saveSelection(false);
    if (result) {
      el("model-config-status").textContent = t("modelSettingsSaved");
      el("model-config-status").className = "activity-message is-success";
      toast("modelSettingsSaved");
    }
  }

  async function plan(kind) {
    if (!state.boundary) return;
    const label = kind.toUpperCase();
    setActivity("preparingRequest", "", { kind: label });
    try {
      const saved = await saveSelection();
      if (!saved) return;
      const result = await postJson("/api/plan", { kind, ...getSettings() });
      setActivity("planReady", "success", { kind: label });
      toast("planToast", { kind: label });
    } catch (error) {
      setActivity("requestFailed", "error", { message: error.message });
    }
  }

  async function searchPlace(event) {
    event.preventDefault();
    const query = el("place-search").value.trim();
    if (!query) return;
    setSearchMessage("searching");
    try {
      const response = await fetch(`/api/geocode?q=${encodeURIComponent(query)}`);
      const result = await response.json();
      if (!response.ok || !result.results?.length) throw new Error("noPlace");
      const place = result.results[0];
      const bounds = place.boundingbox?.map(Number);
      if (bounds?.length === 4 && state.map) state.map.fitBounds([[bounds[0], bounds[2]], [bounds[1], bounds[3]]]);
      else if (state.map) state.map.setView([Number(place.lat), Number(place.lon)], 13);
      setSearchMessage(place.display_name || "placeFound");
    } catch (error) {
      setSearchMessage(messages.en[error.message] ? error.message : "requestFailed", messages.en[error.message] ? {} : { message: error.message });
    }
  }

  function parseHeight(feature, settings) {
    const direct = Number.parseFloat(feature.height);
    if (Number.isFinite(direct) && direct > 0) return { value: direct * settings.height_scale, source: "osm" };
    const levels = Number.parseFloat(feature.levels);
    if (Number.isFinite(levels) && levels > 0) return { value: levels * settings.floor_height_m * settings.height_scale, source: "osm" };
    return { value: settings.default_building_height_m * settings.height_scale, source: "default" };
  }

  function shadeColor(hex, amount) {
    const value = Number.parseInt(String(hex).replace("#", ""), 16);
    if (!Number.isFinite(value)) return "#808080";
    const channels = [value >> 16, (value >> 8) & 255, value & 255].map((channel) =>
      Math.max(0, Math.min(255, Math.round(channel + amount * 255))));
    return `rgb(${channels[0]} ${channels[1]} ${channels[2]})`;
  }

  function previewTransform(canvas) {
    const bbox = state.bbox;
    const latitude = (bbox[1] + bbox[3]) / 2;
    const kx = 111320 * Math.cos(latitude * Math.PI / 180);
    const ky = 110540;
    const centerLon = (bbox[0] + bbox[2]) / 2;
    const centerLat = (bbox[1] + bbox[3]) / 2;
    const extentX = Math.max(10, Math.abs(bbox[2] - bbox[0]) * kx);
    const extentY = Math.max(10, Math.abs(bbox[3] - bbox[1]) * ky);
    const baseScale = Math.min(canvas.width * 0.66 / extentX, canvas.height * 0.48 / extentY) * state.previewView.zoom;
    const cosYaw = Math.cos(state.previewView.yaw);
    const sinYaw = Math.sin(state.previewView.yaw);
    const cosPitch = Math.cos(state.previewView.pitch);
    const sinPitch = Math.sin(state.previewView.pitch);
    const toWorld = (coordinate) => [(coordinate[0] - centerLon) * kx, (coordinate[1] - centerLat) * ky];
    const project = (point, z = 0) => {
      const rx = point[0] * cosYaw - point[1] * sinYaw;
      const ry = point[0] * sinYaw + point[1] * cosYaw;
      const vertical = z * 3.2;
      return [
        canvas.width / 2 + rx * baseScale,
        canvas.height * 0.53 - (ry * cosPitch - vertical * sinPitch) * baseScale,
        ry * sinPitch + vertical * cosPitch
      ];
    };
    return { toWorld, project, extentX, extentY, baseScale };
  }

  function drawPolygon(context, points, fill, stroke = null, lineWidth = 1) {
    if (points.length < 3) return;
    context.beginPath();
    context.moveTo(points[0][0], points[0][1]);
    points.slice(1).forEach((point) => context.lineTo(point[0], point[1]));
    context.closePath();
    context.fillStyle = fill;
    context.fill();
    if (stroke) {
      context.strokeStyle = stroke;
      context.lineWidth = lineWidth;
      context.stroke();
    }
  }

  function drawPreview() {
    const canvas = el("preview-canvas");
    if (canvas.clientWidth > 0 && canvas.clientHeight > 0) {
      const displayWidth = Math.round(canvas.clientWidth);
      const displayHeight = Math.round(canvas.clientHeight);
      if (canvas.width !== displayWidth || canvas.height !== displayHeight) {
        canvas.width = displayWidth;
        canvas.height = displayHeight;
      }
    }
    const context = canvas.getContext("2d");
    if (!context) return;
    const width = canvas.width; const height = canvas.height;
    context.clearRect(0, 0, width, height);
    context.fillStyle = "#17202a";
    context.fillRect(0, 0, width, height);
    if (!state.bbox) {
      el("preview-empty").hidden = false;
      return;
    }
    el("preview-empty").hidden = true;
    const settings = getModelSettings();
    const transform = previewTransform(canvas);
    const halfX = transform.extentX / 2;
    const halfY = transform.extentY / 2;
    const base = [
      transform.project([-halfX, -halfY]),
      transform.project([halfX, -halfY]),
      transform.project([halfX, halfY]),
      transform.project([-halfX, halfY])
    ];
    if (settings.visible_layers.terrain) {
      drawPolygon(context, base, settings.colors.terrain, shadeColor(settings.colors.terrain, -0.16), 1.2);
    }
    if (settings.visible_layers.contours) {
      context.save();
      context.globalAlpha = 0.66;
      context.strokeStyle = settings.colors.contours;
      context.lineWidth = 1;
      for (let index = 1; index < 10; index += 1) {
        const ratio = index / 10;
        const x = -halfX + transform.extentX * ratio;
        const y = -halfY + transform.extentY * ratio;
        const vertical = [transform.project([x, -halfY]), transform.project([x, halfY])];
        const horizontal = [transform.project([-halfX, y]), transform.project([halfX, y])];
        [vertical, horizontal].forEach((line) => {
          context.beginPath(); context.moveTo(line[0][0], line[0][1]); context.lineTo(line[1][0], line[1][1]); context.stroke();
        });
      }
      context.restore();
    }

    const preview = state.osmPreview;
    const primitives = [];
    const stats = { buildings: 0, roads: 0, water: 0, landuse: 0, real: 0, defaults: 0 };
    if (preview?.features) {
      preview.features.forEach((feature) => {
        const world = feature.coordinates.map(transform.toWorld);
        if (feature.kind === "buildings" && settings.visible_layers.buildings && world.length >= 4) {
          const height = parseHeight(feature, settings);
          height.source === "osm" ? stats.real += 1 : stats.defaults += 1;
          stats.buildings += 1;
          const lower = world.slice(0, -1);
          const roof = lower.map((point) => transform.project(point, height.value));
          const ground = lower.map((point) => transform.project(point, 0.12));
          const depth = roof.reduce((sum, point) => sum + point[2], 0) / roof.length;
          primitives.push({ type: "building", roof, ground, depth, color: settings.colors.buildings });
        } else if (feature.kind === "roads" && settings.visible_layers.roads && world.length >= 2) {
          stats.roads += 1;
          const points = world.map((point) => transform.project(point, 0.24));
          const widthMeters = Number.parseFloat(feature.width) || 5;
          primitives.push({
            type: "line", points, depth: points.reduce((sum, point) => sum + point[2], 0) / points.length,
            color: settings.colors.roads, width: Math.max(1.5, Math.min(14, widthMeters * transform.baseScale))
          });
        } else if ((feature.kind === "water" || feature.kind === "landuse") && settings.visible_layers[feature.kind] && world.length >= 4) {
          stats[feature.kind] += 1;
          const points = world.slice(0, -1).map((point) => transform.project(point, feature.kind === "water" ? 0.16 : 0.08));
          primitives.push({
            type: "surface", points, depth: points.reduce((sum, point) => sum + point[2], 0) / points.length,
            color: settings.colors[feature.kind]
          });
        }
      });
    }
    primitives.sort((first, second) => second.depth - first.depth);
    primitives.forEach((primitive) => {
      if (primitive.type === "surface") {
        drawPolygon(context, primitive.points, primitive.color, shadeColor(primitive.color, -0.14), 0.8);
      } else if (primitive.type === "line") {
        context.beginPath();
        context.moveTo(primitive.points[0][0], primitive.points[0][1]);
        primitive.points.slice(1).forEach((point) => context.lineTo(point[0], point[1]));
        context.strokeStyle = primitive.color;
        context.lineWidth = primitive.width;
        context.lineJoin = "round";
        context.lineCap = "round";
        context.stroke();
      } else if (primitive.type === "building") {
        for (let index = 0; index < primitive.roof.length; index += 1) {
          const next = (index + 1) % primitive.roof.length;
          drawPolygon(context, [
            primitive.ground[index], primitive.ground[next], primitive.roof[next], primitive.roof[index]
          ], shadeColor(primitive.color, index % 2 ? -0.12 : -0.2), null);
        }
        drawPolygon(context, primitive.roof, primitive.color, shadeColor(primitive.color, 0.12), 0.8);
      }
    });

    ["buildings", "roads", "water", "landuse"].forEach((key) => {
      el(`stat-${key}`).textContent = stats[key].toLocaleString();
    });
    el("stat-real-heights").textContent = stats.real.toLocaleString();
    el("stat-default-heights").textContent = stats.defaults.toLocaleString();
    el("preview-summary").textContent = t("previewSummary", stats);
    context.fillStyle = "#dce5ef";
    context.font = "600 18px Segoe UI, sans-serif";
    context.fillText(preview ? t("osmPreviewReady") : t("extentOnly"), 32, 40);
    context.fillStyle = "#9eafc2";
    context.font = "13px Segoe UI, sans-serif";
    context.fillText(preview ? t("planarPreview") : t("demNotLoaded"), 32, 64);
  }

  async function loadOsmPreview() {
    if (!state.boundary) return;
    if (el("osm-provider").value !== "overpass") {
      toast("previewRequiresOverpass");
      return;
    }
    el("preview-loading").hidden = false;
    el("load-osm-preview").disabled = true;
    try {
      const result = await postJson("/api/osm-preview", {
        boundary: state.boundary,
        model_settings: getModelSettings()
      });
      state.osmPreview = result;
      el("preview-source-state").textContent = t("osmPreviewReady");
      el("preview-truncated").hidden = !result.truncated;
      drawPreview();
    } catch (error) {
      toast("previewFailed", { message: error.message });
      el("model-config-status").textContent = t("previewFailed", { message: error.message });
      el("model-config-status").className = "activity-message is-error";
    } finally {
      el("preview-loading").hidden = true;
      el("load-osm-preview").disabled = false;
    }
  }

  function resetPreviewView() {
    state.previewView = { yaw: -0.72, pitch: 0.48, zoom: 1, dragging: false, x: 0, y: 0 };
    drawPreview();
  }

  function applyLeafletLocale() {
    if (!window.L) return;
    const local = L.drawLocal;
    if (local?.draw?.toolbar?.buttons) Object.assign(local.draw.toolbar.buttons, {
      polygon: t("drawPolygon"), rectangle: t("drawRectangle")
    });
    if (local?.draw?.toolbar?.actions) Object.assign(local.draw.toolbar.actions, {
      title: t("drawCancel"), text: t("drawCancel")
    });
    if (local?.draw?.handlers?.polygon?.tooltip) Object.assign(local.draw.handlers.polygon.tooltip, {
      start: t("drawStartPolygon"), cont: t("drawContinue"), end: t("drawFinish")
    });
    if (local?.draw?.handlers?.rectangle?.tooltip) local.draw.handlers.rectangle.tooltip.start = t("drawStartRectangle");
    if (local?.edit?.toolbar?.actions) Object.assign(local.edit.toolbar.actions, {
      save: { title: t("editSave"), text: t("editSave") },
      cancel: { title: t("editCancel"), text: t("editCancel") },
      clearAll: { title: t("editClearAll"), text: t("editClearAll") }
    });
    if (local?.edit?.toolbar?.buttons) Object.assign(local.edit.toolbar.buttons, {
      edit: t("editEdit"), editDisabled: t("editDisabled"), remove: t("editRemove"), removeDisabled: t("removeDisabled")
    });
    if (local?.edit?.handlers?.edit?.tooltip) Object.assign(local.edit.handlers.edit.tooltip, { text: t("editTooltip") });
    if (local?.edit?.handlers?.remove?.tooltip) local.edit.handlers.remove.tooltip.text = t("removeTooltip");
    const labels = [
      [".leaflet-draw-draw-polygon", "drawPolygon"], [".leaflet-draw-draw-rectangle", "drawRectangle"],
      [".leaflet-draw-edit-edit", "editLayers"], [".leaflet-draw-edit-remove", "deleteLayers"],
      [".leaflet-control-zoom-in", "zoomIn"], [".leaflet-control-zoom-out", "zoomOut"]
    ];
    labels.forEach(([selector, key]) => document.querySelectorAll(selector).forEach((node) => {
      node.title = t(key); node.setAttribute("aria-label", t(key));
      const screenReaderText = node.querySelector(".sr-only");
      if (screenReaderText) screenReaderText.textContent = t(key);
    }));
  }

  function updateThemeToggle() {
    const hasDarkTheme = document.documentElement.dataset.theme === "dark" ||
      (!document.documentElement.dataset.theme && window.matchMedia?.("(prefers-color-scheme: dark)").matches);
    el("theme-toggle").textContent = t(hasDarkTheme ? "lightMode" : "darkMode");
    el("theme-toggle").setAttribute("aria-pressed", String(hasDarkTheme));
  }

  function preferredLanguage() {
    try {
      const stored = window.localStorage.getItem("rhino-site-language");
      if (stored === "en" || stored === "zh") return stored;
    } catch (_) { /* local preference is optional */ }
    return navigator.language?.toLowerCase().startsWith("zh") ? "zh" : "en";
  }

  function applyLanguage(language) {
    state.language = language === "zh" ? "zh" : "en";
    document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
    document.title = t("documentTitle");
    document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = t(node.dataset.i18n); });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => { node.placeholder = t(node.dataset.i18nPlaceholder); });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((node) => { node.setAttribute("aria-label", t(node.dataset.i18nAriaLabel)); });
    document.querySelectorAll("[data-language]").forEach((node) => {
      const selected = node.dataset.language === state.language;
      const label = node.dataset.language === "zh" ? t("languageChinese") : t("languageEnglish");
      node.classList.toggle("is-active", selected);
      node.setAttribute("aria-pressed", String(selected));
      node.setAttribute("aria-label", label);
      node.title = label;
    });
    setConnection(state.connection);
    setActivity(state.activity.key, state.activity.kind, state.activity.params);
    if (state.searchMessage) setSearchMessage(state.searchMessage.key, state.searchMessage.params);
    updateBoundaryReadout();
    updatePrecisionNote();
    updateThemeToggle();
    updateColorLabels();
    applyLeafletLocale();
    drawPreview();
    try { window.localStorage.setItem("rhino-site-language", state.language); } catch (_) { /* optional */ }
  }

  function toggleTheme() {
    const hasDarkTheme = document.documentElement.dataset.theme === "dark" ||
      (!document.documentElement.dataset.theme && window.matchMedia?.("(prefers-color-scheme: dark)").matches);
    document.documentElement.dataset.theme = hasDarkTheme ? "light" : "dark";
    updateThemeToggle();
  }

  function showPreview(show) {
    if (show && !state.boundary) return;
    const workbench = document.querySelector(".workbench");
    const panel = el("preview-panel");
    workbench.hidden = show;
    panel.hidden = !show;
    el("map-tab").classList.toggle("is-active", !show);
    el("preview-tab").classList.toggle("is-active", show);
    el("map-tab").setAttribute("aria-pressed", String(!show));
    el("preview-tab").setAttribute("aria-pressed", String(show));
    if (show) {
      drawPreview();
      el("load-osm-preview").focus();
    } else {
      el("map-tab").focus();
    }
  }

  async function loadExisting() {
    try {
      const response = await fetch("/api/status");
        const result = await response.json();
      if (result.selection?.boundary) setBoundary(result.selection.boundary);
      if (result.selection) {
        if (result.selection.osm_provider) el("osm-provider").value = result.selection.osm_provider;
        if (result.selection.dem_dataset) el("dem-dataset").value = result.selection.dem_dataset;
        if (result.selection.gee_project) el("gee-project").value = result.selection.gee_project;
        if (result.selection.precision_preset) {
          const radio = document.querySelector(`input[name="precision"][value="${result.selection.precision_preset}"]`);
          if (radio) radio.checked = true;
        }
        if (result.selection.model_settings) applyModelSettings(result.selection.model_settings);
        drawPreview();
      }
    } catch (_) {
      setConnection("offlineMode");
      setActivity("offlineActivity", "error");
    }
  }

  function initMap() {
    if (!window.L) { el("map-fallback").hidden = false; return; }
    applyLeafletLocale();
    state.map = L.map("map", { zoomControl: false, attributionControl: false }).setView([20, 0], 2);
    L.control.zoom({ position: "bottomright" }).addTo(state.map);
    state.map.createPane("worldPane");
    state.map.getPane("worldPane").style.zIndex = "180";
    state.map.getPane("worldPane").style.pointerEvents = "none";
    fetch("/vendor/countries-110m.json")
      .then((response) => response.json())
      .then((topology) => {
        if (!window.topojson) return;
        const world = window.topojson.feature(topology, topology.objects.countries);
        L.geoJSON(world, {
          pane: "worldPane",
          interactive: false,
          style: { color: "#8794a5", weight: 0.65, fillColor: "#c9d3df", fillOpacity: 0.32 }
        }).addTo(state.map);
      })
      .catch(() => setActivity("offlineWorld", "error"));
    const tiles = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19 }).addTo(state.map);
    let tileErrors = 0;
    let tileLoads = 0;
    tiles.on("tileerror", () => {
      tileErrors += 1;
      if (tileErrors === 3 && tileLoads === 0) {
        el("tile-state").hidden = false;
        setActivity("tilesUnavailableActivity", "error");
      }
    });
    tiles.on("tileload", () => { tileLoads += 1; el("tile-state").hidden = true; });
    state.drawn = new L.FeatureGroup().addTo(state.map);
    state.map.addControl(new L.Control.Draw({ position: "bottomleft", edit: { featureGroup: state.drawn }, draw: { polyline: false, circle: false, circlemarker: false, marker: false } }));
    state.map.on(L.Draw.Event.CREATED, (event) => setBoundary(event.layer.toGeoJSON()));
    state.map.on(L.Draw.Event.EDITED, (event) => { event.layers.eachLayer((layer) => setBoundary(layer.toGeoJSON())); });
    state.map.on(L.Draw.Event.DELETED, () => {
      state.boundary = null; state.bbox = null; state.osmPreview = null;
      ["save-selection", "plan-osm", "plan-dem", "preview-tab", "save-model-settings"].forEach((id) => { el(id).disabled = true; });
      updateBoundaryReadout(); drawPreview(); setActivity("boundaryCleared");
    });
    applyLeafletLocale();
  }

  function bind() {
    el("search-form").addEventListener("submit", searchPlace);
    el("save-selection").addEventListener("click", () => saveSelection(true));
    el("plan-osm").addEventListener("click", () => plan("osm"));
    el("plan-dem").addEventListener("click", () => plan("dem"));
    el("preview-tab").addEventListener("click", () => showPreview(true));
    el("map-tab").addEventListener("click", () => showPreview(false));
    el("close-preview").addEventListener("click", () => showPreview(false));
    el("load-osm-preview").addEventListener("click", loadOsmPreview);
    el("reset-preview-view").addEventListener("click", resetPreviewView);
    el("save-model-settings").addEventListener("click", saveModelSettings);
    el("load-boundary-button").addEventListener("click", () => el("boundary-file").click());
    el("boundary-file").addEventListener("change", async (event) => {
      const file = event.target.files?.[0]; if (!file) return;
      try { setBoundary(JSON.parse(await file.text())); toast("geojsonLoaded"); }
      catch (error) { setActivity(messages.en[error.message] ? error.message : "requestFailed", "error", messages.en[error.message] ? {} : { message: error.message }); }
      event.target.value = "";
    });
    el("locate-button").addEventListener("click", () => {
      if (!state.map || !navigator.geolocation) { toast("locationUnavailable"); return; }
      navigator.geolocation.getCurrentPosition((position) => state.map.setView([position.coords.latitude, position.coords.longitude], 13), () => toast("locationDenied"));
    });
    document.querySelectorAll('input[name="precision"]').forEach((radio) => radio.addEventListener("change", () => { updatePrecisionNote(); drawPreview(); }));
    ["default-building-height", "floor-height", "height-scale"].forEach((id) => {
      el(id).addEventListener("input", updateModelControls);
    });
    document.querySelectorAll("[data-layer-visible], [data-layer-color]").forEach((input) => {
      input.addEventListener("input", updateModelControls);
      input.addEventListener("change", updateModelControls);
    });
    const canvas = el("preview-canvas");
    canvas.addEventListener("pointerdown", (event) => {
      state.previewView.dragging = true;
      state.previewView.x = event.clientX;
      state.previewView.y = event.clientY;
      canvas.setPointerCapture(event.pointerId);
    });
    canvas.addEventListener("pointermove", (event) => {
      if (!state.previewView.dragging) return;
      state.previewView.yaw += (event.clientX - state.previewView.x) * 0.008;
      state.previewView.pitch = Math.max(0.18, Math.min(1.05, state.previewView.pitch - (event.clientY - state.previewView.y) * 0.005));
      state.previewView.x = event.clientX;
      state.previewView.y = event.clientY;
      drawPreview();
    });
    const stopDrag = () => { state.previewView.dragging = false; };
    canvas.addEventListener("pointerup", stopDrag);
    canvas.addEventListener("pointercancel", stopDrag);
    canvas.addEventListener("wheel", (event) => {
      event.preventDefault();
      state.previewView.zoom = Math.max(0.55, Math.min(2.4, state.previewView.zoom * (event.deltaY > 0 ? 0.9 : 1.1)));
      drawPreview();
    }, { passive: false });
    canvas.addEventListener("keydown", (event) => {
      const actions = {
        ArrowLeft: () => { state.previewView.yaw -= 0.12; },
        ArrowRight: () => { state.previewView.yaw += 0.12; },
        ArrowUp: () => { state.previewView.pitch = Math.min(1.05, state.previewView.pitch + 0.08); },
        ArrowDown: () => { state.previewView.pitch = Math.max(0.18, state.previewView.pitch - 0.08); },
        "+": () => { state.previewView.zoom = Math.min(2.4, state.previewView.zoom * 1.1); },
        "=": () => { state.previewView.zoom = Math.min(2.4, state.previewView.zoom * 1.1); },
        "-": () => { state.previewView.zoom = Math.max(0.55, state.previewView.zoom * 0.9); }
      };
      if (!actions[event.key]) return;
      event.preventDefault(); actions[event.key](); drawPreview();
    });
    window.addEventListener("resize", drawPreview);
    document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => applyLanguage(button.dataset.language)));
    el("theme-toggle").addEventListener("click", toggleTheme);
  }

  el("preview-tab").disabled = true;
  el("save-model-settings").disabled = true;
  bind(); updateModelControls(); applyLanguage(preferredLanguage()); initMap(); loadExisting();
})();
